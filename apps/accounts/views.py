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

from apps.core.mixins import AdminRequiredMixin
from .forms import (
    CustomAuthenticationForm, CustomUserCreationForm,
    UserEditForm, AdminPasswordResetForm, ProfileForm, UserSettingsForm,
)
from .models import UserProfile, Notificacao


# ── Auth ──────────────────────────────────────────────────────────────────────
class CustomLoginView(LoginView):
    template_name            = 'accounts/login.html'
    authentication_form      = CustomAuthenticationForm
    redirect_authenticated_user = True
    next_page                = reverse_lazy('dashboard:index')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')


class RegisterView(CreateView):
    model         = User
    form_class    = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url   = reverse_lazy('dashboard:index')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields.pop('role', None)
        return form

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        profile, _ = UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'role': 'viewer',
                'phone': form.cleaned_data.get('phone', ''),
            },
        )
        login(self.request, user)
        messages.success(self.request, f'Bem-vindo, {user.first_name or user.username}!')
        return redirect(self.success_url)


# ── Meu Perfil ────────────────────────────────────────────────────────────────
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
            profile_form  = ProfileForm(instance=request.user, user=request.user)
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                update_session_auth_hash(request, password_form.save())
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('accounts:my_profile')

        else:
            profile_form  = ProfileForm(instance=request.user, user=request.user)
            password_form = PasswordChangeForm(user=request.user)

        return render(request, self.template_name, {
            'profile_form': profile_form,
            'password_form': password_form,
        })


# ── Configurações ─────────────────────────────────────────────────────────────
class SystemSettingsView(LoginRequiredMixin, View):
    template_name = 'accounts/settings.html'

    def _get_profile(self, request):
        from apps.core.mixins import get_user_profile
        return get_user_profile(request.user)

    def get(self, request):
        profile = self._get_profile(request)
        return render(request, self.template_name, {
            'form':         UserSettingsForm(instance=profile),
            'user_profile': profile,
        })

    def post(self, request):
        profile = self._get_profile(request)
        form    = UserSettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas.')
            return redirect('accounts:settings')
        return render(request, self.template_name, {'form': form, 'user_profile': profile})


# ── Notificações ──────────────────────────────────────────────────────────────
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


# ── Gestão de usuários (Admin) ────────────────────────────────────────────────
class UserListView(AdminRequiredMixin, ListView):
    model              = User
    template_name      = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by        = 20

    def get_queryset(self):
        return User.objects.select_related('profile').order_by('username')


class UserCreateView(AdminRequiredMixin, CreateView):
    model         = User
    form_class    = CustomUserCreationForm
    template_name = 'accounts/user_form.html'
    success_url   = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        r = super().form_valid(form)
        messages.success(self.request, f'Usuário "{self.object.username}" criado.')
        return r

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), 'title': 'Novo Usuário'}


class UserEditView(AdminRequiredMixin, View):
    template_name = 'accounts/user_form.html'

    def get(self, request, pk):
        u = get_object_or_404(User, pk=pk)
        return render(request, self.template_name, {
            'form': UserEditForm(instance=u), 'title': f'Editar — {u.username}', 'editing': True
        })

    def post(self, request, pk):
        u    = get_object_or_404(User, pk=pk)
        form = UserEditForm(request.POST, instance=u)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuário "{u.username}" atualizado.')
            return redirect('accounts:user_list')
        return render(request, self.template_name, {
            'form': form, 'title': f'Editar — {u.username}', 'editing': True
        })


class UserDeleteView(AdminRequiredMixin, View):
    template_name = 'accounts/user_confirm_delete.html'

    def get(self, request, pk):
        u = get_object_or_404(User, pk=pk)
        if u == request.user:
            messages.error(request, 'Não pode excluir sua própria conta.')
            return redirect('accounts:user_list')
        return render(request, self.template_name, {'target_user': u})

    def post(self, request, pk):
        u = get_object_or_404(User, pk=pk)
        if u == request.user:
            messages.error(request, 'Não pode excluir sua própria conta.')
            return redirect('accounts:user_list')
        name = u.username
        u.delete()
        messages.success(request, f'Usuário "{name}" excluído.')
        return redirect('accounts:user_list')


class UserPasswordResetView(AdminRequiredMixin, View):
    template_name = 'accounts/user_password_reset.html'

    def get(self, request, pk):
        return render(request, self.template_name, {
            'form': AdminPasswordResetForm(), 'target_user': get_object_or_404(User, pk=pk)
        })

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        form   = AdminPasswordResetForm(request.POST)
        if form.is_valid():
            target.set_password(form.cleaned_data['new_password'])
            target.save()
            messages.success(request, f'Senha de "{target.username}" redefinida.')
            return redirect('accounts:user_list')
        return render(request, self.template_name, {'form': form, 'target_user': target})


class UserToggleActiveView(AdminRequiredMixin, View):
    def post(self, request, pk):
        u = get_object_or_404(User, pk=pk)
        if u == request.user:
            messages.error(request, 'Não pode desativar sua própria conta.')
        else:
            u.is_active = not u.is_active
            u.save()
            estado = 'ativado' if u.is_active else 'desativado'
            messages.success(request, f'Usuário "{u.username}" {estado}.')
        return redirect('accounts:user_list')
