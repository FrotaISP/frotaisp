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
    path('ordens/', views.WorkOrderListView.as_view(), name='work_orders'),
    path('ordens/nova/', views.WorkOrderCreateView.as_view(), name='work_order_create'),
    path('ordens/<int:pk>/', views.WorkOrderDetailView.as_view(), name='work_order_detail'),
    path('ordens/<int:pk>/editar/', views.WorkOrderUpdateView.as_view(), name='work_order_update'),
    path('ordens/<int:pk>/excluir/', views.WorkOrderDeleteView.as_view(), name='work_order_delete'),
    path('financeiro/', views.VehicleExpenseListView.as_view(), name='expenses'),
    path('financeiro/novo/', views.VehicleExpenseCreateView.as_view(), name='expense_create'),
    path('financeiro/<int:pk>/', views.VehicleExpenseDetailView.as_view(), name='expense_detail'),
    path('financeiro/<int:pk>/editar/', views.VehicleExpenseUpdateView.as_view(), name='expense_update'),
    path('financeiro/<int:pk>/excluir/', views.VehicleExpenseDeleteView.as_view(), name='expense_delete'),
    path('<int:pk>/', views.MaintenanceDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.MaintenanceUpdateView.as_view(), name='update'),
    path('<int:pk>/excluir/', views.MaintenanceDeleteView.as_view(), name='delete'),
]
