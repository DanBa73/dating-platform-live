# Git-Einrichtung für Ihr Dating-Plattform-Projekt

Diese Anleitung führt Sie durch die Einrichtung eines Git-Repositories für Ihr Projekt und erklärt, wie Sie Änderungen zwischen Ihrer lokalen Entwicklungsumgebung und dem Server synchronisieren können.

## 1. Lokales Git-Repository einrichten

Öffnen Sie eine Kommandozeile (CMD oder PowerShell) und navigieren Sie zu Ihrem Projektverzeichnis:

```bash
cd c:/GEMINI-Project/dating-platform
```

Initialisieren Sie ein neues Git-Repository:

```bash
git init
```

## 2. Dateien zum Repository hinzufügen

Ich habe bereits eine `.gitignore`-Datei erstellt, die bestimmt, welche Dateien nicht in das Repository aufgenommen werden sollen (z.B. temporäre Dateien, Bilder, Datenbanken).

Fügen Sie alle Projektdateien zum Repository hinzu:

```bash
git add .
```

Erstellen Sie den ersten Commit:

```bash
git commit -m "Initialer Commit"
```

## 3. Remote-Repository einrichten

Sie haben mehrere Optionen für Remote-Repositories:

### Option A: GitHub/GitLab/Bitbucket

1. Erstellen Sie ein Konto bei [GitHub](https://github.com/), [GitLab](https://gitlab.com/) oder [Bitbucket](https://bitbucket.org/)
2. Erstellen Sie ein neues Repository (z.B. "dating-platform")
3. Folgen Sie den Anweisungen auf der Website, um Ihr lokales Repository mit dem Remote-Repository zu verbinden:

```bash
git remote add origin https://github.com/IhrBenutzername/dating-platform.git
git branch -M main
git push -u origin main
```

### Option B: Eigener Git-Server

Wenn Sie einen eigenen Server haben und dort Git installiert ist:

```bash
git remote add origin benutzer@ihr-server.de:/pfad/zum/repository.git
git push -u origin main
```

## 4. Git auf dem Server einrichten

### Wenn Sie GitHub/GitLab/Bitbucket verwenden:

1. Installieren Sie Git auf Ihrem Server:
   ```bash
   sudo apt-get update
   sudo apt-get install git
   ```

2. Klonen Sie das Repository auf Ihrem Server:
   ```bash
   git clone https://github.com/IhrBenutzername/dating-platform.git
   ```

### Wenn Sie einen eigenen Git-Server verwenden:

1. Erstellen Sie ein Bare-Repository auf Ihrem Server:
   ```bash
   mkdir -p /pfad/zum/repository.git
   cd /pfad/zum/repository.git
   git init --bare
   ```

2. Klonen Sie das Repository in Ihr Arbeitsverzeichnis:
   ```bash
   cd /pfad/zum/arbeitsverzeichnis
   git clone /pfad/zum/repository.git
   ```

## 5. Änderungen übertragen

### Lokale Änderungen zum Remote-Repository übertragen:

1. Änderungen hinzufügen:
   ```bash
   git add .
   ```

2. Änderungen committen:
   ```bash
   git commit -m "Beschreibung der Änderungen"
   ```

3. Änderungen pushen:
   ```bash
   git push
   ```

### Änderungen auf dem Server abrufen:

Navigieren Sie zum Projektverzeichnis auf dem Server und führen Sie aus:

```bash
git pull
```

## 6. Nützliche Git-Befehle

- `git status`: Zeigt den Status des Repositories an
- `git log`: Zeigt die Commit-Historie an
- `git diff`: Zeigt Änderungen zwischen Commits an
- `git checkout <datei>`: Verwirft Änderungen an einer Datei
- `git branch`: Zeigt alle Branches an
- `git checkout -b <branch-name>`: Erstellt einen neuen Branch und wechselt zu diesem
- `git merge <branch-name>`: Führt einen Branch mit dem aktuellen Branch zusammen

## 7. Automatisierte Deployment-Skripte (optional)

Sie können ein einfaches Deployment-Skript auf Ihrem Server erstellen, um nach einem Pull automatisch Aktionen auszuführen:

Erstellen Sie eine Datei `deploy.sh` im Projektverzeichnis:

```bash
#!/bin/bash
# Deployment-Skript für die Dating-Plattform

# Aktualisiere das Repository
git pull

# Führe weitere Aktionen aus (falls nötig)
# z.B. Django-Migrationen, statische Dateien sammeln, Server neustarten

# Django-Migrationen
python manage.py migrate

# Statische Dateien sammeln
python manage.py collectstatic --noinput

# Server neustarten (falls nötig)
# sudo systemctl restart gunicorn
# sudo systemctl restart nginx
```

Machen Sie das Skript ausführbar:

```bash
chmod +x deploy.sh
```

Jetzt können Sie das Deployment mit einem einfachen Befehl durchführen:

```bash
./deploy.sh
```

## 8. Git-Hooks für automatisches Deployment (fortgeschritten)

Für fortgeschrittene Benutzer: Sie können Git-Hooks verwenden, um automatisch nach jedem Push zu deployen.

Auf dem Server im Bare-Repository:

```bash
cd /pfad/zum/repository.git/hooks
nano post-receive
```

Fügen Sie folgenden Inhalt hinzu:

```bash
#!/bin/bash
GIT_WORK_TREE=/pfad/zum/arbeitsverzeichnis git checkout -f
cd /pfad/zum/arbeitsverzeichnis
./deploy.sh
```

Machen Sie den Hook ausführbar:

```bash
chmod +x post-receive
```

Jetzt wird nach jedem Push automatisch das Deployment ausgeführt.

## Zusammenfassung

Mit dieser Git-Einrichtung können Sie:

1. Änderungen lokal vornehmen und testen
2. Änderungen in das Remote-Repository pushen
3. Änderungen auf dem Server abrufen
4. Optional: Automatisches Deployment nach jedem Push

Diese Methode bietet eine saubere Versionskontrolle und vereinfacht die Übertragung von Änderungen erheblich.
