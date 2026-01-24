from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# User management
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'documents', views.DocumentViewSet, basename='document')

# Profiles
router.register(r'tenants', views.TenantViewSet, basename='tenant')
router.register(r'owners', views.OwnerViewSet, basename='owner')

# Properties
router.register(r'properties', views.PropertyViewSet, basename='property')
router.register(r'property-images', views.PropertyImageViewSet, basename='property-image')
router.register(r'units', views.RentalUnitViewSet, basename='unit')

# Leases
router.register(r'leases', views.LeaseViewSet, basename='lease')

# Payments
router.register(r'payments', views.PaymentViewSet, basename='payment')

# Maintenance
router.register(r'maintenance-requests', views.MaintenanceRequestViewSet, basename='maintenance')

# Reviews
router.register(r'reviews', views.ReviewViewSet, basename='review')

# Notifications
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Dashboard endpoints
    path('dashboard/tenant/', views.TenantDashboardView.as_view(), name='tenant-dashboard'),
    path('dashboard/owner/', views.OwnerDashboardView.as_view(), name='owner-dashboard'),
    path('dashboard/admin/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
]
