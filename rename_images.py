#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bildnamen-Normalisierer

Dieses Skript durchsucht einen Ordner rekursiv nach Bildern und benennt sie um,
wobei kyrillische und andere nicht-ASCII-Zeichen durch ASCII-Zeichen ersetzt werden.
"""

import os
import re
import argparse
import unicodedata
import shutil
from pathlib import Path

def normalize_filename(filename):
    """
    Normalisiert einen Dateinamen, indem nicht-ASCII-Zeichen durch ASCII-Zeichen ersetzt werden
    und ungültige Zeichen für Dateinamen entfernt werden.
    
    Args:
        filename (str): Der zu normalisierende Dateiname
        
    Returns:
        str: Der normalisierte Dateiname
    """
    # Extrahiere Dateiendung
    base, ext = os.path.splitext(filename)
    
    # Normalisiere Unicode-Zeichen (z.B. Umlaute)
    base_normalized = unicodedata.normalize('NFKD', base)
    
    # Ersetze kyrillische Zeichen durch lateinische Entsprechungen
    # Dies ist eine vereinfachte Transliteration
    cyrillics_to_latin = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
        'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch', 'Ъ': '',
        'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    
    for cyrillic, latin in cyrillics_to_latin.items():
        base_normalized = base_normalized.replace(cyrillic, latin)
    
    # Entferne alle nicht-ASCII-Zeichen
    base_ascii = ''.join(c for c in base_normalized if ord(c) < 128)
    
    # Ersetze ungültige Zeichen für Dateinamen durch Unterstriche
    base_clean = re.sub(r'[^\w\-_.]', '_', base_ascii)
    
    # Stelle sicher, dass der Dateiname nicht leer ist
    if not base_clean:
        base_clean = "image"
    
    # Füge Dateiendung wieder hinzu
    return f"{base_clean}{ext}"

def rename_images_in_directory(directory, dry_run=False, verbose=False):
    """
    Benennt alle Bilddateien in einem Verzeichnis und seinen Unterverzeichnissen um.
    
    Args:
        directory (str): Das zu durchsuchende Verzeichnis
        dry_run (bool): Wenn True, werden die Änderungen nur angezeigt, aber nicht durchgeführt
        verbose (bool): Wenn True, werden detaillierte Informationen ausgegeben
        
    Returns:
        tuple: (Anzahl umbenannter Dateien, Anzahl fehlgeschlagener Umbenennungen)
    """
    renamed_count = 0
    failed_count = 0
    
    # Unterstützte Bildformate
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    
    # Durchlaufe alle Dateien im Verzeichnis und seinen Unterverzeichnissen
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # Prüfe, ob es sich um ein Bild handelt
            if filename.lower().endswith(image_extensions):
                # Vollständiger Pfad zur Datei
                file_path = os.path.join(root, filename)
                
                # Normalisiere den Dateinamen
                new_filename = normalize_filename(filename)
                
                # Wenn der Dateiname bereits normalisiert ist, überspringe ihn
                if new_filename == filename:
                    if verbose:
                        print(f"Überspringe bereits normalisierten Dateinamen: {file_path}")
                    continue
                
                # Neuer Pfad für die Datei
                new_file_path = os.path.join(root, new_filename)
                
                # Prüfe, ob die Zieldatei bereits existiert
                counter = 1
                while os.path.exists(new_file_path):
                    # Füge eine Nummer hinzu, um Konflikte zu vermeiden
                    base, ext = os.path.splitext(new_filename)
                    new_filename = f"{base}_{counter}{ext}"
                    new_file_path = os.path.join(root, new_filename)
                    counter += 1
                
                try:
                    if verbose or dry_run:
                        print(f"Benenne um: {file_path} -> {new_file_path}")
                    
                    if not dry_run:
                        # Benenne die Datei um
                        shutil.move(file_path, new_file_path)
                    
                    renamed_count += 1
                except Exception as e:
                    print(f"Fehler beim Umbenennen von {file_path}: {e}")
                    failed_count += 1
    
    return renamed_count, failed_count

def parse_arguments():
    """Parst Kommandozeilenargumente"""
    parser = argparse.ArgumentParser(description="Bildnamen-Normalisierer")
    
    parser.add_argument("directory", help="Das zu durchsuchende Verzeichnis")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Zeigt nur an, was gemacht werden würde, ohne Änderungen vorzunehmen")
    parser.add_argument("-v", "--verbose", action="store_true", help="Gibt detaillierte Informationen aus")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Prüfe, ob das Verzeichnis existiert
    if not os.path.exists(args.directory):
        print(f"Fehler: Verzeichnis '{args.directory}' nicht gefunden")
        exit(1)
    
    print("Bildnamen-Normalisierer")
    print("======================")
    print(f"Verzeichnis: {args.directory}")
    print(f"Dry-Run: {'Ja' if args.dry_run else 'Nein'}")
    print(f"Verbose: {'Ja' if args.verbose else 'Nein'}")
    print("======================")
    
    # Benenne Bilder um
    renamed_count, failed_count = rename_images_in_directory(args.directory, args.dry_run, args.verbose)
    
    print(f"\nUmbenennung abgeschlossen:")
    if args.dry_run:
        print(f"- {renamed_count} Dateien würden umbenannt werden")
    else:
        print(f"- {renamed_count} Dateien umbenannt")
    print(f"- {failed_count} Fehler aufgetreten")
