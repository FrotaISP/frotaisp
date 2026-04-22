# apps/maintenance/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import MaintenanceRegisterMixin, ManagerRequiredMixin, TenantFormMixin, TenantQuerySetMixin
from .models import Maintenance, PreventiveMaintenancePlan
from .forms import MaintenanceForm, PreventiveMaintenancePlanForm


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
