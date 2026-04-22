# apps/drivers/forms.py
from django import forms
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.core.uploads import ALLOWED_IMAGE_TYPES, validate_uploaded_file
from .models import Driver


class DriverCreateForm(forms.Form):
    """Formulário que cria User + Driver em uma única tela."""

    # Dados do usuário
    first_name = forms.CharField(
        label='Nome',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Carlos'})
    )
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Silva'})
    )
    email = forms.EmailField(
        label='E-mail',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'motorista@empresa.com'})
    )
    username = forms.CharField(
        label='Login (usuário)',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: carlos.silva'})
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mínimo 6 caracteres'}),
        min_length=6
    )

    # Dados do motorista
    cnh = forms.CharField(
        label='Número da CNH',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 12345678901'})
    )
    cnh_expiration = forms.DateField(
        label='Validade da CNH',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    phone = forms.CharField(
        label='Telefone',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: (62) 9 9999-9999'})
    )
    address = forms.CharField(
        label='Endereço',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Rua, número, bairro, cidade'})
    )
    is_available = forms.BooleanField(
        label='Motorista disponível',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    avatar = forms.ImageField(
        label='Foto',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este login já está em uso. Escolha outro.')
        return username

    def clean_cnh(self):
        cnh = self.cleaned_data['cnh']
        if Driver.objects.filter(cnh=cnh).exists():
            raise forms.ValidationError('Esta CNH já está cadastrada.')
        return cnh

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        try:
            validate_uploaded_file(
                avatar,
                allowed_types=ALLOWED_IMAGE_TYPES,
                label='A foto do motorista',
            )
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
        return avatar

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email', ''),
        )
        UserProfile.objects.update_or_create(
            user=user,
            defaults={'role': 'driver'},
        )
        driver = Driver.objects.create(
            user=user,
            cnh=data['cnh'],
            cnh_expiration=data['cnh_expiration'],
            phone=data['phone'],
            address=data.get('address', ''),
            is_available=data.get('is_available', True),
            avatar=data.get('avatar') or None,
        )
        return driver


class DriverUpdateForm(forms.ModelForm):
    """Formulário de edição — também permite editar nome/email do usuário."""

    first_name = forms.CharField(
        label='Nome',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='E-mail',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Driver
        fields = ['cnh', 'cnh_expiration', 'phone', 'address', 'is_available', 'avatar']
        widgets = {
            'cnh':            forms.TextInput(attrs={'class': 'form-control'}),
            'cnh_expiration': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone':          forms.TextInput(attrs={'class': 'form-control'}),
            'address':        forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_available':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'avatar':         forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial  = self.instance.user.last_name
            self.fields['email'].initial      = self.instance.user.email

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        try:
            validate_uploaded_file(
                avatar,
                allowed_types=ALLOWED_IMAGE_TYPES,
                label='A foto do motorista',
            )
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
        return avatar

    def save(self, commit=True):
        driver = super().save(commit=False)
        driver.user.first_name = self.cleaned_data['first_name']
        driver.user.last_name  = self.cleaned_data['last_name']
        driver.user.email      = self.cleaned_data.get('email', '')
        driver.user.save()
        if commit:
            driver.save()
            UserProfile.objects.update_or_create(
                user=driver.user,
                defaults={'role': 'driver'},
            )
        return driver
