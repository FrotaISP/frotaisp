# apps/drivers/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from apps.core.mixins import (
    OperatorRequiredMixin,
    ManagerRequiredMixin,
    ProtectedDeleteMixin,
    TenantQuerySetMixin,
    get_user_company,
    scope_queryset_for_user,
)

from .models import Driver
from .forms import DriverCreateForm, DriverUpdateForm


class DriverListView(TenantQuerySetMixin, LoginRequiredMixin, ListView):
    model = Driver
    template_name = 'drivers/driver_list.html'
    context_object_name = 'drivers'
    paginate_by = 10


class DriverDetailView(TenantQuerySetMixin, LoginRequiredMixin, DetailView):
    model = Driver
    template_name = 'drivers/driver_detail.html'
    context_object_name = 'driver'


class DriverCreateView(OperatorRequiredMixin, View):
    template_name = 'drivers/driver_form.html'

    def get(self, request):
        form = DriverCreateForm(company=get_user_company(request.user), user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = DriverCreateForm(
            request.POST,
            request.FILES,
            company=get_user_company(request.user),
            user=request.user,
        )
        if form.is_valid():
            driver = form.save()
            messages.success(request, f'Motorista {driver} cadastrado com sucesso!')
            return redirect('drivers:list')
        return render(request, self.template_name, {'form': form})


class DriverUpdateView(OperatorRequiredMixin, View):
    template_name = 'drivers/driver_form.html'

    def get_object(self, request, pk):
        queryset = scope_queryset_for_user(Driver.objects.all(), request.user)
        return get_object_or_404(queryset, pk=pk)

    def get(self, request, pk):
        driver = self.get_object(request, pk)
        form = DriverUpdateForm(instance=driver, company=get_user_company(request.user), user=request.user)
        return render(request, self.template_name, {'form': form, 'object': driver})

    def post(self, request, pk):
        driver = self.get_object(request, pk)
        form = DriverUpdateForm(
            request.POST,
            request.FILES,
            instance=driver,
            company=get_user_company(request.user),
            user=request.user,
        )
        if form.is_valid():
            form.save()
            messages.success(request, f'Motorista {driver} atualizado com sucesso!')
            return redirect('drivers:list')
        return render(request, self.template_name, {'form': form, 'object': driver})


class DriverDeleteView(TenantQuerySetMixin, ProtectedDeleteMixin, ManagerRequiredMixin, DeleteView):
    model = Driver
    template_name = 'drivers/driver_confirm_delete.html'
    success_url = reverse_lazy('drivers:list')
    protected_error_message = 'Este motorista nao pode ser excluido porque possui viagens vinculadas.'
