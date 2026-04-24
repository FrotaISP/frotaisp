from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.fuel.models import FuelRecord
from apps.drivers.models import Driver
from apps.trips.models import Trip
from apps.vehicles.models import Vehicle, VehicleChecklist, VehicleDocument

from .permissions import IsDriverMobileUser
from .serializers import (
    DriverChecklistCreateSerializer,
    DriverFuelCreateSerializer,
    DriverLocationUpdateSerializer,
    DriverOccurrenceCreateSerializer,
    DriverTripFinishSerializer,
    DriverTripStartSerializer,
    MobileChecklistSerializer,
    MobileDocumentSerializer,
    MobileDriverProfileSerializer,
    MobileFuelRecordSerializer,
    MobileLoginSerializer,
    MobileOccurrenceSerializer,
    MobileTripSerializer,
    MobileVehicleSerializer,
    notify_managers_about_occurrence,
)
from .models import MobileOccurrence


def get_driver_for_user(user):
    return Driver.objects.select_related('user', 'company').prefetch_related('assigned_vehicles').filter(user=user).first()


def get_mobile_driver(user):
    driver = get_driver_for_user(user)
    if driver:
        return driver
    raise PermissionError('Motorista nao encontrado para este usuario.')


def get_open_trip(driver):
    return Trip.objects.select_related('vehicle').filter(driver=driver, end_time__isnull=True).order_by('-start_time').first()


def get_allowed_vehicles(driver):
    assigned = Vehicle.objects.filter(current_driver=driver, is_active=True)
    if assigned.exists():
        return assigned.order_by('plate')
    explicit_assignments = driver.assigned_vehicles.filter(is_active=True)
    if explicit_assignments.exists():
        return explicit_assignments.order_by('plate')
    return Vehicle.objects.filter(company=driver.company, is_active=True).order_by('plate')


def resolve_vehicle_for_driver(driver, vehicle_id=None):
    allowed = get_allowed_vehicles(driver)
    if vehicle_id:
        return allowed.filter(pk=vehicle_id).first()
    open_trip = get_open_trip(driver)
    if open_trip:
        return open_trip.vehicle
    if allowed.count() == 1:
        return allowed.first()
    return None


class MobileLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MobileLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        driver = get_driver_for_user(user)
        if not (user.is_superuser or driver):
            return Response({'detail': 'Motorista nao encontrado para este usuario.'}, status=status.HTTP_403_FORBIDDEN)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'driver': MobileDriverProfileSerializer(driver).data if driver else None,
        })


class MobileLogoutView(APIView):
    permission_classes = [IsAuthenticated, IsDriverMobileUser]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MobileMeView(APIView):
    permission_classes = [IsAuthenticated, IsDriverMobileUser]

    def get(self, request):
        try:
            driver = get_mobile_driver(request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return Response(MobileDriverProfileSerializer(driver).data)


class MobileDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsDriverMobileUser]

    def get(self, request):
        try:
            driver = get_mobile_driver(request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)

        today = timezone.localdate()
        open_trip = get_open_trip(driver)
        today_trips = Trip.objects.select_related('vehicle').filter(driver=driver, start_time__date=today).order_by('-start_time')[:5]
        recent_checklists = VehicleChecklist.objects.select_related('vehicle').filter(driver=driver).order_by('-inspected_at')[:5]
        documents = VehicleDocument.objects.select_related('vehicle').filter(
            company=driver.company,
            expiration_date__lte=today + timedelta(days=30),
            is_active=True,
        ).filter(Q(driver=driver) | Q(vehicle__current_driver=driver)).order_by('expiration_date')[:5]
        recent_fuel = FuelRecord.objects.select_related('vehicle').filter(
            company=driver.company,
            vehicle__in=get_allowed_vehicles(driver),
        ).order_by('-date', '-created_at')[:5]
        recent_occurrences = MobileOccurrence.objects.select_related('vehicle').filter(driver=driver).order_by('-reported_at')[:5]
        allowed_vehicles = get_allowed_vehicles(driver)

        return Response({
            'driver': MobileDriverProfileSerializer(driver).data,
            'assigned_vehicles': MobileVehicleSerializer(allowed_vehicles, many=True).data,
            'open_trip': MobileTripSerializer(open_trip).data if open_trip else None,
            'today_trips': MobileTripSerializer(today_trips, many=True).data,
            'recent_checklists': MobileChecklistSerializer(recent_checklists, many=True).data,
            'expiring_documents': MobileDocumentSerializer(documents, many=True).data,
            'recent_fuel_records': MobileFuelRecordSerializer(recent_fuel, many=True, context={'request': request}).data,
            'recent_occurrences': MobileOccurrenceSerializer(recent_occurrences, many=True, context={'request': request}).data,
        })


class MobileTripListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsDriverMobileUser]

    def get(self, request):
        try:
            driver = get_mobile_driver(request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        trips = Trip.objects.select_related('vehicle').filter(driver=driver).order_by('-start_time')[:30]
        return Response(MobileTripSerializer(trips, many=True).data)

    def post(self, request):
        try:
            driver = get_mobile_driver(request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        if get_open_trip(driver):
            return Response({'detail': 'Ja existe uma viagem em andamento para este motorista.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DriverTripStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vehicle = resolve_vehicle_for_driver(driver, serializer.validated_data.get('vehicle_id'))
        if not vehicle:
            return Response({'detail': 'Nenhum veiculo disponivel para este motorista.'}, status=status.HTTP_400_BAD_REQUEST)

        trip = Trip.objects.create(
            company=driver.company,
            driver=driver,
            vehicle=vehicle,
            destination=serializer.validated_data['destination'],
            purpose=serializer.validated_data['purpose'],
            service_order=serializer.validated_data.get('service_order', ''),
            start_odometer=serializer.validated_data['start_odometer'],
            start_time=serializer.validated_data.get('start_time') or timezone.now(),
        )
        return Response(MobileTripSerializer(trip).data, status=status.HTTP_201_CREATED)


class MobileTripFinishView(APIView):
    permission_classes = [IsAuthenticated, IsDriverMobileUser]

    def post(self, request, pk):
        try:
            driver = get_mobile_driver(request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)

        trip = Trip.objects.select_related('vehicle').filter(pk=pk, driver=driver).first()
        if not trip:
            return Response({'detail': 'Viagem nao encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        if trip.end_time:
            return Response({'detail': 'Esta viagem ja foi finalizada.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DriverTripFinishSerializer(data=request.data, context={'trip': trip})
        serializer.is_valid(raise_exception=True)
        trip.end_odometer = serializer.validated_data['end_odometer']
        trip.end_time = serializer.validated_data['end_time']
        trip.save()
        return Response(MobileTripSerializer(trip).data)


class MobileChecklistListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsDriverMobileUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        try:
            driver = get_mobile_driver(request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        items = VehicleChecklist.objects.select_related('vehicle').filter(driver=driver).order_by('-inspected_at')[:20]
        return Response(MobileChecklistSerializer(items, many=True, context={'request': request}).data)

    def post(self, request):
        try:
            driver = get_mobile_driver(request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        serializer = DriverChecklistCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vehicle = resolve_vehicle_for_driver(driver, serializer.validated_data.get('vehicle_id'))
        if not vehicle:
            return Response({'detail': 'Nenhum veiculo disponivel para checklist.'}, status=status.HTTP_400_BAD_REQUEST)

        checklist = VehicleChecklist.objects.create(
            company=driver.company,
            driver=driver,
            vehicle=vehicle,
            odometer=serializer.validated_data.get('odometer'),
            tires_ok=serializer.validated_data['tires_ok'],
            oil_ok=serializer.validated_data['oil_ok'],
            brakes_ok=serializer.validated_data['brakes_ok'],
            lights_ok=serializer.validated_data['lights_ok'],
            safety_items_ok=serializer.validated_data['safety_items_ok'],
            cleanliness_ok=serializer.validated_data['cleanliness_ok'],
            notes=serializer.validated_data.get('notes', ''),
            status=serializer.validated_data['status'],
            photo=serializer.validated_data.get('photo'),
        )
        return Response(MobileChecklistSerializer(checklist, context={'request': request}).data, status=status.HTTP_201_CREATED)


class MobileFuelListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsDriverMobileUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        try:
            driver = get_mobile_driver(request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        items = FuelRecord.objects.select_related('vehicle').filter(
            company=driver.company,
            vehicle__in=get_allowed_vehicles(driver),
        ).order_by('-date', '-created_at')[:20]
        return Response(MobileFuelRecordSerializer(items, many=True, context={'request': request}).data)

    def post(self, request):
        try:
            driver = get_mobile_driver(request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        serializer = DriverFuelCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vehicle = resolve_vehicle_for_driver(driver, serializer.validated_data.get('vehicle_id'))
        if not vehicle:
            return Response({'detail': 'Nenhum veiculo disponivel para abastecimento.'}, status=status.HTTP_400_BAD_REQUEST)

        record = FuelRecord.objects.create(
            company=driver.company,
            vehicle=vehicle,
            date=serializer.validated_data['date'],
            liters=serializer.validated_data['liters'],
            price_per_liter=serializer.validated_data['price_per_liter'],
            odometer=serializer.validated_data['odometer'],
            gas_station=serializer.validated_data['gas_station'],
            station_city=serializer.validated_data.get('station_city', ''),
            payment_method=serializer.validated_data.get('payment_method', ''),
            is_full_tank=serializer.validated_data.get('is_full_tank', False),
            notes=serializer.validated_data.get('notes', ''),
            photo=serializer.validated_data.get('photo'),
            receipt=serializer.validated_data.get('receipt'),
        )
        return Response(MobileFuelRecordSerializer(record, context={'request': request}).data, status=status.HTTP_201_CREATED)


class MobileOccurrenceListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsDriverMobileUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        try:
            driver = get_mobile_driver(request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        items = MobileOccurrence.objects.select_related('vehicle').filter(driver=driver).order_by('-reported_at')[:30]
        return Response(MobileOccurrenceSerializer(items, many=True, context={'request': request}).data)

    def post(self, request):
        try:
            driver = get_mobile_driver(request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        serializer = DriverOccurrenceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vehicle = resolve_vehicle_for_driver(driver, serializer.validated_data.get('vehicle_id'))
        occurrence = MobileOccurrence.objects.create(
            company=driver.company,
            driver=driver,
            vehicle=vehicle,
            title=serializer.validated_data['title'],
            category=serializer.validated_data['category'],
            description=serializer.validated_data['description'],
            severity=serializer.validated_data['severity'],
            attachment=serializer.validated_data.get('attachment'),
        )
        notify_managers_about_occurrence(occurrence)
        return Response(MobileOccurrenceSerializer(occurrence, context={'request': request}).data, status=status.HTTP_201_CREATED)


class MobileDriverDocumentsView(APIView):
    permission_classes = [IsAuthenticated, IsDriverMobileUser]

    def get(self, request):
        try:
            driver = get_mobile_driver(request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        today = timezone.localdate()
        documents = VehicleDocument.objects.select_related('vehicle').filter(
            company=driver.company,
            is_active=True,
        ).filter(Q(driver=driver) | Q(vehicle__current_driver=driver)).order_by('expiration_date', 'title')
        soon = request.query_params.get('soon')
        if soon == '1':
            documents = documents.filter(expiration_date__lte=today + timedelta(days=30))
        return Response(MobileDocumentSerializer(documents[:50], many=True).data)


class MobileLocationUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsDriverMobileUser]

    def post(self, request):
        try:
            driver = get_mobile_driver(request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        serializer = DriverLocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vehicle = resolve_vehicle_for_driver(driver, serializer.validated_data.get('vehicle_id'))
        if not vehicle:
            return Response({'detail': 'Nenhum veiculo disponivel para atualizar localizacao.'}, status=status.HTTP_400_BAD_REQUEST)

        vehicle.latitude = serializer.validated_data['latitude']
        vehicle.longitude = serializer.validated_data['longitude']
        vehicle.last_location_at = serializer.validated_data['recorded_at']
        vehicle.last_speed_kmh = serializer.validated_data.get('speed_kmh')
        vehicle.heading_degrees = serializer.validated_data.get('heading_degrees')
        vehicle.location_source = serializer.validated_data.get('location_source', 'app_mobile') or 'app_mobile'
        if vehicle.current_driver_id != driver.id:
            vehicle.current_driver = driver
        vehicle.save(update_fields=['latitude', 'longitude', 'last_location_at', 'last_speed_kmh', 'heading_degrees', 'location_source', 'current_driver', 'updated_at'])

        return Response({
            'detail': 'Localizacao atualizada com sucesso.',
            'vehicle': MobileVehicleSerializer(vehicle).data,
        })
