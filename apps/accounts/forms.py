# apps/accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de usuário', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Senha'})
    )


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'})
    )
    first_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'})
    )
    last_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sobrenome'})
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES, label='Papel no sistema',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone'})
    )

    class Meta:
        model  = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ('username', 'password1', 'password2'):
            self.fields[f].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email      = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'role':  self.cleaned_data['role'],
                    'phone': self.cleaned_data.get('phone', ''),
                }
            )
        return user


class UserEditForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES, label='Papel',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    is_active_user = forms.BooleanField(
        required=False, label='Usuário ativo',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            try:
                p = self.instance.profile
                self.fields['role'].initial  = p.role
                self.fields['phone'].initial = p.phone
            except UserProfile.DoesNotExist:
                pass
            self.fields['is_active_user'].initial = self.instance.is_active

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = self.cleaned_data.get('is_active_user', True)
        if commit:
            user.save()
            p, _ = UserProfile.objects.get_or_create(user=user)
            p.role  = self.cleaned_data['role']
            p.phone = self.cleaned_data.get('phone', '')
            p.save()
        return user


class AdminPasswordResetForm(forms.Form):
    new_password = forms.CharField(
        label='Nova senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        label='Confirmar',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        c = super().clean()
        if c.get('new_password') != c.get('confirm_password'):
            raise forms.ValidationError('As senhas não coincidem.')
        return c


# ── Meu Perfil ────────────────────────────────────────────────────────────────
class ProfileForm(forms.ModelForm):
    """Formulário para o usuário editar seus próprios dados."""
    phone = forms.CharField(
        max_length=20, required=False, label='Telefone',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(99) 99999-9999'})
    )

    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            try:
                self.fields['phone'].initial = user.profile.phone
            except UserProfile.DoesNotExist:
                pass

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            p, _ = UserProfile.objects.get_or_create(user=user)
            p.phone = self.cleaned_data.get('phone', '')
            p.save()
        return user


# ── Configurações ─────────────────────────────────────────────────────────────
class UserSettingsForm(forms.ModelForm):
    """Configurações visíveis ao próprio usuário (somente leitura de papel)."""
    class Meta:
        model  = UserProfile
        fields = ('phone',)
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(99) 99999-9999'}),
        }
