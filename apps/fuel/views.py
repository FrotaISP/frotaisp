# apps/fuel/views.py
from django.urls import reverse_lazy
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


class FuelRecordDetailView(TenantQuerySetMixin, LoginRequiredMixin, DetailView):
    model = FuelRecord
    template_name = 'fuel/fuelrecord_detail.html'
    context_object_name = 'record'


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
