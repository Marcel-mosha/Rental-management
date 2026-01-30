from django.db import models
import uuid


class LocalityLevel(models.Model):
    """
    Administrative level hierarchy for Tanzania.
    e.g. Country > Region > District > Ward > Street
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True, help_text="URL-friendly identifier")
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="child_levels",
    )
    code = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Locality(models.Model):
    """
    A node in the Tanzania administrative hierarchy.
    Parent points to a higher level (or None for top).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=64, blank=True, default="")
    level = models.ForeignKey(
        LocalityLevel, on_delete=models.PROTECT, related_name="localities"
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="children"
    )

    class Meta:
        unique_together = ("name", "level", "parent")
        indexes = [
            models.Index(fields=["level", "parent"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    def get_hierarchy(self):
        from collections import OrderedDict
        
        hierarchy = OrderedDict([
            ("country", "Tanzania"),
            ("region", None),
            ("district", None),
            ("ward", None),
            ("street", None)
        ])
        
        current = self
        while current:
            level_slug = current.level.slug.lower() if current.level else None
            
            if level_slug in ["tanzania", "country"]:
                hierarchy["country"] = current.name
            elif level_slug == "region":
                hierarchy["region"] = current.name
            elif level_slug == "district":
                hierarchy["district"] = current.name
            elif level_slug == "ward":
                hierarchy["ward"] = current.name
            elif level_slug == "street":
                hierarchy["street"] = current.name
            
            current = current.parent
        
        return hierarchy
