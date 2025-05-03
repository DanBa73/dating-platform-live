# accounts/management/commands/seed_fake_users.py (Letzter Versuch: 2 Saves)

# Schritt 1: Imports
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
# Spezifischere Exceptions importieren
from django.db import IntegrityError, DataError
from django.core.exceptions import ValidationError
# Passe diesen Import ggf. an
from accounts.models import CustomUser

# Schritt 2: Klassendefinition
class Command(BaseCommand):
    help = 'Seeds the database with 30 fake female users located in Berlin.'

    # Schritt 3: handle-Methode
    def handle(self, *args, **options):
        # Schritt 4: Variablen definieren und Startmeldung
        User = get_user_model()
        num_users_to_create = 30
        password = "password123"
        state = "Berlin"
        city = "Berlin"
        gender = "female"
        seeking_options = ['male']
        created_count = 0
        skipped_count = 0

        self.stdout.write(f"Starting to seed {num_users_to_create} fake female users in Berlin...")

        # Schritt 5: Schleife und User erstellen (Logik: 2 Saves)
        for i in range(num_users_to_create):
            username = f"FakeBerlinerin_{i+1}"
            while User.objects.filter(username=username).exists():
                username = f"FakeBerlinerin_{i+1}_{random.randint(100, 999)}"

            today = date.today()
            days_in_18_years = 18 * 365 + 4
            days_in_55_years = 55 * 365 + 14
            try:
                start_date = today - timedelta(days=days_in_55_years)
                end_date = today - timedelta(days=days_in_18_years)
                if start_date > end_date: start_date = end_date - timedelta(days=1)
                total_days_diff = (end_date - start_date).days
                random_days = random.randint(0, total_days_diff if total_days_diff >=0 else 0)
                birth_date = start_date + timedelta(days=random_days)
            except ValueError:
                 birth_date = today - timedelta(days=30*365)

            about_me = f"Hallo, ich bin eine nette Frau aus Berlin und suche nette Gespräche."

            # ERSTELLUNGS-LOGIK: Mit zwei Saves
            try:
                # 1. Basis-User erstellen
                user = User.objects.create_user(
                    username=username,
                    password=password
                )

                # 2. *Andere* zusätzliche Felder setzen
                user.is_fake = True
                user.state = state
                user.city = city
                user.birth_date = birth_date
                user.about_me = about_me
                user.is_active = True
                user.is_staff = False
                user.is_superuser = False
                # gender & seeking hier noch NICHT setzen

                # 3. Erster Save (ohne gender/seeking)
                fields_to_update_1 = [
                    'is_fake', 'state', 'city', 'birth_date',
                    'about_me', 'is_active', 'is_staff', 'is_superuser'
                    ]
                self.stdout.write(f"DEBUG: Calling save() #1 for {user.username}")
                user.save(update_fields=fields_to_update_1)
                self.stdout.write(f"DEBUG: save() #1 finished for {user.username}")

                # 4. Gender und Seeking setzen
                user.gender = gender
                user.seeking = seeking # Direkt 'male' setzen oder random.choice? Nehmen wir 'male'
                # user.seeking = random.choice(seeking_options) # falls mehr optionen

                self.stdout.write(f"DEBUG: Values set before save() #2: Gender='{user.gender}', Seeking='{user.seeking}'")

                # 5. Zweiter Save (NUR gender/seeking)
                self.stdout.write(f"DEBUG: Calling save() #2 for {user.username}")
                user.save(update_fields=['gender', 'seeking'])
                self.stdout.write(f"DEBUG: save() #2 finished for {user.username}")

                # Debugging nach dem ZWEITEN Speichern
                user.refresh_from_db()
                self.stdout.write(f"DEBUG: User {user.username} attrs AFTER SECOND SAVE & REFRESH: {user.__dict__}")

                created_count += 1

            # Spezifischere Fehler abfangen
            except IntegrityError as e:
                 skipped_count += 1
                 self.stdout.write(self.style.ERROR(f"IntegrityError creating user {username}: {e}"))
            except ValidationError as e:
                 skipped_count += 1
                 self.stdout.write(self.style.ERROR(f"ValidationError creating user {username}: {e}"))
            except DataError as e:
                 skipped_count += 1
                 self.stdout.write(self.style.ERROR(f"DataError creating user {username}: {e}"))
            except Exception as e:
                 skipped_count += 1
                 self.stdout.write(self.style.ERROR(f"Unexpected {type(e).__name__} creating user {username}: {e}"))

        # Schritt 6: Endmeldung
        self.stdout.write(self.style.SUCCESS(f"Finished seeding. {created_count} users created, {skipped_count} skipped."))