# apps/maintenance/urls.py
from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.MaintenanceListView.as_view(), name='list'),
    path('<int:pk>/', views.MaintenanceDetailView.as_view(), name='detail'),
    path('nova/', views.MaintenanceCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.MaintenanceUpdateView.as_view(), name='update'),
    path('<int:pk>/excluir/', views.MaintenanceDeleteView.as_view(), name='delete'),
]