#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Profil-Importer für Dating-Plattform

Dieses Skript importiert heruntergeladene Profile und Bilder in die Dating-Plattform.
Es verwendet die Django-Modelle der Plattform, um neue Fake-Profile zu erstellen.
"""

import os
import sys
import json
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Django-Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# Importiere Django-Modelle
from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.utils import timezone
from accounts.models import UserProfileImage, GenderChoices

User = get_user_model()  # CustomUser-Modell

class ProfileImporter:
    """Klasse zum Importieren von Profilen in die Dating-Plattform"""
    
    def __init__(self, metadata_file, moderator_username=None):
        """
        Initialisiert den Importer
        
        Args:
            metadata_file (str): Pfad zur metadata.json-Datei
            moderator_username (str, optional): Benutzername des Moderators, der die Profile verwalten soll
        """
        self.metadata_file = metadata_file
        self.metadata = self._load_metadata()
        self.moderator = None
        
        if moderator_username:
            try:
                self.moderator = User.objects.get(username=moderator_username, is_staff=True)
                print(f"Moderator gefunden: {self.moderator.username}")
            except User.DoesNotExist:
                print(f"Warnung: Moderator '{moderator_username}' nicht gefunden oder kein Staff-Mitglied")
    
    def _load_metadata(self):
        """Lädt die Metadaten aus der JSON-Datei"""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Fehler beim Laden der Metadaten: {e}")
            return {}
    
    def _generate_username(self, profile_info):
        """Generiert einen eindeutigen Benutzernamen basierend auf den Profilinformationen"""
        base_username = profile_info.get("username", "user")
        
        # Entferne Sonderzeichen und Leerzeichen
        base_username = ''.join(c for c in base_username if c.isalnum() or c == '_').lower()
        
        # Stelle sicher, dass der Benutzername mindestens 3 Zeichen lang ist
        if len(base_username) < 3:
            base_username = f"user_{random.randint(1000, 9999)}"
        
        # Prüfe, ob der Benutzername bereits existiert
        if User.objects.filter(username=base_username).exists():
            # Füge eine Zufallszahl hinzu
            base_username = f"{base_username}_{random.randint(1000, 9999)}"
            
            # Prüfe erneut
            if User.objects.filter(username=base_username).exists():
                base_username = f"user_{random.randint(10000, 99999)}"
        
        return base_username
    
    def _generate_email(self, username):
        """Generiert eine E-Mail-Adresse für den Benutzer"""
        domains = ["example.com", "fakemail.org", "testuser.net"]
        return f"{username}@{random.choice(domains)}"
    
    def _generate_birth_date(self, age):
        """Generiert ein Geburtsdatum basierend auf dem Alter"""
        if not age or age < 18:
            # Standardalter zwischen 25 und 45
            age = random.randint(25, 45)
        
        today = timezone.now().date()
        birth_date = today - timedelta(days=age*365 + random.randint(-180, 180))  # Ungefähres Alter mit Streuung
        return birth_date
    
    def _determine_gender(self, profile_info):
        """Bestimmt das Geschlecht basierend auf den Profilinformationen"""
        gender_text = profile_info.get("gender", "").lower()
        
        if "männlich" in gender_text or "male" in gender_text:
            return GenderChoices.MALE
        elif "weiblich" in gender_text or "female" in gender_text:
            return GenderChoices.FEMALE
        else:
            # Wenn das Geschlecht nicht bestimmt werden kann, verwende den Ordnernamen
            if any(path.startswith("downloaded_profiles/male/") for path in profile_info.get("local_images", [])):
                return GenderChoices.MALE
            elif any(path.startswith("downloaded_profiles/female/") for path in profile_info.get("local_images", [])):
                return GenderChoices.FEMALE
            else:
                # Zufällige Auswahl als Fallback
                return random.choice([GenderChoices.MALE, GenderChoices.FEMALE])
    
    def _determine_seeking(self, gender):
        """Bestimmt die gesuchte Geschlechtergruppe basierend auf dem eigenen Geschlecht"""
        # Standardmäßig das andere Geschlecht suchen
        if gender == GenderChoices.MALE:
            return GenderChoices.FEMALE
        else:
            return GenderChoices.MALE
    
    def import_profile(self, profile_id):
        """
        Importiert ein einzelnes Profil in die Dating-Plattform
        
        Args:
            profile_id (str): ID des Profils in den Metadaten
            
        Returns:
            tuple: (Erfolg (bool), Benutzer-Objekt oder None, Anzahl importierter Bilder)
        """
        if profile_id not in self.metadata:
            print(f"Profil '{profile_id}' nicht in Metadaten gefunden")
            return False, None, 0
        
        profile_info = self.metadata[profile_id]
        
        # Prüfe, ob Bilder vorhanden sind
        local_images = profile_info.get("local_images", [])
        if not local_images:
            print(f"Keine Bilder für Profil '{profile_id}' gefunden")
            return False, None, 0
        
        # Generiere Benutzerdaten
        username = self._generate_username(profile_info)
        email = self._generate_email(username)
        gender = self._determine_gender(profile_info)
        seeking = self._determine_seeking(gender)
        
        # Erstelle Fake-Benutzer
        try:
            user = User.objects.create(
                username=username,
                email=email,
                is_fake=True,  # Markiere als Fake-Profil
                gender=gender,
                seeking=seeking,
                birth_date=self._generate_birth_date(profile_info.get("age")),
                city=profile_info.get("location", "").split(",")[0].strip() if profile_info.get("location") else None,
                country=profile_info.get("location", "").split(",")[-1].strip() if profile_info.get("location") and "," in profile_info.get("location") else None,
                about_me=profile_info.get("description"),
                assigned_moderator=self.moderator
            )
            
            # Setze ein zufälliges Passwort
            user.set_password(f"fake_{random.randint(10000, 99999)}")
            user.save()
            
            print(f"Benutzer '{username}' erstellt (ID: {user.id}, Geschlecht: {gender})")
            
            # Importiere Bilder
            imported_images = 0
            for img_path in local_images:
                if self._import_image(user, img_path):
                    imported_images += 1
            
            print(f"{imported_images} Bilder für '{username}' importiert")
            return True, user, imported_images
            
        except Exception as e:
            print(f"Fehler beim Erstellen des Benutzers '{username}': {e}")
            return False, None, 0
    
    def _import_image(self, user, image_path):
        """
        Importiert ein Bild für einen Benutzer
        
        Args:
            user: Benutzer-Objekt
            image_path (str): Pfad zum Bild
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            # Prüfe, ob die Datei existiert
            if not os.path.exists(image_path):
                print(f"Bild nicht gefunden: {image_path}")
                return False
            
            # Erstelle UserProfileImage
            with open(image_path, 'rb') as img_file:
                image = UserProfileImage(
                    user=user,
                    is_approved=True  # Automatisch genehmigen
                )
                image.image.save(
                    os.path.basename(image_path),
                    ImageFile(img_file),
                    save=True
                )
            
            return True
            
        except Exception as e:
            print(f"Fehler beim Importieren des Bildes {image_path}: {e}")
            return False
    
    def import_all_profiles(self, gender_filter=None, max_profiles=None):
        """
        Importiert alle Profile aus den Metadaten
        
        Args:
            gender_filter (str, optional): Filter nach Geschlecht ('male', 'female', None für alle)
            max_profiles (int, optional): Maximale Anzahl zu importierender Profile
            
        Returns:
            tuple: (Anzahl erfolgreicher Importe, Anzahl fehlgeschlagener Importe)
        """
        success_count = 0
        failure_count = 0
        total_images = 0
        
        # Filtere Profile nach Geschlecht, falls angegeben
        profile_ids = list(self.metadata.keys())
        if gender_filter:
            filtered_ids = []
            for profile_id in profile_ids:
                profile_info = self.metadata[profile_id]
                gender_text = profile_info.get("gender", "").lower()
                
                if gender_filter == "male" and ("männlich" in gender_text or "male" in gender_text):
                    filtered_ids.append(profile_id)
                elif gender_filter == "female" and ("weiblich" in gender_text or "female" in gender_text):
                    filtered_ids.append(profile_id)
                elif gender_filter == "male" and any(path.startswith("downloaded_profiles/male/") for path in profile_info.get("local_images", [])):
                    filtered_ids.append(profile_id)
                elif gender_filter == "female" and any(path.startswith("downloaded_profiles/female/") for path in profile_info.get("local_images", [])):
                    filtered_ids.append(profile_id)
            
            profile_ids = filtered_ids
        
        # Begrenze die Anzahl der Profile, falls angegeben
        if max_profiles and max_profiles > 0:
            profile_ids = profile_ids[:max_profiles]
        
        print(f"Importiere {len(profile_ids)} Profile...")
        
        for profile_id in profile_ids:
            success, user, image_count = self.import_profile(profile_id)
            
            if success:
                success_count += 1
                total_images += image_count
            else:
                failure_count += 1
        
        print(f"\nImport abgeschlossen:")
        print(f"- {success_count} Profile erfolgreich importiert")
        print(f"- {failure_count} Profile fehlgeschlagen")
        print(f"- {total_images} Bilder insgesamt importiert")
        
        return success_count, failure_count


def parse_arguments():
    """Parst Kommandozeilenargumente"""
    parser = argparse.ArgumentParser(description="Profil-Importer für Dating-Plattform")
    
    parser.add_argument("metadata", help="Pfad zur metadata.json-Datei")
    parser.add_argument("-m", "--moderator", help="Benutzername des Moderators für die Fake-Profile")
    parser.add_argument("-g", "--gender", choices=["male", "female"], help="Nur Profile eines bestimmten Geschlechts importieren")
    parser.add_argument("-n", "--number", type=int, help="Maximale Anzahl zu importierender Profile")
    
    return parser.parse_args()


if __name__ == "__main__":
    # Prüfe, ob Django-Umgebung korrekt eingerichtet ist
    try:
        from django.conf import settings
        if not settings.configured:
            print("Fehler: Django-Einstellungen nicht konfiguriert")
            sys.exit(1)
    except ImportError:
        print("Fehler: Django nicht installiert oder nicht im Python-Pfad")
        sys.exit(1)
    
    args = parse_arguments()
    
    # Prüfe, ob die Metadaten-Datei existiert
    if not os.path.exists(args.metadata):
        print(f"Fehler: Metadaten-Datei '{args.metadata}' nicht gefunden")
        sys.exit(1)
    
    print("Profil-Importer für Dating-Plattform")
    print("===================================")
    print(f"Metadaten: {args.metadata}")
    print(f"Moderator: {args.moderator or 'Keiner'}")
    print(f"Geschlechtsfilter: {args.gender or 'Keiner'}")
    print(f"Max. Profile: {args.number or 'Alle'}")
    print("===================================")
    
    # Starte den Import
    importer = ProfileImporter(args.metadata, args.moderator)
    importer.import_all_profiles(args.gender, args.number)
