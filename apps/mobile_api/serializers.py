from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import UserProfile
from apps.drivers.models import Driver
from apps.trips.models import Trip
from apps.vehicles.models import Vehicle, VehicleChecklist, VehicleDocument


class MobileLoginSerializer(serializers.Serializer):
    username = serializers.CharField(label='Usuario')
    password = serializers.CharField(label='Senha', write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        request = self.context.get('request')
        user = authenticate(request=request, username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Usuario ou senha invalidos.')
        if not user.is_active:
            raise serializers.ValidationError('Usuario inativo.')
        profile = getattr(user, 'profile', None)
        if not (user.is_superuser or (profile and profile.is_driver)):
            raise serializers.ValidationError('Este usuario nao possui acesso ao app do motorista.')
        attrs['user'] = user
        return attrs


class MobileVehicleSerializer(serializers.ModelSerializer):
    tracking_status = serializers.CharField(read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'plate', 'brand', 'model', 'year', 'fuel_type', 'current_odometer',
            'latitude', 'longitude', 'last_location_at', 'last_speed_kmh',
            'heading_degrees', 'location_source', 'tracking_status',
        ]


class MobileTripSerializer(serializers.ModelSerializer):
    vehicle = MobileVehicleSerializer(read_only=True)
    distance_km = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'vehicle', 'start_time', 'end_time', 'start_odometer', 'end_odometer',
            'destination', 'purpose', 'service_order', 'distance_km', 'status',
        ]

    def get_distance_km(self, obj):
        return obj.distance()

    def get_status(self, obj):
        return 'in_progress' if not obj.end_time else 'completed'


class MobileChecklistSerializer(serializers.ModelSerializer):
    vehicle = MobileVehicleSerializer(read_only=True)
    has_issues = serializers.BooleanField(read_only=True)

    class Meta:
        model = VehicleChecklist
        fields = [
            'id', 'vehicle', 'inspected_at', 'odometer', 'tires_ok', 'oil_ok', 'brakes_ok',
            'lights_ok', 'safety_items_ok', 'cleanliness_ok', 'status', 'notes', 'photo', 'has_issues',
        ]


class MobileDocumentSerializer(serializers.ModelSerializer):
    days_until_expiration = serializers.IntegerField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    vehicle = MobileVehicleSerializer(read_only=True)

    class Meta:
        model = VehicleDocument
        fields = [
            'id', 'document_type', 'title', 'number', 'expiration_date', 'days_until_expiration',
            'is_expired', 'is_expiring_soon', 'vehicle', 'notes',
        ]


class MobileDriverProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.profile.role', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    assigned_vehicles = serializers.SerializerMethodField()

    class Meta:
        model = Driver
        fields = [
            'id', 'name', 'username', 'email', 'phone', 'cnh', 'cnh_expiration',
            'is_available', 'company_name', 'role', 'assigned_vehicles',
        ]

    def get_assigned_vehicles(self, obj):
        vehicles = obj.assigned_vehicles.filter(is_active=True).order_by('plate')
        return MobileVehicleSerializer(vehicles, many=True).data


class DriverTripStartSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField(required=False)
    destination = serializers.CharField(max_length=255)
    purpose = serializers.CharField()
    service_order = serializers.CharField(max_length=50, required=False, allow_blank=True)
    start_odometer = serializers.IntegerField(min_value=0)
    start_time = serializers.DateTimeField(required=False)

    def validate_start_time(self, value):
        return value or timezone.now()


class DriverTripFinishSerializer(serializers.Serializer):
    end_odometer = serializers.IntegerField(min_value=0)
    end_time = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        trip = self.context['trip']
        end_odometer = attrs['end_odometer']
        if end_odometer < trip.start_odometer:
            raise serializers.ValidationError({'end_odometer': 'O hodometro final nao pode ser menor que o inicial.'})
        attrs['end_time'] = attrs.get('end_time') or timezone.now()
        return attrs


class DriverChecklistCreateSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField(required=False)
    odometer = serializers.IntegerField(required=False, min_value=0, allow_null=True)
    tires_ok = serializers.BooleanField(default=True)
    oil_ok = serializers.BooleanField(default=True)
    brakes_ok = serializers.BooleanField(default=True)
    lights_ok = serializers.BooleanField(default=True)
    safety_items_ok = serializers.BooleanField(default=True)
    cleanliness_ok = serializers.BooleanField(default=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        flags = [
            attrs.get('tires_ok', True),
            attrs.get('oil_ok', True),
            attrs.get('brakes_ok', True),
            attrs.get('lights_ok', True),
            attrs.get('safety_items_ok', True),
            attrs.get('cleanliness_ok', True),
        ]
        attrs['status'] = 'approved' if all(flags) else 'attention'
        return attrs


class DriverLocationUpdateSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField(required=False)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    speed_kmh = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    heading_degrees = serializers.IntegerField(required=False, min_value=0, max_value=360, allow_null=True)
    location_source = serializers.CharField(max_length=80, required=False, allow_blank=True)
    recorded_at = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        attrs['recorded_at'] = attrs.get('recorded_at') or timezone.now()
        return attrs
