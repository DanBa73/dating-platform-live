#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Website-spezifischer Dating-Profil Downloader für Tabor.ru 
(Version 19 - Korrigierte "Mehr laden"-Logik)
"""

import os
import re
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementNotInteractableException, ElementClickInterceptedException

# Annahme: profile_downloader.py befindet sich im gleichen Verzeichnis
try:
    from profile_downloader import DatingProfileDownloader
except ImportError:
    print("FEHLER: Konnte 'profile_downloader.py' nicht finden.")
    print("Stelle sicher, dass diese Datei im gleichen Ordner wie dieses Skript liegt.")
    exit()

class ExampleSiteDownloader(DatingProfileDownloader):
    """Angepasster Downloader für Tabor.ru"""

    def __init__(self, output_dir="downloaded_profiles",
                 delay=2, max_profiles=50, use_selenium=True,
                 username=None, password=None):
        """ Initialisiert den angepassten Downloader """
        base_url = "https://tabor.ru/"
        super().__init__(
            base_url=base_url, output_dir=output_dir, delay=delay,
            max_profiles=max_profiles, use_selenium=use_selenium,
            username=username, password=password
        )

    def login(self):
        """ Überschriebene Login-Methode - Wird für Tabor erstmal übersprungen """
        if not self.username or not self.password:
            print(">>> Login wird übersprungen (Keine Anmeldedaten angegeben).")
            return True
        else:
            print(">>> Login wird übersprungen (Auch wenn Anmeldedaten angegeben).")
            return True

    def get_profile_urls(self, search_url=None):
        """ Überschriebene Methode zum Extrahieren von Profil-URLs von Tabor.ru """
        if search_url is None:
            search_url = "https://tabor.ru/search?search%5Bfind_sex%5D=2&search%5Bage%5D=18%3B70&search%5Bcountry_id%5D=3159&search%5Bphoto%5D=on"
            print(f"Verwende feste Such-URL: {search_url}")

        profile_urls = []
        processed_hrefs = set()

        if self.use_selenium and self.driver:
            try:
                print(f"Öffne Such-Seite: {search_url}")
                self.driver.get(search_url)
                time.sleep(self.delay)

                profile_card_selector = "a.comment"
                load_more_selector = "span.status__link-more"
                
                print(f"Warte auf erste Profilkarte/Link: {profile_card_selector}")
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, profile_card_selector))
                    )
                    time.sleep(1)
                except TimeoutException:
                     print("WARNUNG: Keine Profilkarten auf der initialen Seite gefunden.")
                     return [] 

                # --- KORRIGIERTE Schleife für "Mehr laden"-Knopf ---
                max_load_more_clicks = 50 # Sicherheitslimit
                click_count = 0
                print("Suche und klicke 'Mehr laden'-Knopf...")

                while click_count < max_load_more_clicks:
                    try:
                        # Zähle Karten *vor* dem Klick
                        card_count_before = len(self.driver.find_elements(By.CSS_SELECTOR, profile_card_selector))
                        print(f"  Aktuell sichtbar: {card_count_before} Profilkarten.")
                        
                        # Finde den "Mehr laden" Knopf (kurzer Timeout, da er schnell da sein sollte, wenn er existiert)
                        load_more_button = WebDriverWait(self.driver, 5).until( 
                            EC.element_to_be_clickable((By.CSS_SELECTOR, load_more_selector))
                        )
                        
                        print(f"  Klicke 'Mehr laden' (Versuch #{click_count + 1})...")
                        # Scrollt eventuell erst zum Button
                        try:
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                            time.sleep(0.5)
                            load_more_button.click()
                            click_count += 1
                        except Exception as click_err:
                            print(f"  Fehler beim Scrollen oder Klicken auf 'Mehr laden': {click_err}")
                            break # Bei Klickfehler abbrechen

                        # Warte explizit darauf, dass *mehr* Karten erscheinen
                        print("  Warte auf neue Profile...")
                        time.sleep(self.delay / 2) # Kurze initiale Pause
                        WebDriverWait(self.driver, 15).until( # Timeout für neue Karten
                            lambda d: len(d.find_elements(By.CSS_SELECTOR, profile_card_selector)) > card_count_before
                        )
                        new_count = len(self.driver.find_elements(By.CSS_SELECTOR, profile_card_selector))
                        print(f"  Neue Profile geladen (jetzt {new_count} sichtbar).")
                        time.sleep(self.delay / 2) # Kleine Pause nach Laden

                    except (TimeoutException, NoSuchElementException):
                        print("  'Mehr laden'-Knopf nicht mehr gefunden/klickbar oder keine neuen Karten geladen (Timeout). Ende erreicht.")
                        break # Knopf nicht gefunden oder keine neuen Karten geladen
                    except Exception as e:
                        print(f"  Unbekannter Fehler in 'Mehr laden'-Schleife: {e}")
                        break 
                
                if click_count >= max_load_more_clicks:
                     print(f"Sicherheitslimit von {max_load_more_clicks} Klicks erreicht.")
                # --- Ende "Mehr laden"-Schleife ---

                # --- Sammle URLs NACHDEM alle Klicks gemacht wurden ---
                print("Sammle jetzt alle Profil-URLs von der Seite...")
                final_profile_elements = self.driver.find_elements(By.CSS_SELECTOR, profile_card_selector)
                print(f"  Prüfe {len(final_profile_elements)} gefundene Profilkarten/Links nach dem Laden.")

                for element in final_profile_elements:
                    if len(profile_urls) >= self.max_profiles:
                        print(f"Maximale Anzahl an Profilen ({self.max_profiles}) erreicht.")
                        break
                    try:
                        href = element.get_attribute("href")
                        if href and "/id" in href and href not in processed_hrefs:
                            full_url = urljoin(self.base_url, href) 
                            if full_url not in processed_hrefs:
                                 profile_urls.append(full_url)
                                 processed_hrefs.add(full_url)
                                 processed_hrefs.add(href) 
                                 # Weniger Output hier, nur alle X Profile
                                 if len(profile_urls) % 10 == 0:
                                      print(f"  Gefunden URL #{len(profile_urls)}: {full_url}")
                    except StaleElementReferenceException:
                        print("  WARNUNG: Stale element reference beim Sammeln eines Links - überspringe.")
                        continue 
                    except Exception as extract_err:
                        print(f"  Fehler beim Sammeln eines Links: {extract_err}")

            except Exception as e:
                print(f"Fehler beim Extrahieren von Profil-URLs (Selenium): {e}")
        else:
             print("Selenium wird benötigt für Tabor.ru.")

        print(f"Gefundene Profil-URLs insgesamt: {len(profile_urls)}")
        return profile_urls[:self.max_profiles] # Gibt die gesammelten URLs zurück

    def extract_profile_info(self, profile_url):
        """ Überschriebene Methode zum Extrahieren von Profilinformationen von Tabor.ru (Stabiler V2 & Galerie V2) """
        # (Code von Version 17 - sollte funktionieren)
        profile_info = {
            "url": profile_url, "username": None, "age": None, "gender": "female", # Annahme
            "location": None, "description": None, "image_urls": []
        }
        
        all_image_urls = set() 
        gallery_url = None 

        try:
            if self.use_selenium and self.driver:
                print(f"Öffne Profil-Detailseite: {profile_url}")
                self.driver.get(profile_url)
                time.sleep(self.delay / 2)

                # --- Selektoren für die Detailseite ---
                wait_selector_title = ".user__title" 
                wait_selector_img_link = ".user__img-inner a.link-wrapper" 
                username_selector = "h1.user__name"
                age_selector = "div.user__title span[itemprop='description']"
                location_selector = "div.user__place span[itemprop='addressLocality']"
                preview_image_link_selector = ".user__img-inner a.link-wrapper" 
                gender_selector = ".profile-gender" # Platzhalter!
                description_selector = ".profile-about p" # Platzhalter! 

                # --- Robusteres Warten ---
                try:
                    print(f"Warte auf Detailseiten-Elemente: {wait_selector_title} und {wait_selector_img_link}")
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector_title))
                    )
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector_img_link))
                    )
                    print("  Wichtige Detailseiten-Elemente gefunden.")
                    time.sleep(0.5)
                except (TimeoutException, NoSuchElementException):
                    print(f"  WARNUNG: Wichtige Start-Elemente nicht gefunden. Seite evtl. nicht geladen oder Struktur anders? Überspringe Profil.")
                    return profile_info 

                # --- Extrahiere Basis-Infos (jeweils mit try-except) ---
                try:
                    profile_info["username"] = self.driver.find_element(By.CSS_SELECTOR, username_selector).text.strip()
                    print(f"  Username gefunden: {profile_info['username']}")
                except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e: print(f"  WARNUNG: Username nicht gefunden ({username_selector}): {type(e).__name__}")
                try:
                    age_text = self.driver.find_element(By.CSS_SELECTOR, age_selector).text.strip()
                    age_match = re.search(r'\d+', age_text)
                    if age_match: profile_info["age"] = int(age_match.group())
                    print(f"  Alter gefunden: {profile_info['age']}")
                except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e: print(f"  WARNUNG: Alter nicht gefunden ({age_selector}): {type(e).__name__}")
                try:
                    profile_info["location"] = self.driver.find_element(By.CSS_SELECTOR, location_selector).text.strip()
                    print(f"  Ort gefunden: {profile_info['location']}")
                except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e: print(f"  WARNUNG: Ort nicht gefunden ({location_selector}): {type(e).__name__}")
                try: 
                    profile_info["gender"] = self.driver.find_element(By.CSS_SELECTOR, gender_selector).text.strip()
                    print(f"  Geschlecht gefunden: {profile_info['gender']}")
                except Exception as e: print(f"  INFO: Geschlecht nicht gefunden (Selektor '{gender_selector}' prüfen) - Setze '{profile_info['gender']}'.")
                try: 
                    profile_info["description"] = self.driver.find_element(By.CSS_SELECTOR, description_selector).text.strip()
                    print(f"  Beschreibung gefunden: {profile_info['description'][:50]}...")
                except Exception as e: print(f"  INFO: Beschreibung nicht gefunden (Selektor '{description_selector}' prüfen).")

                # --- Finde Galerie-Link ---
                try:
                    gallery_link_element = self.driver.find_element(By.CSS_SELECTOR, preview_image_link_selector)
                    gallery_url_relative = gallery_link_element.get_attribute('href')
                    if gallery_url_relative:
                        gallery_url = urljoin(self.base_url, gallery_url_relative)
                        print(f"  Link zur Fotogalerie gefunden: {gallery_url}")
                    else: gallery_url = None
                except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                    print(f"  WARNUNG: Galerie-Link nicht gefunden ({preview_image_link_selector}): {type(e).__name__}")
                    gallery_url = None

                # --- Extrahiere ALLE Bilder aus der Galerie ---
                if gallery_url:
                    try:
                        print(f"  Navigiere zur ersten Foto-Seite: {gallery_url}")
                        self.driver.get(gallery_url)
                        time.sleep(self.delay / 2) 

                        large_image_selector = "img.modal__photo__img"
                        next_arrow_selector = "a.modal__pager-wrap_right"
                        
                        photo_limit = 20 
                        photo_count = 0
                        current_src = None 

                        while photo_count < photo_limit:
                            photo_count += 1
                            print(f"  Verarbeite Foto #{photo_count}...")
                            
                            try:
                                large_image_element = WebDriverWait(self.driver, 15).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, large_image_selector))
                                )
                                if current_src:
                                    print(f"    Warte darauf, dass sich das Bild von {current_src} ändert...")
                                    try:
                                        WebDriverWait(self.driver, 15).until(
                                            lambda d: d.find_element(By.CSS_SELECTOR, large_image_selector).get_attribute('src') != current_src
                                        )
                                        print("    Bild hat sich geändert.")
                                        large_image_element = self.driver.find_element(By.CSS_SELECTOR, large_image_selector)
                                    except TimeoutException:
                                        print(f"    WARNUNG: Warten auf Bildwechsel (src != {current_src}) fehlgeschlagen (Timeout). Breche Galerie ab.")
                                        break 
                                
                                new_src = large_image_element.get_attribute('src')
                                if new_src:
                                     current_src = new_src 
                                     full_img_url = urljoin(self.base_url, current_src)
                                     if full_img_url not in all_image_urls:
                                         print(f"    Gefundene Bild-URL: {full_img_url}")
                                         all_image_urls.add(full_img_url)
                                     else:
                                         print("    Bild-URL bereits bekannt (Galerie Ende?).")
                                         break 
                                else:
                                    print("    WARNUNG: Konnte src Attribut nicht vom Bild lesen.")
                                    break 

                            except (TimeoutException, StaleElementReferenceException) as img_err:
                                print(f"    WARNUNG: Fehler beim Warten/Lesen des großen Bildes: {img_err}")
                                break 

                            try:
                                next_arrow = self.driver.find_element(By.CSS_SELECTOR, next_arrow_selector)
                                print("    'Weiter'-Pfeil gefunden, klicke...")
                                next_arrow.click() 
                                time.sleep(1) 

                            except NoSuchElementException:
                                print("    Kein 'Weiter'-Pfeil mehr gefunden. Ende der Galerie erreicht.")
                                break 
                            except Exception as click_err:
                                print(f"    WARNUNG: Fehler beim Klicken auf 'Weiter': {click_err}")
                                break 
                        
                        if photo_count >= photo_limit:
                            print(f"  Sicherheitslimit von {photo_limit} Fotos erreicht.")

                    except Exception as gallery_err:
                        print(f"  WARNUNG: Fehler beim Verarbeiten der Fotogalerie: {gallery_err}")
                
                # --- Fallback auf Vorschau ---
                if not all_image_urls:
                     print("  Keine Bilder aus Galerie gefunden/verarbeitet, versuche Vorschau-Bild...")
                     try:
                         if self.driver.current_url != profile_url:
                              print(f"  Navigiere zurück zur Detailseite: {profile_url}")
                              self.driver.get(profile_url)
                              time.sleep(self.delay / 2)
                         preview_img_selector = "img.user__img" 
                         preview_img_element = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, preview_img_selector))
                         )
                         preview_src = preview_img_element.get_attribute('src')
                         if preview_src:
                             full_img_url = urljoin(self.base_url, preview_src)
                             print(f"    Gefundene Vorschau-Bild-URL: {full_img_url}")
                             all_image_urls.add(full_img_url)
                     except Exception as prev_err:
                         print(f"    WARNUNG: Fehler beim Finden des Vorschau-Bildes: {prev_err}")

            else:
                print("Requests-basiertes Extrahieren nicht implementiert.")

        except Exception as e:
            print(f"!!! SCHWERER FEHLER beim Extrahieren von Profilinformationen für {profile_url}: {e}")

        profile_info["image_urls"] = list(all_image_urls) 
        print(f"  -> Extraktion abgeschlossen für {profile_url}. Gefundene Bild-URLs: {len(profile_info['image_urls'])}")
        
        time.sleep(self.delay / 2) 
        return profile_info


if __name__ == "__main__":
    # Konfiguration für Tabor.ru
    downloader = ExampleSiteDownloader(
        output_dir="tabor_profiles", 
        delay=6, 
        max_profiles=500, # <<<=== HIER WERT ANPASSEN FALLS GEWÜNSCHT
        use_selenium=True 
    )

    # --- KEINE Zugangsdaten benötigt für diesen Testlauf ---
    # downloader.username = "DEIN_BENUTZERNAME"
    # downloader.password = "DEIN_PASSWORT"
    # ----------------------------------------------------

    # Starte den Download-Prozess
    downloader.run()