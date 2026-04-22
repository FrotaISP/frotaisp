# apps/maintenance/urls.py
from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.MaintenanceListView.as_view(), name='list'),
    path('nova/', views.MaintenanceCreateView.as_view(), name='create'),
    path('preventivas/', views.PreventiveMaintenancePlanListView.as_view(), name='plans'),
    path('preventivas/novo/', views.PreventiveMaintenancePlanCreateView.as_view(), name='plan_create'),
    path('preventivas/<int:pk>/', views.PreventiveMaintenancePlanDetailView.as_view(), name='plan_detail'),
    path('preventivas/<int:pk>/editar/', views.PreventiveMaintenancePlanUpdateView.as_view(), name='plan_update'),
    path('preventivas/<int:pk>/excluir/', views.PreventiveMaintenancePlanDeleteView.as_view(), name='plan_delete'),
    path('<int:pk>/', views.MaintenanceDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.MaintenanceUpdateView.as_view(), name='update'),
    path('<int:pk>/excluir/', views.MaintenanceDeleteView.as_view(), name='delete'),
]
