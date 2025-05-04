# Migration von PostgreSQL zu MariaDB/MySQL

Diese Anleitung beschreibt die Schritte, die notwendig sind, um das Django-Backend von PostgreSQL auf MariaDB/MySQL umzustellen, damit es auf einem Strato V-Server mit Plesk Web Admin Edition läuft.

## Vorgenommene Änderungen

Ich habe folgende Änderungen am Code vorgenommen:

1. **requirements.txt**: 
   - PostgreSQL-Treiber (psycopg2-binary) auskommentiert
   - MySQL-Treiber (mysqlclient) hinzugefügt

2. **config/settings.py**:
   - Datenbankeinstellungen von PostgreSQL auf MariaDB/MySQL umgestellt
   - Standard-Benutzer von 'postgres' auf 'root' geändert
   - Standard-Port von '5432' auf '3306' geändert
   - OPTIONS für Zeichenkodierung (utf8mb4) und SQL-Modus (STRICT_TRANS_TABLES) hinzugefügt

## Einrichtung auf dem Server

### 1. Datenbank in Plesk erstellen

1. Melden Sie sich in Plesk an
2. Navigieren Sie zu "Datenbanken"
3. Klicken Sie auf "Datenbank hinzufügen"
4. Geben Sie einen Namen für die Datenbank ein (z.B. "dating_platform_db")
5. Erstellen Sie einen Datenbankbenutzer und ein sicheres Passwort
6. Notieren Sie sich diese Informationen für den nächsten Schritt

### 2. Umgebungsvariablen einrichten

Erstellen oder aktualisieren Sie die `.env`-Datei im Projektverzeichnis mit den folgenden Einstellungen:

```
SECRET_KEY=IhrGeheimSchlüssel
DEBUG=False
DATABASE_NAME=IhrDatenbankName
DATABASE_USER=IhrDatenbankBenutzer
DATABASE_PASSWORD=IhrDatenbankPasswort
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

Ersetzen Sie die Platzhalter durch Ihre tatsächlichen Werte.

### 3. Abhängigkeiten installieren

Installieren Sie die aktualisierten Abhängigkeiten:

```bash
pip install -r requirements.txt
```

### 4. Datenbank migrieren

Führen Sie die Django-Migrationen aus, um die Datenbankstruktur zu erstellen:

```bash
python manage.py migrate
```

### 5. Statische Dateien sammeln

Sammeln Sie die statischen Dateien für die Produktionsumgebung:

```bash
python manage.py collectstatic --noinput
```

### 6. Superuser erstellen

Erstellen Sie einen Admin-Benutzer für das Django-Admin-Interface:

```bash
python manage.py createsuperuser
```

## Mögliche Probleme und Lösungen

### 1. Zeichenkodierung

MariaDB/MySQL verwendet standardmäßig eine andere Zeichenkodierung als PostgreSQL. Wir haben die Einstellung `'charset': 'utf8mb4'` hinzugefügt, um vollständige UTF-8-Unterstützung (einschließlich Emojis) zu gewährleisten.

### 2. SQL-Modus

Der SQL-Modus `STRICT_TRANS_TABLES` wurde hinzugefügt, um ein ähnliches Verhalten wie PostgreSQL zu erreichen, das standardmäßig strenger ist als MySQL.

### 3. Migrationsprobleme

Wenn bei der Migration Probleme auftreten, kann es hilfreich sein, die Datenbank neu zu erstellen und die Migrationen von Grund auf neu auszuführen:

```bash
python manage.py migrate --fake zero
python manage.py migrate
```

### 4. Datenimport

Wenn Sie Daten aus der PostgreSQL-Datenbank in die neue MariaDB/MySQL-Datenbank importieren möchten, können Sie Django's dumpdata und loaddata verwenden:

```bash
# Auf dem alten System mit PostgreSQL
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data.json

# Auf dem neuen System mit MariaDB/MySQL
python manage.py loaddata data.json
```

## Überprüfung der Installation

Nach der Migration sollten Sie überprüfen, ob alle Funktionen wie erwartet funktionieren:

1. Melden Sie sich im Django-Admin-Interface an
2. Überprüfen Sie, ob alle Modelle korrekt angezeigt werden
3. Testen Sie die API-Endpunkte
4. Überprüfen Sie, ob das Frontend korrekt mit dem Backend kommuniziert

## Weitere Anpassungen

Je nach Ihren spezifischen Anforderungen können weitere Anpassungen notwendig sein. Wenn Sie auf Probleme stoßen, überprüfen Sie die Django-Dokumentation für MySQL-spezifische Einstellungen oder wenden Sie sich an mich für weitere Unterstützung.
