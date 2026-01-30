from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer."""
    notification_type_display = serializers.CharField(
        source='get_notification_type_display', read_only=True
    )
    message_localized = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'notification_type_display',
                  'title', 'message', 'message_swahili', 'message_localized',
                  'is_read', 'created_at', 'action_url']
        read_only_fields = ['id', 'created_at']
    
    def get_message_localized(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.get_message(request.user.preferred_language)
        return obj.message
