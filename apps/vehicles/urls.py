# apps/vehicles/urls.py
from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    path('', views.VehicleListView.as_view(), name='list'),
    path('<int:pk>/', views.VehicleDetailView.as_view(), name='detail'),
    path('novo/', views.VehicleCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.VehicleUpdateView.as_view(), name='update'),
    path('<int:pk>/excluir/', views.VehicleDeleteView.as_view(), name='delete'),
]