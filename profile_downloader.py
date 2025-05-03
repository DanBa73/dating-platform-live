#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dating-Profil Bilder Downloader

Dieses Skript ermöglicht das automatisierte Herunterladen von Profilbildern von Dating-Websites.
Die Bilder werden in einer strukturierten Ordnerstruktur gespeichert und mit Metadaten versehen.
"""

import os
import re
import json
import time
import random
import argparse
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Versuche, optionale Abhängigkeiten zu importieren
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class DatingProfileDownloader:
    """Hauptklasse zum Herunterladen von Dating-Profilbildern"""
    
    def __init__(self, base_url, output_dir="downloaded_profiles", 
                 delay=1, max_profiles=100, use_selenium=False,
                 username=None, password=None):
        """
        Initialisiert den Downloader
        
        Args:
            base_url (str): Die Basis-URL der Dating-Website
            output_dir (str): Verzeichnis zum Speichern der heruntergeladenen Bilder
            delay (float): Verzögerung zwischen Anfragen in Sekunden
            max_profiles (int): Maximale Anzahl an Profilen zum Herunterladen
            use_selenium (bool): Ob Selenium für JavaScript-Rendering verwendet werden soll
            username (str, optional): Benutzername für Login
            password (str, optional): Passwort für Login
        """
        self.base_url = base_url
        self.output_dir = output_dir
        self.delay = delay
        self.max_profiles = max_profiles
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.driver = None
        self.metadata = {}
        
        # Erstelle Ausgabeverzeichnis, falls es nicht existiert
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Erstelle Unterverzeichnisse für verschiedene Kategorien
        self.male_dir = os.path.join(output_dir, "male")
        self.female_dir = os.path.join(output_dir, "female")
        self.other_dir = os.path.join(output_dir, "other")
        
        for directory in [self.male_dir, self.female_dir, self.other_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                
        # Lade bestehende Metadaten, falls vorhanden
        self.metadata_file = os.path.join(output_dir, "metadata.json")
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except json.JSONDecodeError:
                print("Warnung: Metadaten-Datei beschädigt, erstelle neue Datei")
                self.metadata = {}
        
        # User-Agent rotieren
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        
        # Setze zufälligen User-Agent
        self.session.headers.update({
            "User-Agent": random.choice(self.user_agents)
        })
    
    def setup_selenium(self):
        """Initialisiert den Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            print("Selenium ist nicht installiert. Bitte installieren Sie es mit 'pip install selenium'")
            return False
            
        try:
            options = Options()
            options.add_argument("--headless")  # Headless-Modus (kein Browser-Fenster)
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"user-agent={random.choice(self.user_agents)}")
            
            self.driver = webdriver.Chrome(options=options)
            return True
        except Exception as e:
            print(f"Fehler beim Initialisieren von Selenium: {e}")
            return False
    
    def login(self):
        """Führt den Login auf der Website durch"""
        if not self.username or not self.password:
            print("Kein Login erforderlich oder Anmeldedaten fehlen")
            return False
            
        # Hier müssen Sie die Login-Logik für Ihre spezifische Website implementieren
        # Dies ist ein Beispiel und muss angepasst werden
        
        if self.use_selenium and self.driver:
            try:
                self.driver.get(urljoin(self.base_url, "/login"))
                
                # Warten auf Login-Formular
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                
                # Login-Daten eingeben
                self.driver.find_element(By.ID, "username").send_keys(self.username)
                self.driver.find_element(By.ID, "password").send_keys(self.password)
                self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                
                # Warten auf erfolgreichen Login
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".logged-in-indicator"))
                )
                
                print("Login erfolgreich (Selenium)")
                return True
            except Exception as e:
                print(f"Login fehlgeschlagen (Selenium): {e}")
                return False
        else:
            try:
                login_url = urljoin(self.base_url, "/login")
                response = self.session.get(login_url)
                
                # CSRF-Token extrahieren (falls erforderlich)
                soup = BeautifulSoup(response.text, 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrf_token'})
                
                login_data = {
                    'username': self.username,
                    'password': self.password
                }
                
                if csrf_token:
                    login_data['csrf_token'] = csrf_token.get('value', '')
                
                login_response = self.session.post(login_url, data=login_data)
                
                if login_response.status_code == 200 and "Logout" in login_response.text:
                    print("Login erfolgreich (Requests)")
                    return True
                else:
                    print("Login fehlgeschlagen (Requests)")
                    return False
            except Exception as e:
                print(f"Login fehlgeschlagen (Requests): {e}")
                return False
    
    def get_profile_urls(self, search_url=None):
        """
        Extrahiert URLs zu Benutzerprofilen von der Suchseite
        
        Args:
            search_url (str, optional): URL der Suchseite, falls nicht angegeben wird die Basis-URL verwendet
            
        Returns:
            list: Liste von Profil-URLs
        """
        if search_url is None:
            search_url = urljoin(self.base_url, "/search")
            
        profile_urls = []
        
        if self.use_selenium and self.driver:
            try:
                self.driver.get(search_url)
                
                # Warten auf das Laden der Suchergebnisse
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".profile-card"))
                )
                
                # Scrolle, um mehr Profile zu laden (für Infinite-Scroll-Seiten)
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                
                while len(profile_urls) < self.max_profiles:
                    # Scrolle zum Ende der Seite
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    
                    # Warte auf das Laden neuer Inhalte
                    time.sleep(2)
                    
                    # Berechne neue Scrollhöhe und vergleiche mit der letzten Scrollhöhe
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        # Wenn keine neuen Inhalte geladen wurden, breche die Schleife ab
                        break
                    last_height = new_height
                    
                    # Extrahiere Profil-Links
                    profile_elements = self.driver.find_elements(By.CSS_SELECTOR, ".profile-card a")
                    for element in profile_elements:
                        href = element.get_attribute("href")
                        if href and "/profile/" in href and href not in profile_urls:
                            profile_urls.append(href)
                            
                            if len(profile_urls) >= self.max_profiles:
                                break
                
            except Exception as e:
                print(f"Fehler beim Extrahieren von Profil-URLs (Selenium): {e}")
        else:
            try:
                response = self.session.get(search_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Anpassen an die spezifische Website-Struktur
                # Dies ist ein Beispiel und muss angepasst werden
                profile_links = soup.select(".profile-card a")
                
                for link in profile_links:
                    href = link.get("href")
                    if href and "/profile/" in href:
                        full_url = urljoin(self.base_url, href)
                        if full_url not in profile_urls:
                            profile_urls.append(full_url)
                            
                            if len(profile_urls) >= self.max_profiles:
                                break
                
            except Exception as e:
                print(f"Fehler beim Extrahieren von Profil-URLs (Requests): {e}")
        
        print(f"Gefundene Profil-URLs: {len(profile_urls)}")
        return profile_urls
    
    def extract_profile_info(self, profile_url):
        """
        Extrahiert Profilinformationen und Bild-URLs von einer Profilseite
        
        Args:
            profile_url (str): URL des Benutzerprofils
            
        Returns:
            dict: Profilinformationen und Bild-URLs
        """
        profile_info = {
            "url": profile_url,
            "username": None,
            "age": None,
            "gender": None,
            "location": None,
            "description": None,
            "image_urls": []
        }
        
        try:
            if self.use_selenium and self.driver:
                self.driver.get(profile_url)
                
                # Warten auf das Laden der Profilseite
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".profile-container"))
                )
                
                # Extrahiere Profilinformationen
                try:
                    profile_info["username"] = self.driver.find_element(By.CSS_SELECTOR, ".profile-username").text
                except: pass
                
                try:
                    age_text = self.driver.find_element(By.CSS_SELECTOR, ".profile-age").text
                    profile_info["age"] = int(re.search(r'\d+', age_text).group())
                except: pass
                
                try:
                    profile_info["gender"] = self.driver.find_element(By.CSS_SELECTOR, ".profile-gender").text
                except: pass
                
                try:
                    profile_info["location"] = self.driver.find_element(By.CSS_SELECTOR, ".profile-location").text
                except: pass
                
                try:
                    profile_info["description"] = self.driver.find_element(By.CSS_SELECTOR, ".profile-description").text
                except: pass
                
                # Extrahiere Bild-URLs
                image_elements = self.driver.find_elements(By.CSS_SELECTOR, ".profile-gallery img")
                for img in image_elements:
                    src = img.get_attribute("src")
                    if src:
                        # Prüfe auf hochauflösende Versionen
                        data_hd = img.get_attribute("data-hd-src")
                        if data_hd:
                            profile_info["image_urls"].append(data_hd)
                        else:
                            profile_info["image_urls"].append(src)
                
            else:
                response = self.session.get(profile_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extrahiere Profilinformationen
                username_elem = soup.select_one(".profile-username")
                if username_elem:
                    profile_info["username"] = username_elem.text.strip()
                
                age_elem = soup.select_one(".profile-age")
                if age_elem:
                    age_match = re.search(r'\d+', age_elem.text)
                    if age_match:
                        profile_info["age"] = int(age_match.group())
                
                gender_elem = soup.select_one(".profile-gender")
                if gender_elem:
                    profile_info["gender"] = gender_elem.text.strip()
                
                location_elem = soup.select_one(".profile-location")
                if location_elem:
                    profile_info["location"] = location_elem.text.strip()
                
                description_elem = soup.select_one(".profile-description")
                if description_elem:
                    profile_info["description"] = description_elem.text.strip()
                
                # Extrahiere Bild-URLs
                for img in soup.select(".profile-gallery img"):
                    src = img.get("src")
                    if src:
                        # Prüfe auf hochauflösende Versionen
                        data_hd = img.get("data-hd-src")
                        if data_hd:
                            profile_info["image_urls"].append(data_hd)
                        else:
                            profile_info["image_urls"].append(src)
            
        except Exception as e:
            print(f"Fehler beim Extrahieren von Profilinformationen für {profile_url}: {e}")
        
        return profile_info
    
    def download_image(self, image_url, save_path):
        """
        Lädt ein Bild herunter und speichert es
        
        Args:
            image_url (str): URL des Bildes
            save_path (str): Pfad zum Speichern des Bildes
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            # Füge zufällige Verzögerung hinzu, um Erkennung zu vermeiden
            time.sleep(self.delay * (0.5 + random.random()))
            
            # Setze zufälligen User-Agent
            headers = {"User-Agent": random.choice(self.user_agents)}
            
            response = requests.get(image_url, headers=headers, stream=True)
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return True
            else:
                print(f"Fehler beim Herunterladen von {image_url}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Fehler beim Herunterladen von {image_url}: {e}")
            return False
    
    def process_profile(self, profile_url):
        """
        Verarbeitet ein einzelnes Profil: Extrahiert Informationen und lädt Bilder herunter
        
        Args:
            profile_url (str): URL des Benutzerprofils
            
        Returns:
            dict: Profilinformationen mit lokalen Bildpfaden
        """
        profile_info = self.extract_profile_info(profile_url)
        
        if not profile_info["image_urls"]:
            print(f"Keine Bilder gefunden für {profile_url}")
            return None
        
        # Bestimme Zielverzeichnis basierend auf Geschlecht
        if profile_info["gender"] and "männlich" in profile_info["gender"].lower() or profile_info["gender"] == "MALE":
            target_dir = self.male_dir
        elif profile_info["gender"] and "weiblich" in profile_info["gender"].lower() or profile_info["gender"] == "FEMALE":
            target_dir = self.female_dir
        else:
            target_dir = self.other_dir
        
        # Erstelle Unterverzeichnis für dieses Profil
        profile_dirname = profile_info["username"] if profile_info["username"] else f"profile_{int(time.time())}"
        profile_dirname = re.sub(r'[^\w\-_]', '_', profile_dirname)  # Bereinige Verzeichnisnamen
        
        profile_dir = os.path.join(target_dir, profile_dirname)
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        
        # Lade Bilder herunter
        local_images = []
        for i, img_url in enumerate(profile_info["image_urls"]):
            # Extrahiere Dateiendung oder verwende .jpg als Standard
            parsed_url = urlparse(img_url)
            file_ext = os.path.splitext(parsed_url.path)[1]
            if not file_ext:
                file_ext = ".jpg"
            
            # Erstelle Dateinamen
            filename = f"{profile_dirname}_{i+1}{file_ext}"
            save_path = os.path.join(profile_dir, filename)
            
            if self.download_image(img_url, save_path):
                local_images.append(save_path)
                print(f"Bild heruntergeladen: {save_path}")
            
            # Füge Verzögerung hinzu
            time.sleep(self.delay)
        
        # Aktualisiere Profilinformationen mit lokalen Bildpfaden
        profile_info["local_images"] = local_images
        profile_info["download_date"] = datetime.now().isoformat()
        
        return profile_info
    
    def run(self, search_url=None):
        """
        Führt den gesamten Download-Prozess aus
        
        Args:
            search_url (str, optional): URL der Suchseite
            
        Returns:
            dict: Heruntergeladene Profilinformationen
        """
        if self.use_selenium and not self.driver:
            if not self.setup_selenium():
                print("Selenium konnte nicht initialisiert werden. Verwende Requests-Modus.")
                self.use_selenium = False
        
        # Login, falls Anmeldedaten vorhanden
        if self.username and self.password:
            self.login()
        
        # Hole Profil-URLs
        profile_urls = self.get_profile_urls(search_url)
        
        if not profile_urls:
            print("Keine Profile gefunden.")
            return {}
        
        # Verarbeite Profile
        downloaded_profiles = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            for i, profile_info in enumerate(executor.map(self.process_profile, profile_urls)):
                if profile_info:
                    profile_id = profile_info["username"] or f"profile_{i}"
                    downloaded_profiles[profile_id] = profile_info
                    
                    # Aktualisiere Metadaten
                    self.metadata[profile_id] = profile_info
                    
                    # Speichere Metadaten regelmäßig
                    if i % 10 == 0:
                        self.save_metadata()
                
                # Prüfe, ob maximale Anzahl erreicht wurde
                if len(downloaded_profiles) >= self.max_profiles:
                    break
        
        # Speichere endgültige Metadaten
        self.save_metadata()
        
        # Schließe Selenium-Treiber, falls verwendet
        if self.use_selenium and self.driver:
            self.driver.quit()
        
        print(f"Download abgeschlossen. {len(downloaded_profiles)} Profile heruntergeladen.")
        return downloaded_profiles
    
    def save_metadata(self):
        """Speichert die Metadaten in eine JSON-Datei"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Fehler beim Speichern der Metadaten: {e}")
            return False


def parse_arguments():
    """Parst Kommandozeilenargumente"""
    parser = argparse.ArgumentParser(description="Dating-Profil Bilder Downloader")
    
    parser.add_argument("url", help="Die Basis-URL der Dating-Website")
    parser.add_argument("-o", "--output", default="downloaded_profiles", help="Ausgabeverzeichnis für heruntergeladene Bilder")
    parser.add_argument("-d", "--delay", type=float, default=1.0, help="Verzögerung zwischen Anfragen in Sekunden")
    parser.add_argument("-m", "--max", type=int, default=100, help="Maximale Anzahl an Profilen zum Herunterladen")
    parser.add_argument("-s", "--search", help="URL der Suchseite (optional)")
    parser.add_argument("--selenium", action="store_true", help="Verwende Selenium für JavaScript-Rendering")
    parser.add_argument("-u", "--username", help="Benutzername für Login (optional)")
    parser.add_argument("-p", "--password", help="Passwort für Login (optional)")
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    print("Dating-Profil Bilder Downloader")
    print("==============================")
    print(f"Ziel-Website: {args.url}")
    print(f"Ausgabeverzeichnis: {args.output}")
    print(f"Verzögerung: {args.delay} Sekunden")
    print(f"Max. Profile: {args.max}")
    print(f"Selenium: {'Ja' if args.selenium else 'Nein'}")
    print(f"Login: {'Ja' if args.username and args.password else 'Nein'}")
    print("==============================")
    
    downloader = DatingProfileDownloader(
        base_url=args.url,
        output_dir=args.output,
        delay=args.delay,
        max_profiles=args.max,
        use_selenium=args.selenium,
        username=args.username,
        password=args.password
    )
    
    downloader.run(args.search)
