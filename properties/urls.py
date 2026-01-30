from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'properties', views.PropertyViewSet, basename='property')
router.register(r'images', views.PropertyImageViewSet, basename='property-image')
router.register(r'units', views.RentalUnitViewSet, basename='rental-unit')

urlpatterns = [
    path('', include(router.urls)),
]
