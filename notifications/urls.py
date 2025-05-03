from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Benachrichtigungen abrufen
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    
    # Benachrichtigungen als gelesen markieren
    path('<int:pk>/read/', views.MarkNotificationReadView.as_view(), name='mark-notification-read'),
    path('read-all/', views.MarkAllNotificationsReadView.as_view(), name='mark-all-notifications-read'),
    
    # Zusammenfassung der Benachrichtigungen
    path('summary/', views.NotificationSummaryView.as_view(), name='notification-summary'),
    
    # Push-Benachrichtigungen
    path('push-subscription/', views.PushSubscriptionView.as_view(), name='push-subscription'),
]
