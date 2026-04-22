# apps/accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils.text import slugify

from apps.core.mixins import AdminRequiredMixin, get_user_company
from .forms import (
    CompanyBillingForm, CustomAuthenticationForm, CustomUserCreationForm,
    UserEditForm, AdminPasswordResetForm, ProfileForm, UserSettingsForm,
)
from .models import Company, UserProfile, Notificacao


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True
    next_page = reverse_lazy('dashboard:index')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('dashboard:index')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields.pop('role', None)
        return form

    def _create_company_for_user(self, user, form):
        submitted_name = form.cleaned_data.get('company_name', '').strip()
        base_name = submitted_name or f'{user.first_name} {user.last_name}'.strip() or user.username
        name = submitted_name or f'{base_name} - Empresa'
        base_slug = slugify(name) or f'empresa-{user.pk}'
        slug = base_slug
        suffix = 1
        while Company.objects.filter(slug=slug).exists():
            suffix += 1
            slug = f'{base_slug}-{suffix}'
        return Company.objects.create(
            name=name,
            slug=slug,
            billing_email=user.email,
            subscription_status='trial',
            plan='starter',
            max_users=3,
            max_vehicles=10,
        )

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        company = self._create_company_for_user(user, form)
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'company': company,
                'role': 'admin',
                'phone': form.cleaned_data.get('phone', ''),
            },
        )
        login(self.request, user)
        messages.success(self.request, f'Bem-vindo, {user.first_name or user.username}! Seu teste gratis foi ativado.')
        return redirect(self.success_url)


class MyProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/my_profile.html'

    def get(self, request):
        return render(request, self.template_name, {
            'profile_form': ProfileForm(instance=request.user, user=request.user),
            'password_form': PasswordChangeForm(user=request.user),
        })

    def post(self, request):
        action = request.POST.get('action')

        if action == 'update_profile':
            profile_form = ProfileForm(request.POST, request.FILES, instance=request.user, user=request.user)
            password_form = PasswordChangeForm(user=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('accounts:my_profile')

        elif action == 'change_password':
            profile_form = ProfileForm(instance=request.user, user=request.user)
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                update_session_auth_hash(request, password_form.save())
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('accounts:my_profile')

        else:
            profile_form = ProfileForm(instance=request.user, user=request.user)
            password_form = PasswordChangeForm(user=request.user)

        return render(request, self.template_name, {
            'profile_form': profile_form,
            'password_form': password_form,
        })


class SystemSettingsView(LoginRequiredMixin, View):
    template_name = 'accounts/settings.html'

    def _get_profile(self, request):
        from apps.core.mixins import get_user_profile
        return get_user_profile(request.user)

    def get(self, request):
        profile = self._get_profile(request)
        return render(request, self.template_name, {
            'form': UserSettingsForm(instance=profile),
            'user_profile': profile,
        })

    def post(self, request):
        profile = self._get_profile(request)
        form = UserSettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuracoes salvas.')
            return redirect('accounts:settings')
        return render(request, self.template_name, {'form': form, 'user_profile': profile})


class SubscriptionView(LoginRequiredMixin, View):
    template_name = 'accounts/subscription.html'

    def get_company(self):
        return get_user_company(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        company = self.get_company()
        profile = getattr(request.user, 'profile', None)
        if not request.user.is_superuser and profile and not profile.can_manage_users():
            messages.error(request, 'Apenas administradores podem alterar dados da assinatura.')
            return redirect('dashboard:index')
        if not company:
            messages.error(request, 'Empresa nao encontrada para este usuario.')
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)

    def get_context(self, form=None):
        company = self.get_company()
        users_count = company.users_count()
        vehicles_count = company.vehicles_count()
        return {
            'company': company,
            'form': form or CompanyBillingForm(instance=company),
            'users_count': users_count,
            'vehicles_count': vehicles_count,
            'users_percent': company.usage_percent(users_count, company.max_users),
            'vehicles_percent': company.usage_percent(vehicles_count, company.max_vehicles),
        }

    def get(self, request):
        return render(request, self.template_name, self.get_context())

    def post(self, request):
        company = self.get_company()
        form = CompanyBillingForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados da empresa atualizados.')
            return redirect('accounts:subscription')
        return render(request, self.template_name, self.get_context(form=form))


class NotificacoesView(LoginRequiredMixin, View):
    template_name = 'accounts/notificacoes.html'

    def get(self, request):
        notifs = Notificacao.objects.filter(usuario=request.user)
        return render(request, self.template_name, {'notificacoes': notifs})


class MarcarNotificacaoLidaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notif = get_object_or_404(Notificacao, pk=pk, usuario=request.user)
        notif.lida = True
        notif.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        return redirect('accounts:notificacoes')


class MarcarTodasLidasView(LoginRequiredMixin, View):
    def post(self, request):
        Notificacao.objects.filter(usuario=request.user, lida=False).update(lida=True)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        return redirect('accounts:notificacoes')


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.select_related('profile', 'profile__company').order_by('username')
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(profile__company=get_user_company(self.request.user))


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def dispatch(self, request, *args, **kwargs):
        company = get_user_company(request.user)
        if company and not company.can_add_user():
            messages.error(request, 'Limite de usuarios do plano atingido. Atualize o plano para adicionar novos usuarios.')
            return redirect('accounts:subscription')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = get_user_company(self.request.user)
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Usuario "{self.object.username}" criado.')
        return response

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), 'title': 'Novo Usuario'}


class UserEditView(AdminRequiredMixin, View):
    template_name = 'accounts/user_form.html'

    def get_queryset(self, request):
        queryset = User.objects.select_related('profile', 'profile__company')
        if request.user.is_superuser:
            return queryset
        return queryset.filter(profile__company=get_user_company(request.user))

    def get(self, request, pk):
        u = get_object_or_404(self.get_queryset(request), pk=pk)
        return render(request, self.template_name, {
            'form': UserEditForm(instance=u, company=get_user_company(request.user)),
            'title': f'Editar - {u.username}',
            'editing': True,
        })

    def post(self, request, pk):
        u = get_object_or_404(self.get_queryset(request), pk=pk)
        form = UserEditForm(request.POST, instance=u, company=get_user_company(request.user))
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario "{u.username}" atualizado.')
            return redirect('accounts:user_list')
        return render(request, self.template_name, {
            'form': form,
            'title': f'Editar - {u.username}',
            'editing': True,
        })


class UserDeleteView(AdminRequiredMixin, View):
    template_name = 'accounts/user_confirm_delete.html'

    def get_queryset(self, request):
        queryset = User.objects.select_related('profile', 'profile__company')
        if request.user.is_superuser:
            return queryset
        return queryset.filter(profile__company=get_user_company(request.user))

    def get(self, request, pk):
        u = get_object_or_404(self.get_queryset(request), pk=pk)
        if u == request.user:
            messages.error(request, 'Nao pode excluir sua propria conta.')
            return redirect('accounts:user_list')
        return render(request, self.template_name, {'target_user': u})

    def post(self, request, pk):
        u = get_object_or_404(self.get_queryset(request), pk=pk)
        if u == request.user:
            messages.error(request, 'Nao pode excluir sua propria conta.')
            return redirect('accounts:user_list')
        name = u.username
        u.delete()
        messages.success(request, f'Usuario "{name}" excluido.')
        return redirect('accounts:user_list')


class UserPasswordResetView(AdminRequiredMixin, View):
    template_name = 'accounts/user_password_reset.html'

    def get_queryset(self, request):
        queryset = User.objects.select_related('profile', 'profile__company')
        if request.user.is_superuser:
            return queryset
        return queryset.filter(profile__company=get_user_company(request.user))

    def get(self, request, pk):
        return render(request, self.template_name, {
            'form': AdminPasswordResetForm(),
            'target_user': get_object_or_404(self.get_queryset(request), pk=pk),
        })

    def post(self, request, pk):
        target = get_object_or_404(self.get_queryset(request), pk=pk)
        form = AdminPasswordResetForm(request.POST)
        if form.is_valid():
            target.set_password(form.cleaned_data['new_password'])
            target.save()
            messages.success(request, f'Senha de "{target.username}" redefinida.')
            return redirect('accounts:user_list')
        return render(request, self.template_name, {'form': form, 'target_user': target})


class UserToggleActiveView(AdminRequiredMixin, View):
    def get_queryset(self, request):
        queryset = User.objects.select_related('profile', 'profile__company')
        if request.user.is_superuser:
            return queryset
        return queryset.filter(profile__company=get_user_company(request.user))

    def post(self, request, pk):
        u = get_object_or_404(self.get_queryset(request), pk=pk)
        if u == request.user:
            messages.error(request, 'Nao pode desativar sua propria conta.')
        else:
            u.is_active = not u.is_active
            u.save()
            estado = 'ativado' if u.is_active else 'desativado'
            messages.success(request, f'Usuario "{u.username}" {estado}.')
        return redirect('accounts:user_list')
