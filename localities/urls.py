from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'levels', views.LocalityLevelViewSet, basename='locality-level')
router.register(r'localities', views.LocalityViewSet, basename='locality')

urlpatterns = [
    path('', include(router.urls)),
]
