# apps/maintenance/views.py
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import MaintenanceRegisterMixin, ManagerRequiredMixin, TenantFormMixin, TenantQuerySetMixin
from .models import Maintenance, PreventiveMaintenancePlan, VehicleExpense, WorkOrder
from .forms import MaintenanceForm, PreventiveMaintenancePlanForm, VehicleExpenseForm, WorkOrderForm


class MaintenanceListView(TenantQuerySetMixin, LoginRequiredMixin, ListView):
    model = Maintenance
    template_name = 'maintenance/maintenance_list.html'
    context_object_name = 'maintenances'
    paginate_by = 10


class MaintenanceDetailView(TenantQuerySetMixin, LoginRequiredMixin, DetailView):
    model = Maintenance
    template_name = 'maintenance/maintenance_detail.html'
    context_object_name = 'maintenance'


class MaintenanceCreateView(TenantFormMixin, MaintenanceRegisterMixin, CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'maintenance/maintenance_form.html'
    success_url = reverse_lazy('maintenance:list')


class MaintenanceUpdateView(TenantFormMixin, TenantQuerySetMixin, MaintenanceRegisterMixin, UpdateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'maintenance/maintenance_form.html'
    success_url = reverse_lazy('maintenance:list')


class MaintenanceDeleteView(TenantQuerySetMixin, ManagerRequiredMixin, DeleteView):
    model = Maintenance
    template_name = 'maintenance/maintenance_confirm_delete.html'
    success_url = reverse_lazy('maintenance:list')


class PreventiveMaintenancePlanListView(TenantQuerySetMixin, LoginRequiredMixin, ListView):
    model = PreventiveMaintenancePlan
    template_name = 'maintenance/plan_list.html'
    context_object_name = 'plans'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().select_related('vehicle')


class PreventiveMaintenancePlanDetailView(TenantQuerySetMixin, LoginRequiredMixin, DetailView):
    model = PreventiveMaintenancePlan
    template_name = 'maintenance/plan_detail.html'
    context_object_name = 'plan'


class PreventiveMaintenancePlanCreateView(TenantFormMixin, MaintenanceRegisterMixin, CreateView):
    model = PreventiveMaintenancePlan
    form_class = PreventiveMaintenancePlanForm
    template_name = 'maintenance/plan_form.html'
    success_url = reverse_lazy('maintenance:plans')


class PreventiveMaintenancePlanUpdateView(TenantFormMixin, TenantQuerySetMixin, MaintenanceRegisterMixin, UpdateView):
    model = PreventiveMaintenancePlan
    form_class = PreventiveMaintenancePlanForm
    template_name = 'maintenance/plan_form.html'
    success_url = reverse_lazy('maintenance:plans')


class PreventiveMaintenancePlanDeleteView(TenantQuerySetMixin, ManagerRequiredMixin, DeleteView):
    model = PreventiveMaintenancePlan
    template_name = 'maintenance/plan_confirm_delete.html'
    success_url = reverse_lazy('maintenance:plans')


class WorkOrderListView(TenantQuerySetMixin, LoginRequiredMixin, ListView):
    model = WorkOrder
    template_name = 'maintenance/workorder_list.html'
    context_object_name = 'orders'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().select_related('vehicle', 'driver', 'driver__user')


class WorkOrderDetailView(TenantQuerySetMixin, LoginRequiredMixin, DetailView):
    model = WorkOrder
    template_name = 'maintenance/workorder_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expenses'] = self.object.expenses.select_related('vehicle').all()
        context['expenses_total'] = context['expenses'].aggregate(total=Sum('amount'))['total'] or 0
        return context


class WorkOrderCreateView(TenantFormMixin, MaintenanceRegisterMixin, CreateView):
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = 'maintenance/workorder_form.html'
    success_url = reverse_lazy('maintenance:work_orders')


class WorkOrderUpdateView(TenantFormMixin, TenantQuerySetMixin, MaintenanceRegisterMixin, UpdateView):
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = 'maintenance/workorder_form.html'
    success_url = reverse_lazy('maintenance:work_orders')


class WorkOrderDeleteView(TenantQuerySetMixin, ManagerRequiredMixin, DeleteView):
    model = WorkOrder
    template_name = 'maintenance/workorder_confirm_delete.html'
    success_url = reverse_lazy('maintenance:work_orders')


class VehicleExpenseListView(TenantQuerySetMixin, LoginRequiredMixin, ListView):
    model = VehicleExpense
    template_name = 'maintenance/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().select_related('vehicle', 'work_order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_amount'] = self.get_queryset().aggregate(total=Sum('amount'))['total'] or 0
        return context


class VehicleExpenseDetailView(TenantQuerySetMixin, LoginRequiredMixin, DetailView):
    model = VehicleExpense
    template_name = 'maintenance/expense_detail.html'
    context_object_name = 'expense'


class VehicleExpenseCreateView(TenantFormMixin, MaintenanceRegisterMixin, CreateView):
    model = VehicleExpense
    form_class = VehicleExpenseForm
    template_name = 'maintenance/expense_form.html'
    success_url = reverse_lazy('maintenance:expenses')


class VehicleExpenseUpdateView(TenantFormMixin, TenantQuerySetMixin, MaintenanceRegisterMixin, UpdateView):
    model = VehicleExpense
    form_class = VehicleExpenseForm
    template_name = 'maintenance/expense_form.html'
    success_url = reverse_lazy('maintenance:expenses')


class VehicleExpenseDeleteView(TenantQuerySetMixin, ManagerRequiredMixin, DeleteView):
    model = VehicleExpense
    template_name = 'maintenance/expense_confirm_delete.html'
    success_url = reverse_lazy('maintenance:expenses')
