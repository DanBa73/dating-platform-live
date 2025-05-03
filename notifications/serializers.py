from rest_framework import serializers
from .models import Notification, PushSubscription
from accounts.serializers import CustomUserDetailsSerializer

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer für das Notification-Modell
    """
    sender_details = CustomUserDetailsSerializer(source='sender', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'content', 'is_read', 'created_at',
            'reference_id', 'reference_model', 'sender_details'
        ]
        read_only_fields = ['id', 'created_at']

class NotificationSummarySerializer(serializers.Serializer):
    """
    Serializer für die Zusammenfassung der Benachrichtigungen
    """
    total_unread = serializers.IntegerField()
    new_likes = serializers.IntegerField()
    unread_messages = serializers.IntegerField()
    
class PushSubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer für das PushSubscription-Modell
    """
    class Meta:
        model = PushSubscription
        fields = ['id', 'subscription_info', 'created_at', 'last_used']
        read_only_fields = ['id', 'created_at', 'last_used']
