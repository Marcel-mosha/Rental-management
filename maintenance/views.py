from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import MaintenanceRequest, MaintenanceImage
from .serializers import (
    MaintenanceRequestSerializer, MaintenanceRequestListSerializer,
    MaintenanceRequestCreateSerializer, MaintenanceStatusUpdateSerializer,
    MaintenanceImageSerializer
)
from .filters import MaintenanceRequestFilter
from notifications.services import NotificationService


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing maintenance requests."""
    
    queryset = MaintenanceRequest.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MaintenanceRequestFilter
    search_fields = ['description', 'unit__property__title', 'technician_name']
    ordering_fields = ['priority', 'status', 'request_date']
    ordering = ['-request_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MaintenanceRequestListSerializer
        if self.action == 'create':
            return MaintenanceRequestCreateSerializer
        return MaintenanceRequestSerializer
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return MaintenanceRequest.objects.all()
        
        queryset = MaintenanceRequest.objects.none()
        
        if hasattr(user, 'tenant_profile'):
            queryset = queryset | MaintenanceRequest.objects.filter(
                tenant=user.tenant_profile
            )
        
        if hasattr(user, 'owner_profile'):
            queryset = queryset | MaintenanceRequest.objects.filter(
                owner=user.owner_profile
            )
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        request = serializer.save()
        
        # Send notification to owner
        NotificationService.send_maintenance_submitted(request)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update maintenance request status."""
        maintenance_request = self.get_object()
        serializer = MaintenanceStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_status = maintenance_request.status
        new_status = serializer.validated_data['status']
        
        maintenance_request.status = new_status
        
        if new_status == 'acknowledged' and old_status == 'submitted':
            maintenance_request.acknowledged_date = timezone.now()
        
        if new_status == 'completed':
            maintenance_request.resolved_date = timezone.now()
            if 'cost' in serializer.validated_data:
                maintenance_request.cost = serializer.validated_data['cost']
            if 'cost_responsibility' in serializer.validated_data:
                maintenance_request.cost_responsibility = serializer.validated_data['cost_responsibility']
        
        if 'resolution_notes' in serializer.validated_data:
            maintenance_request.resolution_notes = serializer.validated_data['resolution_notes']
        if 'technician_name' in serializer.validated_data:
            maintenance_request.technician_name = serializer.validated_data['technician_name']
        if 'technician_contact' in serializer.validated_data:
            maintenance_request.technician_contact = serializer.validated_data['technician_contact']
        
        maintenance_request.save()
        
        # Send notification based on status change
        NotificationService.send_maintenance_update(maintenance_request, new_status)
        
        return Response(MaintenanceRequestSerializer(maintenance_request).data)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def add_image(self, request, pk=None):
        """Add an image to a maintenance request."""
        maintenance_request = self.get_object()
        serializer = MaintenanceImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(maintenance_request=maintenance_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Get urgent and high priority pending requests."""
        requests = self.get_queryset().filter(
            priority__in=['urgent', 'high'],
            status__in=['submitted', 'acknowledged', 'in_progress']
        )
        serializer = MaintenanceRequestListSerializer(requests, many=True)
        return Response(serializer.data)
