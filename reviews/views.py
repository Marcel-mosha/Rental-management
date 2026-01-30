from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Review
from .serializers import (
    ReviewSerializer, ReviewListSerializer, ReviewCreateSerializer,
    ReviewResponseSerializer
)
from notifications.services import NotificationService


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for managing reviews."""
    
    queryset = Review.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['rating', 'review_date']
    ordering = ['-review_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReviewListSerializer
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Review.objects.filter(is_visible=True)
        
        # Filter by property if specified
        property_id = self.request.query_params.get('property')
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        
        # Filter by tenant if specified
        tenant_id = self.request.query_params.get('tenant')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """Add a response to a review."""
        review = self.get_object()
        serializer = ReviewResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verify the responder is authorized
        user = request.user
        can_respond = False
        
        if review.review_type == 'tenant_to_property':
            # Owner can respond
            if hasattr(user, 'owner_profile') and review.property.owner == user.owner_profile:
                can_respond = True
        elif review.review_type == 'owner_to_tenant':
            # Tenant can respond
            if hasattr(user, 'tenant_profile') and review.tenant == user.tenant_profile:
                can_respond = True
        
        if not can_respond:
            return Response(
                {'error': 'You are not authorized to respond to this review'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        review.response = serializer.validated_data['response']
        review.response_date = timezone.now()
        review.response_by = user
        review.save()
        
        # Send notification
        NotificationService.send_review_response(review)
        
        return Response(ReviewSerializer(review).data)
