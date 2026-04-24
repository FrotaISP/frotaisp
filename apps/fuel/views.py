# apps/fuel/views.py
from django.urls import reverse_lazy
from django.db.models import Sum
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import FuelRegisterMixin, ManagerRequiredMixin, TenantFormMixin, TenantQuerySetMixin
from .models import FuelRecord
from .forms import FuelRecordForm


class FuelRecordListView(TenantQuerySetMixin, LoginRequiredMixin, ListView):
    model = FuelRecord
    template_name = 'fuel/fuelrecord_list.html'
    context_object_name = 'fuel_records'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().select_related('vehicle')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        records = self.get_queryset()
        context.update({
            'records_total': records.count(),
            'records_with_receipt': records.exclude(receipt='').count(),
            'records_with_photo': records.exclude(photo='').count(),
            'records_total_cost': records.aggregate(total=Sum('total_cost'))['total'] or 0,
        })
        return context


class FuelRecordDetailView(TenantQuerySetMixin, LoginRequiredMixin, DetailView):
    model = FuelRecord
    template_name = 'fuel/fuelrecord_detail.html'
    context_object_name = 'record'

    def get_queryset(self):
        return super().get_queryset().select_related('vehicle')


class FuelRecordCreateView(TenantFormMixin, FuelRegisterMixin, CreateView):
    model = FuelRecord
    form_class = FuelRecordForm
    template_name = 'fuel/fuelrecord_form.html'
    success_url = reverse_lazy('fuel:list')


class FuelRecordUpdateView(TenantFormMixin, TenantQuerySetMixin, FuelRegisterMixin, UpdateView):
    model = FuelRecord
    form_class = FuelRecordForm
    template_name = 'fuel/fuelrecord_form.html'
    success_url = reverse_lazy('fuel:list')


class FuelRecordDeleteView(TenantQuerySetMixin, ManagerRequiredMixin, DeleteView):
    model = FuelRecord
    template_name = 'fuel/fuelrecord_confirm_delete.html'
    success_url = reverse_lazy('fuel:list')
