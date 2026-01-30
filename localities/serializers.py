from rest_framework import serializers
from .models import LocalityLevel, Locality


class LocalityLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalityLevel
        fields = ["id", "name", "slug", "parent", "code"]


class LocalitySerializer(serializers.ModelSerializer):
    level_name = serializers.CharField(source='level.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Locality
        fields = ["id", "name", "code", "level", "level_name", "parent", "parent_name"]


class LocalityDetailSerializer(serializers.ModelSerializer):
    """
    Serializer that returns locality with full hierarchy traversal.
    """
    country = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    ward = serializers.SerializerMethodField()
    street = serializers.SerializerMethodField()
    
    class Meta:
        model = Locality
        fields = ["country", "region", "district", "ward", "street"]
    
    def get_country(self, obj):
        return obj.get_hierarchy().get("country")
    
    def get_region(self, obj):
        return obj.get_hierarchy().get("region")
    
    def get_district(self, obj):
        return obj.get_hierarchy().get("district")
    
    def get_ward(self, obj):
        return obj.get_hierarchy().get("ward")
    
    def get_street(self, obj):
        return obj.get_hierarchy().get("street")