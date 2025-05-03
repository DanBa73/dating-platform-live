from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Notification, PushSubscription, NotificationType
from .serializers import (
    NotificationSerializer, 
    NotificationSummarySerializer,
    PushSubscriptionSerializer
)

class NotificationListView(ListAPIView):
    """
    API-Endpunkt zum Abrufen aller Benachrichtigungen eines Benutzers
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class NotificationDetailView(RetrieveUpdateAPIView):
    """
    API-Endpunkt zum Abrufen und Aktualisieren einer einzelnen Benachrichtigung
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class MarkNotificationReadView(APIView):
    """
    API-Endpunkt zum Markieren einer Benachrichtigung als gelesen
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk=None):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response(status=status.HTTP_200_OK)

class MarkAllNotificationsReadView(APIView):
    """
    API-Endpunkt zum Markieren aller Benachrichtigungen eines Benutzers als gelesen
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response(status=status.HTTP_200_OK)

class NotificationSummaryView(APIView):
    """
    API-Endpunkt zum Abrufen einer Zusammenfassung der Benachrichtigungen eines Benutzers
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Anzahl der ungelesenen Benachrichtigungen nach Typ
        unread_likes = Notification.objects.filter(
            user=user, 
            is_read=False, 
            type=NotificationType.LIKE
        ).count()
        
        unread_messages = Notification.objects.filter(
            user=user, 
            is_read=False, 
            type=NotificationType.MESSAGE
        ).count()
        
        total_unread = unread_likes + unread_messages + Notification.objects.filter(
            user=user, 
            is_read=False, 
            type=NotificationType.SYSTEM
        ).count()
        
        summary = {
            'total_unread': total_unread,
            'new_likes': unread_likes,
            'unread_messages': unread_messages
        }
        
        serializer = NotificationSummarySerializer(summary)
        return Response(serializer.data)

class PushSubscriptionView(APIView):
    """
    API-Endpunkt zum Erstellen und Aktualisieren von Push-Benachrichtigungsabonnements
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        subscription_info = request.data.get('subscription')
        if not subscription_info:
            return Response(
                {"error": "Subscription information is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vorhandenes Abonnement aktualisieren oder neues erstellen
        subscription, created = PushSubscription.objects.update_or_create(
            user=request.user,
            defaults={'subscription_info': subscription_info}
        )
        
        serializer = PushSubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    def delete(self, request):
        PushSubscription.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
