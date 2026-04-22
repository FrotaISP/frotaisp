# apps/vehicles/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import OperatorRequiredMixin, ManagerRequiredMixin, ProtectedDeleteMixin, TenantFormMixin, TenantQuerySetMixin
from .models import Tire, TireEvent, Vehicle, VehicleChecklist, VehicleDocument
from .forms import TireEventForm, TireForm, VehicleChecklistForm, VehicleDocumentForm, VehicleForm


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


class TireListView(TenantQuerySetMixin, LoginRequiredMixin, ListView):
    model = Tire
    template_name = 'vehicles/tire_list.html'
    context_object_name = 'tires'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().select_related('current_vehicle')


class TireDetailView(TenantQuerySetMixin, LoginRequiredMixin, DetailView):
    model = Tire
    template_name = 'vehicles/tire_detail.html'
    context_object_name = 'tire'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = self.object.events.select_related('vehicle').all()[:20]
        return context


class TireCreateView(TenantFormMixin, OperatorRequiredMixin, CreateView):
    model = Tire
    form_class = TireForm
    template_name = 'vehicles/tire_form.html'
    success_url = reverse_lazy('vehicles:tires')


class TireUpdateView(TenantFormMixin, TenantQuerySetMixin, OperatorRequiredMixin, UpdateView):
    model = Tire
    form_class = TireForm
    template_name = 'vehicles/tire_form.html'
    success_url = reverse_lazy('vehicles:tires')


class TireDeleteView(TenantQuerySetMixin, ProtectedDeleteMixin, ManagerRequiredMixin, DeleteView):
    model = Tire
    template_name = 'vehicles/tire_confirm_delete.html'
    success_url = reverse_lazy('vehicles:tires')
    protected_error_message = 'Este pneu possui eventos no historico e nao pode ser excluido.'


class TireEventListView(TenantQuerySetMixin, LoginRequiredMixin, ListView):
    model = TireEvent
    template_name = 'vehicles/tire_event_list.html'
    context_object_name = 'events'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related('tire', 'vehicle')


class TireEventCreateView(TenantFormMixin, OperatorRequiredMixin, CreateView):
    model = TireEvent
    form_class = TireEventForm
    template_name = 'vehicles/tire_event_form.html'
    success_url = reverse_lazy('vehicles:tire_events')

    def get_initial(self):
        initial = super().get_initial()
        tire_id = self.request.GET.get('tire')
        if tire_id:
            initial['tire'] = tire_id
        return initial

    def get_success_url(self):
        if self.object and self.object.tire_id:
            return reverse_lazy('vehicles:tire_detail', kwargs={'pk': self.object.tire_id})
        return super().get_success_url()


class TireEventUpdateView(TenantFormMixin, TenantQuerySetMixin, OperatorRequiredMixin, UpdateView):
    model = TireEvent
    form_class = TireEventForm
    template_name = 'vehicles/tire_event_form.html'
    success_url = reverse_lazy('vehicles:tire_events')

    def get_success_url(self):
        if self.object and self.object.tire_id:
            return reverse_lazy('vehicles:tire_detail', kwargs={'pk': self.object.tire_id})
        return super().get_success_url()


class TireEventDeleteView(TenantQuerySetMixin, ManagerRequiredMixin, DeleteView):
    model = TireEvent
    template_name = 'vehicles/tire_event_confirm_delete.html'
    success_url = reverse_lazy('vehicles:tire_events')
