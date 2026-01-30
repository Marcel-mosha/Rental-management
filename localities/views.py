from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsOwnerOrAdmin
from .models import LocalityLevel, Locality
from .serializers import LocalityLevelSerializer, LocalitySerializer


class LocalityLevelViewSet(viewsets.ModelViewSet):
    queryset = LocalityLevel.objects.all()
    serializer_class = LocalityLevelSerializer
    permission_classes = [IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "code"]
    filterset_fields = ["parent"]


class LocalityViewSet(viewsets.ModelViewSet):
    queryset = Locality.objects.select_related("level", "parent").all()
    serializer_class = LocalitySerializer
    permission_classes = [IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "code"]
    filterset_fields = ["level", "parent"]

    def get_queryset(self):
        qs = super().get_queryset()
        
        level = self.request.query_params.get("level")
        level_id = self.request.query_params.get("level_id")
        parent = self.request.query_params.get("parent")
        parent_id = self.request.query_params.get("parent_id")
        
        if level:
            qs = qs.filter(level__slug=level)
        if level_id:
            qs = qs.filter(level_id=level_id)
        if parent:
            qs = qs.filter(parent__name=parent)
        if parent_id:
            qs = qs.filter(parent_id=parent_id)
            
        return qs.order_by("name")

    @action(detail=False, methods=['get'])
    def regions(self, request):
        regions = Locality.objects.filter(level__slug='region').order_by('name')
        serializer = self.get_serializer(regions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def districts(self, request):
        districts = Locality.objects.filter(level__slug='district')
        region_id = request.query_params.get('region_id')
        if region_id:
            districts = districts.filter(parent_id=region_id)
        districts = districts.order_by('name')
        serializer = self.get_serializer(districts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def wards(self, request):
        wards = Locality.objects.filter(level__slug='ward')
        district_id = request.query_params.get('district_id')
        if district_id:
            wards = wards.filter(parent_id=district_id)
        wards = wards.order_by('name')
        serializer = self.get_serializer(wards, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def streets(self, request):
        streets = Locality.objects.filter(level__slug='street')
        ward_id = request.query_params.get('ward_id')
        if ward_id:
            streets = streets.filter(parent_id=ward_id)
        streets = streets.order_by('name')
        serializer = self.get_serializer(streets, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        locality = self.get_object()
        children = locality.children.all().order_by('name')
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)
