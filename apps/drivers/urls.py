# apps/drivers/urls.py
from django.urls import path
from . import views

app_name = 'drivers'

urlpatterns = [
    path('', views.DriverListView.as_view(), name='list'),
    path('<int:pk>/', views.DriverDetailView.as_view(), name='detail'),
    path('novo/', views.DriverCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.DriverUpdateView.as_view(), name='update'),
    path('<int:pk>/excluir/', views.DriverDeleteView.as_view(), name='delete'),
]