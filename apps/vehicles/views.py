# apps/vehicles/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import OperatorRequiredMixin, ManagerRequiredMixin, ProtectedDeleteMixin, TenantFormMixin, TenantQuerySetMixin
from .models import Vehicle
from .forms import VehicleForm


class VehicleListView(TenantQuerySetMixin, LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = 'vehicles/vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 10


class VehicleDetailView(TenantQuerySetMixin, LoginRequiredMixin, DetailView):
    model = Vehicle
    template_name = 'vehicles/vehicle_detail.html'
    context_object_name = 'vehicle'


class VehicleCreateView(TenantFormMixin, OperatorRequiredMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicles/vehicle_form.html'
    success_url = reverse_lazy('vehicles:list')


class VehicleUpdateView(TenantFormMixin, TenantQuerySetMixin, OperatorRequiredMixin, UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicles/vehicle_form.html'
    success_url = reverse_lazy('vehicles:list')


class VehicleDeleteView(TenantQuerySetMixin, ProtectedDeleteMixin, ManagerRequiredMixin, DeleteView):
    model = Vehicle
    template_name = 'vehicles/vehicle_confirm_delete.html'
    success_url = reverse_lazy('vehicles:list')
    protected_error_message = 'Este veiculo nao pode ser excluido porque possui viagens, abastecimentos ou manutencoes vinculadas.'
