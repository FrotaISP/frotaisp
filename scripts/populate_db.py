#!/usr/bin/env python
"""
Script para popular o banco de dados com dados de teste para o FleetISP.
Executar com: python scripts/populate_db.py
"""
import os
import sys
import random
import datetime
from decimal import Decimal

# Configuração do ambiente Django DEVE vir antes de qualquer import do Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

# Agora importamos os módulos do Django e dos apps
from django.utils import timezone
from django.contrib.auth.models import User
from faker import Faker

from apps.vehicles.models import Vehicle
from apps.drivers.models import Driver
from apps.trips.models import Trip
from apps.fuel.models import FuelRecord
from apps.maintenance.models import Maintenance

fake = Faker('pt_BR')

# Configurações de quantidade
NUM_DRIVERS = 8
NUM_VEHICLES = 10
NUM_TRIPS_PER_VEHICLE = 5
NUM_FUEL_RECORDS_PER_VEHICLE = 10
NUM_MAINTENANCES_PER_VEHICLE = 3


def create_users_and_drivers():
    """Cria usuários e perfis de motorista."""
    print("Criando motoristas...")
    drivers = []
    for i in range(NUM_DRIVERS):
        username = f"motorista{i+1}"
        first_name = fake.first_name()
        last_name = fake.last_name()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': f"{username}@fleetisp.com",
            }
        )
        if created:
            user.set_password('senha123')
            user.save()

        # Criar perfil Driver
        driver, created = Driver.objects.get_or_create(
            user=user,
            defaults={
                'cnh': fake.numerify(text='###########'),
                'cnh_expiration': fake.date_between(start_date='+1y', end_date='+5y'),
                'phone': fake.cellphone_number(),
                'address': fake.address(),
                'is_available': random.choice([True, True, True, False]),
            }
        )
        drivers.append(driver)
    print(f"  Criados {len(drivers)} motoristas.")
    return drivers


def create_vehicles():
    """Cria veículos de diferentes modelos."""
    print("Criando veículos...")
    models_data = [
        ('Fiat', 'Fiorino', 'G', 650),
        ('Renault', 'Master', 'D', 1500),
        ('VW', 'Saveiro', 'F', 700),
        ('Ford', 'Ranger', 'D', 1000),
        ('Toyota', 'Hilux', 'D', 1000),
        ('Chevrolet', 'S10', 'D', 1000),
        ('Fiat', 'Strada', 'F', 650),
        ('Mercedes-Benz', 'Sprinter', 'D', 2000),
        ('Peugeot', 'Partner', 'F', 800),
        ('Citroën', 'Jumpy', 'F', 900),
    ]

    vehicles = []
    for brand, model, fuel, capacity in models_data:
        plate = fake.license_plate()
        year = random.randint(2018, 2024)
        while Vehicle.objects.filter(plate=plate).exists():
            plate = fake.license_plate()

        vehicle = Vehicle.objects.create(
            plate=plate,
            brand=brand,
            model=model,
            year=year,
            chassis=fake.numerify(text='#################'),
            fuel_type=fuel,
            capacity_kg=capacity,
            current_odometer=random.randint(5000, 120000),
            is_active=True,
        )
        vehicles.append(vehicle)
    print(f"  Criados {len(vehicles)} veículos.")
    return vehicles


def create_trips(vehicles, drivers):
    """Cria viagens (algumas finalizadas, outras em andamento)."""
    print("Criando viagens...")
    trip_count = 0

    for vehicle in vehicles:
        for _ in range(NUM_TRIPS_PER_VEHICLE):
            driver = random.choice(drivers)
            start_date = fake.date_time_between(
                start_date='-60d', end_date='now', tzinfo=timezone.get_current_timezone()
            )
            start_odometer = random.randint(vehicle.current_odometer - 5000, vehicle.current_odometer - 10)
            if start_odometer < 0:
                start_odometer = 1000

            if random.random() < 0.8:  # 80% finalizada
                end_time = start_date + datetime.timedelta(hours=random.randint(1, 8))
                distance = random.randint(10, 200)
                end_odometer = start_odometer + distance
            else:
                end_time = None
                end_odometer = None

            Trip.objects.create(
                vehicle=vehicle,
                driver=driver,
                start_time=start_date,
                end_time=end_time,
                start_odometer=start_odometer,
                end_odometer=end_odometer,
                destination=fake.city(),
                purpose=random.choice([
                    'Instalação de novo cliente',
                    'Reparo técnico',
                    'Vistoria de rede',
                    'Entrega de equipamentos',
                    'Manutenção preventiva externa',
                ]),
                service_order=f"OS-{fake.numerify(text='####')}" if random.random() > 0.3 else '',
            )
            trip_count += 1

            if end_odometer:
                vehicle.current_odometer = end_odometer
                vehicle.save()

    print(f"  Criadas {trip_count} viagens.")


def create_fuel_records(vehicles):
    """Cria registros de abastecimento."""
    print("Criando abastecimentos...")
    fuel_count = 0

    for vehicle in vehicles:
        current_km = vehicle.current_odometer
        for _ in range(NUM_FUEL_RECORDS_PER_VEHICLE):
            days_ago = random.randint(1, 90)
            date = timezone.now().date() - datetime.timedelta(days=days_ago)

            km = current_km - random.randint(0, 2000)
            if km < 1000:
                km = 1000

            liters = Decimal(random.uniform(30, 80)).quantize(Decimal('0.01'))
            price_per_liter = Decimal(random.uniform(5.0, 7.5)).quantize(Decimal('0.01'))

            FuelRecord.objects.create(
                vehicle=vehicle,
                date=date,
                liters=liters,
                price_per_liter=price_per_liter,
                odometer=km,
                gas_station=random.choice([
                    'Posto Ipiranga', 'Posto Shell', 'Posto Petrobras',
                    'Posto Ale', 'Posto BR', 'Auto Posto Center'
                ]) + ' ' + fake.city(),
            )
            fuel_count += 1
            current_km = km - random.randint(100, 500)

    print(f"  Criados {fuel_count} abastecimentos.")


def create_maintenances(vehicles):
    """Cria manutenções (preventivas e corretivas)."""
    print("Criando manutenções...")
    maint_count = 0

    for vehicle in vehicles:
        current_km = vehicle.current_odometer
        for _ in range(NUM_MAINTENANCES_PER_VEHICLE):
            days_ago = random.randint(10, 300)
            date = timezone.now().date() - datetime.timedelta(days=days_ago)
            km = current_km - random.randint(1000, 10000)
            if km < 1000:
                km = 1000

            maint_type = random.choice(['P', 'C', 'E'])
            cost = Decimal(random.uniform(150, 2500)).quantize(Decimal('0.01'))

            if maint_type == 'P':
                next_alert_km = km + random.choice([5000, 10000, 15000])
                next_alert_date = date + datetime.timedelta(days=180)
            else:
                next_alert_km = None
                next_alert_date = None

            Maintenance.objects.create(
                vehicle=vehicle,
                type=maint_type,
                date=date,
                description=random.choice([
                    'Troca de óleo e filtros',
                    'Revisão geral',
                    'Troca de pneus',
                    'Reparo no sistema de freios',
                    'Troca de correia dentada',
                    'Alinhamento e balanceamento',
                    'Reparo elétrico',
                    'Troca de amortecedores',
                ]),
                cost=cost,
                odometer=km,
                workshop=f'Oficina {fake.company()}',
                next_alert_km=next_alert_km,
                next_alert_date=next_alert_date,
            )
            maint_count += 1
            current_km = km

    print(f"  Criadas {maint_count} manutenções.")


def main():
    print("=" * 50)
    print("Populando banco de dados do FleetISP...")
    print("=" * 50)

    if Vehicle.objects.exists() or Driver.objects.exists():
        resp = sys.argv[1] if len(sys.argv) > 1 else "n"
        if resp.lower() == 's':
            print("Apagando dados existentes...")
            Maintenance.objects.all().delete()
            FuelRecord.objects.all().delete()
            Trip.objects.all().delete()
            Vehicle.objects.all().delete()
            Driver.objects.all().delete()
            User.objects.filter(username__startswith='motorista').delete()
        else:
            print("Operação cancelada.")
            return

    drivers = create_users_and_drivers()
    vehicles = create_vehicles()
    create_trips(vehicles, drivers)
    create_fuel_records(vehicles)
    create_maintenances(vehicles)

    print("\n✅ População concluída com sucesso!")
    print(f"   - Motoristas: {Driver.objects.count()}")
    print(f"   - Veículos: {Vehicle.objects.count()}")
    print(f"   - Viagens: {Trip.objects.count()}")
    print(f"   - Abastecimentos: {FuelRecord.objects.count()}")
    print(f"   - Manutenções: {Maintenance.objects.count()}")


if __name__ == '__main__':
    main()