# apps/vehicles/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import OperatorRequiredMixin, ManagerRequiredMixin, ProtectedDeleteMixin, TenantFormMixin, TenantQuerySetMixin
from .models import Vehicle, VehicleChecklist, VehicleDocument
from .forms import VehicleChecklistForm, VehicleDocumentForm, VehicleForm


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


class VehicleDocumentListView(TenantQuerySetMixin, LoginRequiredMixin, ListView):
    model = VehicleDocument
    template_name = 'vehicles/document_list.html'
    context_object_name = 'documents'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().select_related('vehicle', 'driver', 'driver__user')


class VehicleDocumentDetailView(TenantQuerySetMixin, LoginRequiredMixin, DetailView):
    model = VehicleDocument
    template_name = 'vehicles/document_detail.html'
    context_object_name = 'document'


class VehicleDocumentCreateView(TenantFormMixin, OperatorRequiredMixin, CreateView):
    model = VehicleDocument
    form_class = VehicleDocumentForm
    template_name = 'vehicles/document_form.html'
    success_url = reverse_lazy('vehicles:documents')


class VehicleDocumentUpdateView(TenantFormMixin, TenantQuerySetMixin, OperatorRequiredMixin, UpdateView):
    model = VehicleDocument
    form_class = VehicleDocumentForm
    template_name = 'vehicles/document_form.html'
    success_url = reverse_lazy('vehicles:documents')


class VehicleDocumentDeleteView(TenantQuerySetMixin, ManagerRequiredMixin, DeleteView):
    model = VehicleDocument
    template_name = 'vehicles/document_confirm_delete.html'
    success_url = reverse_lazy('vehicles:documents')


class VehicleChecklistListView(TenantQuerySetMixin, LoginRequiredMixin, ListView):
    model = VehicleChecklist
    template_name = 'vehicles/checklist_list.html'
    context_object_name = 'checklists'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().select_related('vehicle', 'driver', 'driver__user')


class VehicleChecklistDetailView(TenantQuerySetMixin, LoginRequiredMixin, DetailView):
    model = VehicleChecklist
    template_name = 'vehicles/checklist_detail.html'
    context_object_name = 'checklist'


class VehicleChecklistCreateView(TenantFormMixin, OperatorRequiredMixin, CreateView):
    model = VehicleChecklist
    form_class = VehicleChecklistForm
    template_name = 'vehicles/checklist_form.html'
    success_url = reverse_lazy('vehicles:checklists')


class VehicleChecklistUpdateView(TenantFormMixin, TenantQuerySetMixin, OperatorRequiredMixin, UpdateView):
    model = VehicleChecklist
    form_class = VehicleChecklistForm
    template_name = 'vehicles/checklist_form.html'
    success_url = reverse_lazy('vehicles:checklists')


class VehicleChecklistDeleteView(TenantQuerySetMixin, ManagerRequiredMixin, DeleteView):
    model = VehicleChecklist
    template_name = 'vehicles/checklist_confirm_delete.html'
    success_url = reverse_lazy('vehicles:checklists')
