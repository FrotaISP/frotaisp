# apps/trips/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from apps.core.mixins import TripRegisterMixin, ManagerRequiredMixin
from .models import Trip


class TripListView(LoginRequiredMixin, ListView):
    model = Trip
    template_name = 'trips/trip_list.html'
    context_object_name = 'trips'
    paginate_by = 10


class TripDetailView(LoginRequiredMixin, DetailView):
    model = Trip
    template_name = 'trips/trip_detail.html'
    context_object_name = 'trip'


class TripCreateView(TripRegisterMixin, CreateView):
    model = Trip
    fields = ['vehicle', 'driver', 'start_time', 'start_odometer', 'destination', 'purpose', 'service_order']
    template_name = 'trips/trip_form.html'
    success_url = reverse_lazy('trips:list')

    def get_initial(self):
        initial = super().get_initial()
        initial['start_time'] = timezone.now()
        return initial


class TripUpdateView(TripRegisterMixin, UpdateView):
    model = Trip
    fields = ['vehicle', 'driver', 'start_time', 'end_time', 'start_odometer', 'end_odometer', 'destination', 'purpose', 'service_order']
    template_name = 'trips/trip_form.html'
    success_url = reverse_lazy('trips:list')


class TripDeleteView(ManagerRequiredMixin, DeleteView):
    model = Trip
    template_name = 'trips/trip_confirm_delete.html'
    success_url = reverse_lazy('trips:list')
