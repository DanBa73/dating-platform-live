from django.contrib import admin
from .models import Notification, PushSubscription

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'type', 'sender', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__username', 'sender__username', 'content')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user', 'sender')
    date_hierarchy = 'created_at'

@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'last_used')
    list_filter = ('created_at', 'last_used')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'last_used')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'
