from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import Property, PropertyImage, PropertyAmenity, RentalUnit
from .serializers import (
    PropertySerializer, PropertyListSerializer, PropertyCreateSerializer,
    PropertyImageSerializer, PropertyAmenitySerializer,
    RentalUnitSerializer, RentalUnitListSerializer
)
from .filters import PropertyFilter, RentalUnitFilter
from accounts.permissions import IsOwner, IsPropertyOwner


class PropertyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing properties."""
    
    queryset = Property.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ['title', 'description', 'locality']
    ordering_fields = ['monthly_rent', 'listed_date', 'created_at']
    ordering = ['-listed_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        if self.action == 'create':
            return PropertyCreateSerializer
        return PropertySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'create':
            return [IsOwner()]
        return [IsPropertyOwner()]
    
    def get_queryset(self):
        queryset = Property.objects.select_related('owner', 'locality')
        
        # Filter by owner if specified
        owner_only = self.request.query_params.get('my_properties')
        if owner_only and hasattr(self.request.user, 'owner_profile'):
            queryset = queryset.filter(owner=self.request.user.owner_profile)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available properties."""
        properties = Property.objects.filter(is_available=True)
        serializer = PropertyListSerializer(
            properties, many=True, context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def units(self, request, pk=None):
        """Get all units for a property."""
        property_obj = self.get_object()
        units = property_obj.units.all()
        serializer = RentalUnitSerializer(units, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get all reviews for a property."""
        from reviews.serializers import ReviewListSerializer
        property_obj = self.get_object()
        reviews = property_obj.reviews.filter(is_visible=True)
        serializer = ReviewListSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def add_image(self, request, pk=None):
        """Add an image to a property."""
        property_obj = self.get_object()
        serializer = PropertyImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(property=property_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def add_amenities(self, request, pk=None):
        """Add amenities to a property."""
        property_obj = self.get_object()
        amenities = request.data.get('amenities', [])
        
        created = []
        for amenity_code in amenities:
            amenity, is_created = PropertyAmenity.objects.get_or_create(
                property=property_obj,
                amenity=amenity_code
            )
            if is_created:
                created.append(amenity_code)
        
        return Response({
            'message': f'Added {len(created)} amenities',
            'amenities': created
        })


class PropertyImageViewSet(viewsets.ModelViewSet):
    """ViewSet for property images."""
    
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        property_id = self.request.query_params.get('property')
        if property_id:
            return PropertyImage.objects.filter(property_id=property_id)
        return PropertyImage.objects.all()


class RentalUnitViewSet(viewsets.ModelViewSet):
    """ViewSet for managing rental units."""
    
    queryset = RentalUnit.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RentalUnitFilter
    search_fields = ['unit_number', 'property__title']
    ordering_fields = ['unit_rent', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RentalUnitListSerializer
        return RentalUnitSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsPropertyOwner()]
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available (unoccupied) units."""
        units = RentalUnit.objects.filter(is_occupied=False)
        serializer = RentalUnitListSerializer(units, many=True)
        return Response(serializer.data)
