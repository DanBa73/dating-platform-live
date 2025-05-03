# Dating-Profil Downloader und Importer

Dieses Projekt enthält Tools zum Herunterladen von Profilbildern von Dating-Websites und zum Importieren dieser Bilder in Ihre eigene Dating-Plattform.

## Übersicht

Das Projekt besteht aus drei Hauptkomponenten:

1. **profile_downloader.py**: Ein allgemeiner Downloader für Profilbilder von Dating-Websites
2. **website_specific_downloader.py**: Ein Beispiel für die Anpassung des Downloaders an eine bestimmte Website
3. **import_profiles.py**: Ein Tool zum Importieren der heruntergeladenen Profile in Ihre Django-basierte Dating-Plattform

## Voraussetzungen

### Für den Downloader:
- Python 3.6+
- requests
- beautifulsoup4
- Optional: selenium (für JavaScript-basierte Websites)

### Für den Importer:
- Django-Projekt mit den entsprechenden Modellen (CustomUser, UserProfileImage)
- Zugriff auf die Django-Datenbank

## Installation

1. Installieren Sie die erforderlichen Python-Pakete:

```bash
pip install requests beautifulsoup4
pip install selenium  # Optional, aber empfohlen
```

2. Wenn Sie Selenium verwenden möchten, installieren Sie auch den entsprechenden WebDriver:
   - [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) für Chrome
   - [GeckoDriver](https://github.com/mozilla/geckodriver/releases) für Firefox

## Verwendung des Downloaders

### Allgemeiner Downloader

Der allgemeine Downloader kann direkt von der Kommandozeile aus verwendet werden:

```bash
python profile_downloader.py https://example-dating-site.com --selenium --delay 2 --max 50
```

Parameter:
- `url`: Die Basis-URL der Dating-Website
- `--output` / `-o`: Ausgabeverzeichnis für heruntergeladene Bilder (Standard: "downloaded_profiles")
- `--delay` / `-d`: Verzögerung zwischen Anfragen in Sekunden (Standard: 1.0)
- `--max` / `-m`: Maximale Anzahl an Profilen zum Herunterladen (Standard: 100)
- `--search` / `-s`: URL der Suchseite (optional)
- `--selenium`: Verwende Selenium für JavaScript-Rendering
- `--username` / `-u`: Benutzername für Login (optional)
- `--password` / `-p`: Passwort für Login (optional)

### Website-spezifischer Downloader

Für die meisten Dating-Websites müssen Sie den Downloader anpassen, da jede Website eine andere Struktur hat. Das Beispiel `website_specific_downloader.py` zeigt, wie Sie den allgemeinen Downloader für eine bestimmte Website anpassen können.

Um den Website-spezifischen Downloader zu verwenden:

```bash
python website_specific_downloader.py
```

#### Anpassung an eine spezifische Website

Um den Downloader an eine bestimmte Website anzupassen, müssen Sie folgende Methoden überschreiben:

1. **login**: Anpassung der Login-Logik
2. **get_profile_urls**: Anpassung der Methode zum Extrahieren von Profil-URLs
3. **extract_profile_info**: Anpassung der Methode zum Extrahieren von Profilinformationen

Die wichtigsten Anpassungen betreffen die CSS-Selektoren, die verwendet werden, um Elemente auf der Website zu finden. Hier sind einige Beispiele für häufige Selektoren:

- Profilkarten: `.profile-card`, `.user-card`, `.member-item`
- Profillinks: `a.profile-link`, `.profile-card a`, `.user-card a`
- Profilname: `.profile-name`, `.username`, `.user-info h2`
- Profilalter: `.profile-age`, `.age`, `.user-info .age`
- Profilgeschlecht: `.profile-gender`, `.gender`, `.user-info .gender`
- Profilort: `.profile-location`, `.location`, `.user-info .location`
- Profilbeschreibung: `.profile-description`, `.about-me`, `.user-info .description`
- Bildergalerie: `.profile-gallery`, `.photo-gallery`, `.user-photos`
- Bilder: `.profile-gallery img`, `.photo-gallery img`, `.user-photos img`

### Tipps für effektives Web-Scraping

1. **Respektieren Sie die robots.txt**: Prüfen Sie, ob die Website das Scraping erlaubt
2. **Verwenden Sie angemessene Verzögerungen**: Setzen Sie den `delay`-Parameter auf mindestens 1-2 Sekunden
3. **Rotieren Sie User-Agents**: Der Downloader tut dies bereits automatisch
4. **Verwenden Sie Selenium für moderne Websites**: Viele Dating-Websites verwenden JavaScript, was Selenium erfordert
5. **Begrenzen Sie die Anzahl der Profile**: Setzen Sie den `max_profiles`-Parameter auf einen vernünftigen Wert
6. **Vermeiden Sie IP-Sperren**: Verwenden Sie VPNs oder Proxies, wenn Sie viele Profile herunterladen

## Verwendung des Importers

Der Importer wird verwendet, um die heruntergeladenen Profile in Ihre Django-basierte Dating-Plattform zu importieren:

```bash
python import_profiles.py downloaded_profiles/metadata.json --moderator admin_username --gender female --number 20
```

Parameter:
- `metadata`: Pfad zur metadata.json-Datei (wird vom Downloader erstellt)
- `--moderator` / `-m`: Benutzername des Moderators für die Fake-Profile
- `--gender` / `-g`: Nur Profile eines bestimmten Geschlechts importieren ("male" oder "female")
- `--number` / `-n`: Maximale Anzahl zu importierender Profile

### Anpassung des Importers

Der Importer ist für die Django-Modelle in diesem Projekt konfiguriert. Wenn Ihre Modelle anders sind, müssen Sie den Importer anpassen:

1. Ändern Sie die Modellimporte am Anfang der Datei
2. Passen Sie die `import_profile`-Methode an, um die richtigen Felder zu setzen
3. Passen Sie die `_import_image`-Methode an, um Bilder korrekt zu importieren

## Ordnerstruktur

Nach dem Herunterladen werden die Bilder in folgender Struktur gespeichert:

```
downloaded_profiles/
├── metadata.json
├── male/
│   ├── username1/
│   │   ├── username1_1.jpg
│   │   ├── username1_2.jpg
│   │   └── ...
│   └── ...
├── female/
│   ├── username2/
│   │   ├── username2_1.jpg
│   │   ├── username2_2.jpg
│   │   └── ...
│   └── ...
└── other/
    └── ...
```

Die `metadata.json`-Datei enthält alle Informationen zu den heruntergeladenen Profilen, einschließlich der lokalen Bildpfade.

## Rechtliche Hinweise

Bitte beachten Sie, dass das Scraping von Websites rechtliche Einschränkungen haben kann:

1. Prüfen Sie die Nutzungsbedingungen der Website, bevor Sie den Downloader verwenden
2. Respektieren Sie die Privatsphäre der Benutzer
3. Verwenden Sie die heruntergeladenen Bilder nur für legitime Zwecke
4. Stellen Sie sicher, dass die Verwendung von Fake-Profilen in Ihrer Dating-Plattform legal ist und den Nutzungsbedingungen entspricht

## Fehlerbehebung

### Der Downloader findet keine Profile

- Prüfen Sie die CSS-Selektoren in der `get_profile_urls`-Methode
- Verwenden Sie den Browser-Inspektor, um die richtigen Selektoren zu finden
- Aktivieren Sie Selenium mit `--selenium`, falls die Website JavaScript verwendet

### Der Downloader kann nicht auf Profilseiten zugreifen

- Prüfen Sie, ob die Website einen Login erfordert
- Verwenden Sie die `--username` und `--password`-Parameter
- Passen Sie die `login`-Methode an, um den Login-Prozess zu unterstützen

### Der Downloader findet keine Bilder

- Prüfen Sie die CSS-Selektoren in der `extract_profile_info`-Methode
- Verwenden Sie den Browser-Inspektor, um die richtigen Selektoren zu finden
- Prüfen Sie, ob die Bilder dynamisch geladen werden (erfordert Selenium)

### Der Importer kann keine Profile erstellen

- Prüfen Sie, ob die Django-Umgebung korrekt eingerichtet ist
- Prüfen Sie, ob die Modelle mit den erwarteten Feldern übereinstimmen
- Prüfen Sie die Berechtigungen für den Dateizugriff

## Beispiel für die Anpassung an eine spezifische Website

Hier ist ein Beispiel, wie Sie den Downloader an eine spezifische Website anpassen können:

1. Kopieren Sie `website_specific_downloader.py` und benennen Sie es um (z.B. `tinder_downloader.py`)
2. Ändern Sie die Basis-URL und die CSS-Selektoren
3. Passen Sie die Login-Logik an, falls erforderlich
4. Führen Sie das Skript aus und überwachen Sie die Ausgabe auf Fehler
5. Passen Sie die Selektoren weiter an, bis der Downloader funktioniert

## Beispiel für den Import in Ihre Dating-Plattform

1. Stellen Sie sicher, dass Ihre Django-Umgebung korrekt eingerichtet ist
2. Führen Sie den Importer mit dem Pfad zur metadata.json-Datei aus
3. Überwachen Sie die Ausgabe auf Fehler
4. Prüfen Sie die importierten Profile in Ihrer Django-Admin-Oberfläche
