# messaging/views_mass_message.py
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Q, Count, Max, F
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from accounts.models import CustomUser
from .models import Message
import json

@staff_member_required
def mass_message_form(request):
    """
    Zeigt das Formular zum Senden von Massennachrichten an.
    """
    # Nur Fake-Profile für den Absender auswählen
    fake_profiles = CustomUser.objects.filter(is_fake=True)
    
    context = {
        'fake_profiles': fake_profiles,
        'title': 'Massennachrichten senden',
    }
    
    return render(request, 'admin/mass_message_form.html', context)

@staff_member_required
def mass_message_preview(request):
    """
    Gibt die Anzahl der ausgewählten Benutzer zurück, die die Nachricht erhalten würden.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Nur POST-Anfragen sind erlaubt.'}, status=400)
    
    # Parameter aus dem Formular extrahieren
    all_users = request.POST.get('all_users') == '1'
    activity_period = request.POST.get('activity_period', '')
    gender = request.POST.get('gender', '')
    region = request.POST.get('region', '')
    user_type = request.POST.get('user_type', 'real')
    no_conversations = request.POST.get('no_conversations') == '1'
    never_messaged = request.POST.get('never_messaged') == '1'
    
    # Basisabfrage für Benutzer
    users_query = CustomUser.objects.all()
    
    # Wenn nicht "Alle Benutzer" ausgewählt ist, Filter anwenden
    if not all_users:
        # Benutzertyp filtern
        if user_type == 'real':
            users_query = users_query.filter(is_fake=False)
        elif user_type == 'fake':
            users_query = users_query.filter(is_fake=True)
        
        # Geschlecht filtern
        if gender:
            users_query = users_query.filter(gender=gender)
        
        # Region/PLZ filtern
        if region:
            users_query = users_query.filter(postal_code__startswith=region)
        
        # Aktivitätszeitraum filtern
        if activity_period:
            days = int(activity_period)
            cutoff_date = timezone.now() - timedelta(days=days)
            
            # Benutzer, die in den letzten X Tagen aktiv waren (Nachrichten gesendet oder erhalten)
            active_user_ids = Message.objects.filter(
                Q(timestamp__gte=cutoff_date)
            ).values_list('sender_id', 'recipient_id').distinct()
            
            # Flache Liste von Benutzer-IDs erstellen
            active_ids = set()
            for sender_id, recipient_id in active_user_ids:
                active_ids.add(sender_id)
                active_ids.add(recipient_id)
            
            users_query = users_query.filter(id__in=active_ids)
        
        # Benutzer ohne aktive Gespräche filtern
        if no_conversations:
            # Benutzer-IDs mit Gesprächen finden
            users_with_conversations = Message.objects.values_list('sender_id', 'recipient_id').distinct()
            users_with_conv_ids = set()
            for sender_id, recipient_id in users_with_conversations:
                users_with_conv_ids.add(sender_id)
                users_with_conv_ids.add(recipient_id)
            
            # Benutzer ohne Gespräche auswählen
            users_query = users_query.exclude(id__in=users_with_conv_ids)
        
        # Benutzer, die noch nie eine Nachricht erhalten haben
        if never_messaged:
            users_with_messages = Message.objects.values_list('recipient_id', flat=True).distinct()
            users_query = users_query.exclude(id__in=users_with_messages)
    
    # Anzahl der ausgewählten Benutzer zählen
    user_count = users_query.count()
    
    return JsonResponse({'user_count': user_count})

@staff_member_required
def mass_message_send(request):
    """
    Sendet Nachrichten an die ausgewählten Benutzer.
    """
    if request.method != 'POST':
        return redirect('admin:index')
    
    # Parameter aus dem Formular extrahieren
    message_text = request.POST.get('message_text', '').strip()
    sender_profile_id = request.POST.get('sender_profile')
    all_users = request.POST.get('all_users') == '1'
    activity_period = request.POST.get('activity_period', '')
    gender = request.POST.get('gender', '')
    region = request.POST.get('region', '')
    user_type = request.POST.get('user_type', 'real')
    no_conversations = request.POST.get('no_conversations') == '1'
    never_messaged = request.POST.get('never_messaged') == '1'
    
    # Validierung
    if not message_text:
        messages.error(request, 'Der Nachrichtentext darf nicht leer sein.')
        return redirect('admin:mass_message_form')
    
    if not sender_profile_id:
        messages.error(request, 'Bitte wählen Sie ein Absender-Profil aus.')
        return redirect('admin:mass_message_form')
    
    try:
        sender_profile = CustomUser.objects.get(pk=sender_profile_id, is_fake=True)
    except (CustomUser.DoesNotExist, ValueError):
        messages.error(request, 'Das ausgewählte Absender-Profil ist ungültig.')
        return redirect('admin:mass_message_form')
    
    # Basisabfrage für Benutzer
    users_query = CustomUser.objects.all()
    
    # Wenn nicht "Alle Benutzer" ausgewählt ist, Filter anwenden
    if not all_users:
        # Benutzertyp filtern
        if user_type == 'real':
            users_query = users_query.filter(is_fake=False)
        elif user_type == 'fake':
            users_query = users_query.filter(is_fake=True)
        
        # Geschlecht filtern
        if gender:
            users_query = users_query.filter(gender=gender)
        
        # Region/PLZ filtern
        if region:
            users_query = users_query.filter(postal_code__startswith=region)
        
        # Aktivitätszeitraum filtern
        if activity_period:
            days = int(activity_period)
            cutoff_date = timezone.now() - timedelta(days=days)
            
            # Benutzer, die in den letzten X Tagen aktiv waren (Nachrichten gesendet oder erhalten)
            active_user_ids = Message.objects.filter(
                Q(timestamp__gte=cutoff_date)
            ).values_list('sender_id', 'recipient_id').distinct()
            
            # Flache Liste von Benutzer-IDs erstellen
            active_ids = set()
            for sender_id, recipient_id in active_user_ids:
                active_ids.add(sender_id)
                active_ids.add(recipient_id)
            
            users_query = users_query.filter(id__in=active_ids)
        
        # Benutzer ohne aktive Gespräche filtern
        if no_conversations:
            # Benutzer-IDs mit Gesprächen finden
            users_with_conversations = Message.objects.values_list('sender_id', 'recipient_id').distinct()
            users_with_conv_ids = set()
            for sender_id, recipient_id in users_with_conversations:
                users_with_conv_ids.add(sender_id)
                users_with_conv_ids.add(recipient_id)
            
            # Benutzer ohne Gespräche auswählen
            users_query = users_query.exclude(id__in=users_with_conv_ids)
        
        # Benutzer, die noch nie eine Nachricht erhalten haben
        if never_messaged:
            users_with_messages = Message.objects.values_list('recipient_id', flat=True).distinct()
            users_query = users_query.exclude(id__in=users_with_messages)
    
    # Nachrichten senden
    recipient_count = 0
    message_batch = []
    
    # Nachrichten in Batches erstellen
    batch_size = 500
    for recipient in users_query.iterator():
        # Nicht an sich selbst senden
        if recipient.id == sender_profile.id:
            continue
        
        message_batch.append(Message(
            sender=sender_profile,
            recipient=recipient,
            content=message_text
        ))
        recipient_count += 1
        
        # Batch speichern, wenn er voll ist
        if len(message_batch) >= batch_size:
            Message.objects.bulk_create(message_batch)
            message_batch = []
    
    # Restliche Nachrichten speichern
    if message_batch:
        Message.objects.bulk_create(message_batch)
    
    messages.success(request, f'Nachrichten wurden erfolgreich an {recipient_count} Benutzer gesendet.')
    return redirect('admin:index')
