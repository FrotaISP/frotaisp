# apps/accounts/urls.py
from django.urls import path
from .views import (
    CustomLoginView, CustomLogoutView, RegisterView,
    MyProfileView, SystemSettingsView,
    UserListView, UserCreateView, UserEditView, UserDeleteView,
    UserPasswordResetView, UserToggleActiveView,
)

app_name = 'accounts'

urlpatterns = [
    path('login/',    CustomLoginView.as_view(),  name='login'),
    path('logout/',   CustomLogoutView.as_view(), name='logout'),
    path('registro/', RegisterView.as_view(),     name='register'),

    path('perfil/',        MyProfileView.as_view(),     name='my_profile'),
    path('configuracoes/', SystemSettingsView.as_view(), name='settings'),

    path('usuarios/',                    UserListView.as_view(),         name='user_list'),
    path('usuarios/novo/',               UserCreateView.as_view(),       name='user_create'),
    path('usuarios/<int:pk>/editar/',    UserEditView.as_view(),         name='user_edit'),
    path('usuarios/<int:pk>/excluir/',   UserDeleteView.as_view(),       name='user_delete'),
    path('usuarios/<int:pk>/senha/',     UserPasswordResetView.as_view(),name='user_password_reset'),
    path('usuarios/<int:pk>/ativar/',    UserToggleActiveView.as_view(), name='user_toggle_active'),
]
