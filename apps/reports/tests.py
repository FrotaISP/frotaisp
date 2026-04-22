from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.drivers.models import Driver
from apps.fuel.models import FuelRecord
from apps.maintenance.models import Maintenance
from apps.trips.models import Trip
from apps.vehicles.models import Vehicle


class ReportViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='report-user', password='senha123')
        UserProfile.objects.update_or_create(user=self.user, defaults={'role': 'manager'})
        self.driver = Driver.objects.create(
            user=self.user,
            cnh='88888888888',
            cnh_expiration='2030-01-01',
            phone='(62) 99999-1111',
        )
        self.vehicle = Vehicle.objects.create(
            plate='RPT1234',
            brand='Fiat',
            model='Toro',
            year=2024,
            fuel_type='F',
            current_odometer=12000,
        )
        self.fuel = FuelRecord.objects.create(
            vehicle=self.vehicle,
            date=timezone.localdate(),
            liters=Decimal('35.00'),
            price_per_liter=Decimal('5.50'),
            odometer=12100,
            gas_station='Posto Teste',
        )
        self.trip = Trip.objects.create(
            vehicle=self.vehicle,
            driver=self.driver,
            start_time=timezone.now(),
            end_time=timezone.now(),
            start_odometer=12100,
            end_odometer=12220,
            destination='Cliente Y',
            purpose='Atendimento',
            service_order='OS-500',
        )
        self.maintenance = Maintenance.objects.create(
            vehicle=self.vehicle,
            type='P',
            date=timezone.localdate(),
            description='Revisao',
            cost=Decimal('420.00'),
            odometer=12220,
            workshop='Oficina Teste',
        )

    def test_reports_dashboard_requires_authentication(self):
        response = self.client.get(reverse('reports:dashboard'))

        self.assertEqual(response.status_code, 302)

    def test_general_report_view_renders_for_authenticated_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('reports:general'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['trip_count'], 1)
        self.assertEqual(response.context['maint_count'], 1)

    def test_general_report_excel_returns_spreadsheet(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('reports:general_excel'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    def test_fuel_report_filters_by_vehicle(self):
        other_vehicle = Vehicle.objects.create(
            plate='RPT9999',
            brand='VW',
            model='Saveiro',
            year=2023,
            fuel_type='G',
            current_odometer=5000,
        )
        FuelRecord.objects.create(
            vehicle=other_vehicle,
            date=timezone.localdate(),
            liters=Decimal('20.00'),
            price_per_liter=Decimal('6.00'),
            odometer=5100,
            gas_station='Outro Posto',
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('reports:fuel'), {'vehicle': self.vehicle.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['records']), [self.fuel])
