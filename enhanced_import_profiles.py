#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Erweiterter Profil-Importer für Dating-Plattform

Dieses Skript importiert heruntergeladene Profile und Bilder in die Dating-Plattform.
Es verwendet die Django-Modelle der Plattform, um neue Fake-Profile zu erstellen.
Erweitert mit Funktionen für zufällige Benutzernamen und Ortsangaben.
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

# Listen für zufällige Namen und Orte
FEMALE_NAMES = [
    "Anna", "Maria", "Sophie", "Emma", "Hannah", "Lena", "Lea", "Leonie", "Julia", "Sarah",
    "Lisa", "Laura", "Lara", "Nele", "Mia", "Jana", "Katharina", "Johanna", "Melanie", "Nina",
    "Vanessa", "Jessica", "Natalie", "Sabrina", "Jasmin", "Karin", "Stefanie", "Christina", "Sandra", "Nicole",
    "Elli", "Tina", "Jenny", "Franzi", "Susi", "Kati", "Miri", "Lilli", "Vicky", "Conny"
]

NICKNAMES_PREFIXES = [
    "süsse", "kleine", "sexy", "traum", "zauber", "glitzer", "sonnen", "herz", "liebe", "schatz",
    "engel", "prinzessin", "fee", "stern", "blumen", "zucker", "honig", "wild", "sanft", "zart",
    "süsses", "kleines", "Traum", "Zauber", "Glitzer", "Sonnen", "Herz", "Liebe", "Schatz", "Engel"
]

NICKNAMES_SUFFIXES = [
    "maus", "fee", "perle", "blume", "rose", "katze", "elfe", "nixe", "lady", "girl",
    "prinzessin", "königin", "göttin", "schönheit", "traumfrau", "sirene", "nymphe", "venus", "aphrodite", "diana",
    "Maus", "Fee", "Perle", "Blume", "Rose", "Katze", "Elfe", "Lady", "Girl", "Prinzessin"
]

# Zusätzliche Elemente für kreative Benutzernamen
USERNAME_ADJECTIVES = [
    "süss", "wild", "frech", "zart", "sanft", "sexy", "schön", "klug", "lieb", "nett",
    "Süss", "Wild", "Frech", "Zart", "Sanft", "Sexy", "Schön", "Klug", "Lieb", "Nett"
]

USERNAME_NOUNS = [
    "tänzerin", "träumerin", "lächeln", "küsschen", "herz", "seele", "sternchen", "sonnenschein", "schönheit", "blick",
    "Tänzerin", "Träumerin", "Lächeln", "Küsschen", "Herz", "Seele", "Sternchen", "Sonnenschein", "Schönheit", "Blick"
]

USERNAME_SPECIALS = [
    "xoxo", "007", "69", "24", "blue", "red", "pink", "black", "white", "gold",
    "Xoxo", "Blue", "Red", "Pink", "Black", "White", "Gold", "Silver", "Green", "Purple"
]

# Städte mit ihren Postleitzahlbereichen (als Strings, um führende Nullen zu erlauben)
GERMAN_CITIES = {
    "Berlin": {"plz_range": ("10115", "14199")},
    "Hamburg": {"plz_range": ("20038", "22769")},
    "München": {"plz_range": ("80331", "81929")},
    "Köln": {"plz_range": ("50667", "51149")},
    "Frankfurt": {"plz_range": ("60306", "60599")},
    "Stuttgart": {"plz_range": ("70173", "70619")},
    "Düsseldorf": {"plz_range": ("40210", "40629")},
    "Leipzig": {"plz_range": ("04103", "04357")},
    "Dortmund": {"plz_range": ("44135", "44388")},
    "Essen": {"plz_range": ("45127", "45359")},
    "Bremen": {"plz_range": ("28195", "28779")},
    "Dresden": {"plz_range": ("01067", "01326")},
    "Hannover": {"plz_range": ("30159", "30659")},
    "Nürnberg": {"plz_range": ("90402", "90491")},
    "Duisburg": {"plz_range": ("47051", "47279")},
    "Bochum": {"plz_range": ("44787", "44894")},
    "Wuppertal": {"plz_range": ("42103", "42399")},
    "Bielefeld": {"plz_range": ("33602", "33739")},
    "Bonn": {"plz_range": ("53111", "53229")},
    "Münster": {"plz_range": ("48143", "48167")},
    "Karlsruhe": {"plz_range": ("76131", "76229")},
    "Mannheim": {"plz_range": ("68159", "68309")},
    "Augsburg": {"plz_range": ("86150", "86199")},
    "Wiesbaden": {"plz_range": ("65183", "65207")},
    "Gelsenkirchen": {"plz_range": ("45879", "45897")},
    "Mönchengladbach": {"plz_range": ("41061", "41179")},
    "Braunschweig": {"plz_range": ("38100", "38126")},
    "Kiel": {"plz_range": ("24103", "24159")},
    "Chemnitz": {"plz_range": ("09111", "09131")},
    "Aachen": {"plz_range": ("52062", "52080")}
}

# Verschiedene Profilbeschreibungen mit unterschiedlichen Längen und Stilen
PROFILE_DESCRIPTIONS = [
    # Extrem kurz
    "Lebensfrohe {alter}-jährige sucht Abenteuer und mehr.",
    "Hier um Spaß zu haben und vielleicht mehr zu finden.",
    "Spontan, direkt und immer gut drauf. Meld dich!",
    "Neugierig auf neue Menschen und Erfahrungen.",
    "{name}, {alter}, sucht dich für gemeinsame Erlebnisse.",
    
    # Sehr kurz
    "Spontan, direkt und immer für Spaß zu haben. Mag gute Gespräche und Wein. Zeig mir deine Welt!",
    "Liebe das Leben, Reisen und gute Gesellschaft. Wenn du Humor hast, sollten wir uns kennenlernen.",
    "Kreative Seele mit Vorliebe für Abenteuer. Suche jemanden, der mich zum Lachen bringt.",
    "Träumerin mit Bodenhaftung. Mag Musik, Bücher und tiefe Gespräche bei einem Glas Wein.",
    "Optimistin mit Faible für gutes Essen und interessante Menschen. Zeig mir deine Perspektive!",
    
    # Kurz
    "Lebenslustige Optimistin sucht Gegenstück. Liebe Reisen, gutes Essen und tiefe Gespräche. Wenn du Humor hast und das Leben nicht zu ernst nimmst, könnten wir zusammenpassen.",
    "Tagsüber im Büro, abends auf Entdeckungstour. Suche jemanden, der sowohl den Alltag als auch besondere Momente mit mir teilen möchte. Humor und Ehrlichkeit sind mir wichtig.",
    "Ich bin eine Mischung aus Träumerin und Realistin. Liebe es, neue Orte zu entdecken, aber schätze auch gemütliche Abende zu Hause. Suche einen authentischen Partner für gemeinsame Abenteuer.",
    "Kreative Seele mit Leidenschaft für Musik, Kunst und gute Gespräche. Suche jemanden, der das Leben in vollen Zügen genießt und offen für Neues ist.",
    "Naturverbundene {alter}-Jährige mit Vorliebe für Spontanität. Wenn du Tiefgang hast, aber auch über dich selbst lachen kannst, sollten wir uns kennenlernen.",
    
    # Mittellang
    "Ich bin eine Träumerin mit Bodenhaftung. Verliere mich gerne in Büchern und Musik, liebe aber auch Wanderungen in der Natur. Suche jemanden, der authentisch ist und mit dem ich lachen kann. Das Leben ist zu kurz für Oberflächlichkeiten – lass uns etwas Echtes aufbauen.",
    "Leidenschaftliche {alter}-Jährige mit Faible für Abenteuer und ruhige Momente gleichermaßen. Ich liebe es zu reisen, neue Kulturen zu entdecken und über das Leben zu philosophieren. Suche einen Partner, der Tiefgang hat, aber auch weiß, wann es Zeit ist, einfach nur zu lachen und das Leben zu genießen.",
    "Das Leben ist eine Reise, und ich suche jemanden, der mich auf diesem Weg begleitet. Ich bin spontan, neugierig und immer offen für neue Erfahrungen. Meine Freunde beschreiben mich als warmherzig, humorvoll und manchmal ein bisschen verrückt. Wenn du Lust auf gemeinsame Abenteuer hast, freue ich mich auf deine Nachricht.",
    "Ich glaube an echte Verbindungen und daran, dass man im Leben nie aufhören sollte zu lernen. Liebe gute Gespräche bei einem Glas Wein, Spaziergänge in der Natur und spontane Wochenendtrips. Suche jemanden, der das Leben mit all seinen Facetten zu schätzen weiß und mit dem ich sowohl lachen als auch tiefgründige Gespräche führen kann.",
    "Zwischen Träumen und Taten liegt oft nur ein kleiner Schritt. Ich bin jemand, der diesen Schritt gerne wagt. Ob beim Reisen, in der Liebe oder im Alltag – ich suche das Echte, das Besondere. Wenn du ähnlich tickst und Lust hast, gemeinsam Neues zu entdecken, würde ich mich freuen, dich kennenzulernen.",
    
    # Mittellang mit Emojis
    "Reiselustig ✈️ Naturverbunden 🌿 Kaffeeliebhaberin ☕ Suche jemanden zum Lachen und Träumen. Wenn du Tiefgang und Humor vereinst, könnten wir zusammenpassen. Leben ist zu kurz für Langeweile - lass uns gemeinsam Erinnerungen schaffen! 💫",
    "Kreative Seele 🎨 Musikliebhaberin 🎵 Immer auf der Suche nach dem nächsten Abenteuer 🌍 Wenn du authentisch bist und das Leben in vollen Zügen genießt, sollten wir uns kennenlernen! Glaube an tiefe Verbindungen und magische Momente ✨",
    "Optimistin mit Faible für gutes Essen 🍷 und tiefe Gespräche 💭 Liebe es, neue Orte zu entdecken 🌎 und den Moment zu genießen ⏳ Suche jemanden, der mich zum Lachen bringt und mit dem ich über Gott und die Welt philosophieren kann 💫",
    "Sportbegeistert 🏃‍♀️ Naturliebhaberin 🌳 Genießerin 🍫 Suche einen Partner, der sowohl Tiefgang als auch Humor hat. Das Leben ist zu kurz für Mittelmäßigkeit - lass uns zusammen etwas Besonderes daraus machen! 💖",
    "Bücherwurm 📚 Reiselustig 🧳 Kaffee-Junkie ☕ Suche jemanden, der mich inspiriert und mit dem ich lachen kann. Glaube an Ehrlichkeit, Respekt und daran, dass die schönsten Momente oft die unerwarteten sind ✨",
    
    # Lang
    "Tagsüber Businesslady, abends Abenteurerin. Ich liebe es, neue Orte zu entdecken, fremde Küchen zu probieren und Menschen kennenzulernen, die mich inspirieren. Meine Freunde beschreiben mich als leidenschaftlich, einfühlsam und manchmal ein bisschen verrückt. Ich glaube an tiefe Verbindungen und daran, dass man im Leben nie aufhören sollte zu lernen und zu wachsen. Suche einen Partner, der meine Intensität schätzt, mich zum Lachen bringt und mit dem ich sowohl den Alltag als auch besondere Momente teilen kann.",
    "Ich bin eine Mischung aus Träumerin und Realistin – glaube an die Magie des Lebens, aber behalte immer beide Füße auf dem Boden. Liebe es, durch fremde Städte zu schlendern, in Buchhandlungen zu stöbern und stundenlang bei gutem Essen zu sitzen. Meine Freunde würden mich als warmherzig, loyal und manchmal zu perfektionistisch beschreiben. Ich suche jemanden, der seine eigene Geschichte hat und mit mir zusammen neue Kapitel schreiben möchte – jemanden, der Tiefgang hat, aber auch weiß, wann es Zeit ist, einfach nur zu lachen und das Leben zu genießen.",
    "Das Leben ist eine Sammlung von Momenten – ich versuche, jeden davon wertzuschätzen. Ob beim Wandern in den Bergen, beim Kochen mit Freunden oder beim Entdecken eines neuen Buches – ich finde überall etwas, das mich begeistert. Ich bin neugierig, offen und immer bereit für neue Erfahrungen. Meine Freunde sagen, ich hätte die Gabe, selbst in alltäglichen Dingen etwas Besonderes zu sehen. Ich glaube an Ehrlichkeit, Respekt und daran, dass eine Beziehung sowohl Halt als auch Freiheit geben sollte. Wenn du ähnlich denkst und Lust hast, gemeinsam das Leben zu erkunden, würde ich mich freuen, dich kennenzulernen.",
    "Ich bin jemand, der das Leben in all seinen Facetten zu schätzen weiß – die lauten, aufregenden Momente genauso wie die leisen, nachdenklichen. Reisen ist meine große Leidenschaft, aber ich genieße auch die kleinen Abenteuer des Alltags. Ich liebe tiefe Gespräche bei einem guten Glas Wein, spontane Roadtrips und das Gefühl, wenn ein Buch oder ein Film mich wirklich berührt. Meine Freunde beschreiben mich als empathisch, humorvoll und manchmal zu analytisch. Ich suche jemanden, der seine eigenen Leidenschaften hat, der mich inspiriert und herausfordert, und mit dem ich sowohl lachen als auch über die großen Fragen des Lebens philosophieren kann.",
    "Zwischen Träumen und Taten liegt oft nur ein kleiner Schritt – ich bin jemand, der diesen Schritt gerne wagt. Ob beim Reisen, in der Liebe oder im Alltag – ich suche das Echte, das Besondere. Ich bin kreativ, neugierig und immer offen für neue Perspektiven. Meine Freunde schätzen meine Fähigkeit, zuzuhören und auch in schwierigen Situationen einen Silberstreif am Horizont zu finden. Ich glaube an tiefe Verbindungen, an Gespräche, die bis in die frühen Morgenstunden gehen, und daran, dass man im Leben nie aufhören sollte, neugierig zu sein. Wenn du Lust hast, gemeinsam Neues zu entdecken und dabei auch die kleinen Dinge des Lebens zu genießen, würde ich mich freuen, dich kennenzulernen.",
    
    # Sehr lang
    "Die Welt ist voller Möglichkeiten und ich bin hier, um sie zu entdecken! Wenn ich nicht gerade auf Reisen bin oder neue Rezepte ausprobiere, findet man mich beim Yoga oder mit einem guten Buch in meiner Lieblingsecke. Ich habe auf drei Kontinenten gelebt und spreche vier Sprachen – Kommunikation ist mir wichtig, egal ob durch Worte, Blicke oder Berührungen. Meine Freunde sagen, ich hätte die Gabe, selbst in alltäglichen Dingen etwas Besonderes zu sehen. Ich glaube an Ehrlichkeit, Respekt und daran, dass man nie aufhören sollte, neugierig zu sein. Die kleinen Dinge machen für mich das Leben aus: der perfekte Sonnenuntergang, ein herzhaftes Lachen, der Duft von frischem Kaffee am Morgen. Ich suche jemanden, der seine eigene Geschichte hat und mit mir zusammen neue Kapitel schreiben möchte – jemanden, der Tiefgang hat, aber auch weiß, wann es Zeit ist, einfach nur zu lachen und das Leben zu genießen. Wenn du dich in dieser Beschreibung wiederfindest, würde ich mich freuen, dich kennenzulernen.",
    "Das Leben ist eine Reise, und ich bin jemand, der jeden Moment davon auskosten möchte. Ich liebe es, neue Orte zu entdecken, fremde Kulturen kennenzulernen und Menschen zu begegnen, die mich inspirieren. Aber ich schätze auch die ruhigen Momente: einen Sonnenuntergang am Meer, ein gutes Buch bei einer Tasse Tee oder tiefe Gespräche mit Freunden bis in die frühen Morgenstunden. Meine Freunde beschreiben mich als warmherzig, abenteuerlustig und manchmal ein bisschen chaotisch. Ich glaube an echte Verbindungen, an Gespräche, die unter die Haut gehen, und daran, dass man im Leben nie aufhören sollte zu träumen. Die kleinen Dinge sind für mich oft die wertvollsten: ein aufrichtiges Lächeln, eine spontane Umarmung oder ein Moment vollkommener Stille in einer hektischen Welt. Ich suche jemanden, der seine eigenen Leidenschaften hat, der mich zum Lachen bringt und mit dem ich sowohl den Alltag als auch besondere Momente teilen kann – jemanden, der das Leben in all seinen Facetten zu schätzen weiß und offen für neue Abenteuer ist. Wenn du Lust hast, gemeinsam Neues zu entdecken und dabei auch die kleinen Wunder des Alltags zu genießen, würde ich mich freuen, dich kennenzulernen.",
    "Zwischen Träumen und Realität liegt oft nur ein kleiner Schritt – ich bin jemand, der diesen Schritt gerne wagt. Ob beim Reisen, in der Liebe oder im Alltag – ich suche das Authentische, das Besondere. Ich bin kreativ, neugierig und immer offen für neue Perspektiven. Meine Freunde schätzen meine Fähigkeit, zuzuhören und auch in schwierigen Situationen einen Silberstreif am Horizont zu finden. Ich glaube an tiefe Verbindungen, an Gespräche, die bis in die frühen Morgenstunden gehen, und daran, dass man im Leben nie aufhören sollte, neugierig zu sein. Die kleinen Dinge machen für mich oft den Unterschied: ein aufrichtiges Kompliment, ein spontaner Tanz in der Küche oder ein Moment vollkommener Verbundenheit mit einem anderen Menschen. Ich liebe es, neue Orte zu entdecken, fremde Küchen zu probieren und Menschen kennenzulernen, die mich inspirieren. Aber ich genieße auch die ruhigen Momente: einen Spaziergang im Wald, ein gutes Buch bei einer Tasse Kaffee oder tiefe Gespräche mit Freunden. Ich suche jemanden, der seine eigenen Leidenschaften hat, der mich herausfordert und inspiriert, und mit dem ich sowohl lachen als auch über die großen Fragen des Lebens philosophieren kann – jemanden, der das Leben in all seinen Höhen und Tiefen zu schätzen weiß und mit dem ich gemeinsam wachsen kann. Wenn du Lust hast, gemeinsam Neues zu entdecken und dabei auch die kleinen Wunder des Alltags zu genießen, würde ich mich freuen, dich kennenzulernen.",
    
    # Sexy/Verführerisch
    "Ich bin eine leidenschaftliche Frau, die weiß, was sie will. Tagsüber Businesslady, nachts wilde Katze. Ich liebe tiefe Gespräche bei einem Glas Wein und spontane Abenteuer. Suche einen selbstbewussten Mann, der mit meiner Intensität umgehen kann und mich zum Lachen bringt. Wenn du Tiefgang und Feuer in einem Paket suchst, sind wir vielleicht ein Match.",
    "Sinnlich, selbstbewusst und immer für Überraschungen gut. Ich liebe es, zu verführen und verführt zu werden – mit Worten, Blicken und mehr. Suche einen Mann, der weiß, was er will und wie er eine Frau behandeln sollte. Das Leben ist zu kurz für Langeweile – lass es uns zusammen interessant machen.",
    
    # Verträumt/Romantisch
    "Träumerin mit beiden Beinen auf dem Boden. Ich verliere mich gerne in Büchern, liebe Spaziergänge im Regen und glaube an die kleinen Wunder des Alltags. Mein Herz schlägt für Sonnenuntergänge, handgeschriebene Briefe und tiefe Gespräche bis in die Nacht. Suche jemanden, der die Welt mit offenen Augen sieht und mit mir zusammen neue Kapitel schreiben möchte.",
    "Ich glaube an die Magie der kleinen Momente und daran, dass wahre Romantik im Alltäglichen zu finden ist. Liebe Poesie, Kerzenlicht und Gespräche, die unter die Haut gehen. Suche jemanden, der das Leben mit all seinen Farben wahrnimmt und mit dem ich sowohl lachen als auch träumen kann.",
    
    # Abenteuerlustig/Draufgängerisch
    "Leben ist zu kurz für Langeweile! Wenn ich nicht gerade auf Reisen bin oder neue Sportarten ausprobiere, plane ich schon das nächste Abenteuer. Habe schon auf drei Kontinenten gelebt und bin süchtig nach Adrenalin und neuen Erfahrungen. Suche einen Komplizen, der spontan den Rucksack packt, wenn ich sage: 'Lass uns verschwinden!' Stillstand ist nichts für mich – bist du bereit mitzuhalten?",
    "Adrenalin-Junkie mit Faible für spontane Roadtrips und neue Herausforderungen. Ob Fallschirmspringen, Tauchen oder einfach nur eine neue Stadt erkunden – ich bin immer dabei! Suche jemanden, der genauso abenteuerlustig ist und keine Angst hat, aus der Komfortzone herauszutreten. Das Leben passiert außerhalb der eigenen vier Wände – lass es uns gemeinsam entdecken!",
    
    # Bodenständig/Natürlich
    "Einfach und unkompliziert - das bin ich. Ich genieße die kleinen Dinge: einen guten Kaffee am Morgen, Lachen mit Freunden, Kochen mit frischen Zutaten vom Markt. Bin lieber in der Natur als in überfüllten Clubs und schätze ehrliche Gespräche mehr als oberflächlichen Smalltalk. Suche jemanden authentischen, mit dem ich gemeinsam durch den Alltag gehen kann - mit all seinen Höhen und Tiefen.",
    "Naturverbunden und bodenständig. Ich finde Schönheit in den einfachen Dingen des Lebens und schätze Authentizität über alles. Liebe Wanderungen im Wald, gemütliche Abende zu Hause und herzliches Lachen. Suche einen Partner, der ähnliche Werte teilt und mit dem ich eine ehrliche, tiefe Verbindung aufbauen kann.",
    
    # Humorvoll/Quirky
    "Warnung: Ich lache über meine eigenen Witze! Chronisch optimistisch und mit einer Vorliebe für schlechte Wortspiele ausgestattet. Meine Freunde sagen, ich bin die perfekte Mischung aus verrückt und liebenswert. Wenn ich nicht gerade meine Tanzschritte vor dem Spiegel übe oder mit meiner Katze philosophiere, backe ich die weltbesten Chocolate Chip Cookies. Suche jemanden, der meine Verrücktheit ergänzt und mit mir das Leben nicht zu ernst nimmt.",
    "Life's too short to be serious all the time! Ich bin die, die nachts um 3 philosophische Fragen stellt und morgens mit einem Lächeln aufwacht. Meine Spezialität: spontane Tanzeinlagen und kreative Lösungen für alltägliche Probleme. Suche jemanden, der meine schrägen Ideen zu schätzen weiß und mit mir die Absurdität des Lebens feiern möchte."
]

class EnhancedProfileImporter:
    """Erweiterte Klasse zum Importieren von Profilen in die Dating-Plattform"""
    
    def __init__(self, profiles_dir, moderator_username=None, city=None, use_nicknames=False):
        """
        Initialisiert den Importer
        
        Args:
            profiles_dir (str): Pfad zum Verzeichnis mit den Profilen
            moderator_username (str, optional): Benutzername des Moderators, der die Profile verwalten soll
            city (str, optional): Stadt, die für alle Profile verwendet werden soll
            use_nicknames (bool): Ob Internet-Nicknames statt echter Namen verwendet werden sollen
        """
        self.profiles_dir = profiles_dir
        self.metadata_file = os.path.join(profiles_dir, "metadata.json")
        self.metadata = self._load_metadata()
        self.moderator = None
        self.city = city
        self.use_nicknames = use_nicknames
        
        if moderator_username:
            try:
                self.moderator = User.objects.get(username=moderator_username, is_staff=True)
                print(f"Moderator gefunden: {self.moderator.username}")
            except User.DoesNotExist:
                print(f"Warnung: Moderator '{moderator_username}' nicht gefunden oder kein Staff-Mitglied")
    
    def _load_metadata(self):
        """Lädt die Metadaten aus der JSON-Datei"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Warnung: Metadaten-Datei '{self.metadata_file}' nicht gefunden. Verwende leere Metadaten.")
                return {}
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Fehler beim Laden der Metadaten: {e}")
            return {}
    
    def _generate_username(self, profile_info=None):
        """
        Generiert einen eindeutigen Benutzernamen mit verschiedenen kreativen Mustern
        
        Args:
            profile_info (dict, optional): Profilinformationen
            
        Returns:
            str: Eindeutiger Benutzername
        """
        # Wähle ein zufälliges Muster für den Benutzernamen
        pattern = random.choice([
            "real_name",           # Echter Name mit Variationen
            "nickname",            # Klassischer Nickname (prefix + suffix)
            "camel_case",          # CamelCase-Stil (z.B. süssesMädchen)
            "adjective_noun",      # Adjektiv + Substantiv
            "special_prefix",      # Spezialzeichen/Zahl + Name
            "creative_combo"       # Kreative Kombination
        ])
        
        if pattern == "real_name":
            # Echter Name mit verschiedenen Variationen
            name = random.choice(FEMALE_NAMES)
            variation = random.choice([
                lambda n: n.lower(),                                # alles klein
                lambda n: n,                                        # normal
                lambda n: f"{n}{random.randint(0, 99)}",            # Name + Zahl
                lambda n: f"{n.lower()}{random.randint(0, 99)}",    # name + Zahl
                lambda n: f"{n}{random.choice('._-x')}{random.randint(0, 99)}"  # Name.Zahl
            ])
            base_username = variation(name)
            
        elif pattern == "nickname":
            # Klassischer Nickname mit verschiedenen Schreibweisen
            prefix = random.choice(NICKNAMES_PREFIXES)
            suffix = random.choice(NICKNAMES_SUFFIXES)
            
            # Zufällige Formatierung
            if random.choice([True, False]):
                # Erste Buchstaben groß
                prefix = prefix.capitalize()
            if random.choice([True, False]):
                # Erste Buchstaben groß
                suffix = suffix.capitalize()
                
            # Mit oder ohne Zahl
            if random.choice([True, False]):
                number = random.randint(0, 99)
                base_username = f"{prefix}{suffix}{number}"
            else:
                base_username = f"{prefix}{suffix}"
                
        elif pattern == "camel_case":
            # CamelCase-Stil
            prefix = random.choice(NICKNAMES_PREFIXES)
            suffix = random.choice(NICKNAMES_SUFFIXES)
            
            # CamelCase formatieren
            prefix = prefix[0].lower() + prefix[1:]
            suffix = suffix[0].upper() + suffix[1:]
            
            # Mit oder ohne Zahl
            if random.choice([True, False]):
                number = random.randint(0, 99)
                base_username = f"{prefix}{suffix}{number}"
            else:
                base_username = f"{prefix}{suffix}"
                
        elif pattern == "adjective_noun":
            # Adjektiv + Substantiv
            adjective = random.choice(USERNAME_ADJECTIVES)
            noun = random.choice(USERNAME_NOUNS)
            
            # Zufällige Formatierung
            format_style = random.choice([
                lambda a, n: f"{a}{n}",                     # alles zusammen
                lambda a, n: f"{a.capitalize()}{n}",        # Adjektiv groß
                lambda a, n: f"{a}{n.capitalize()}",        # Substantiv groß
                lambda a, n: f"{a.capitalize()}{n.capitalize()}"  # Beides groß
            ])
            
            base_username = format_style(adjective, noun)
            
            # Manchmal eine Zahl hinzufügen
            if random.choice([True, False]):
                base_username = f"{base_username}{random.randint(0, 99)}"
                
        elif pattern == "special_prefix":
            # Spezialzeichen/Zahl + Name
            special = random.choice(USERNAME_SPECIALS)
            name = random.choice(FEMALE_NAMES)
            
            # Zufällige Formatierung
            format_style = random.choice([
                lambda s, n: f"{s}{n}",                 # special + Name
                lambda s, n: f"{s}_{n}",                # special_Name
                lambda s, n: f"{s}{n.lower()}",         # special + name
                lambda s, n: f"{s.lower()}{n}"          # special + Name
            ])
            
            base_username = format_style(special, name)
            
        else:  # creative_combo
            # Kreative Kombination
            elements = [
                random.choice(FEMALE_NAMES),
                random.choice(USERNAME_ADJECTIVES),
                random.choice(USERNAME_NOUNS),
                random.choice(USERNAME_SPECIALS),
                str(random.randint(0, 99))
            ]
            
            # Wähle 2-3 zufällige Elemente aus
            selected_elements = random.sample(elements, random.randint(2, 3))
            
            # Zufällige Formatierung für jedes Element
            formatted_elements = []
            for i, element in enumerate(selected_elements):
                if random.choice([True, False]) and element.isalpha():
                    # Großbuchstaben für einige Elemente
                    if random.choice([True, False]):
                        element = element.capitalize()
                    else:
                        element = element.upper()
                formatted_elements.append(element)
            
            # Verbinde die Elemente
            connector = random.choice(['', '_', '.', '-'])
            base_username = connector.join(formatted_elements)
        
        # Stelle sicher, dass der Benutzername eindeutig ist
        original_username = base_username
        counter = 1
        
        while User.objects.filter(username=base_username).exists():
            # Füge eine Zahl hinzu oder erhöhe die bestehende
            if counter == 1:
                base_username = f"{original_username}{random.randint(100, 999)}"
            else:
                base_username = f"{original_username}{random.randint(1000, 9999)}"
            counter += 1
            
            # Fallback, falls immer noch nicht eindeutig
            if counter > 5:
                base_username = f"user_{random.randint(10000, 99999)}"
                break
        
        return base_username
    
    def _generate_email(self, username):
        """Generiert eine E-Mail-Adresse für den Benutzer"""
        domains = ["example.com", "fakemail.org", "testuser.net", "datinguser.de", "flirtmail.net"]
        return f"{username}@{random.choice(domains)}"
    
    def _generate_birth_date(self, age=None):
        """
        Generiert ein Geburtsdatum basierend auf dem Alter
        
        Args:
            age (int, optional): Alter der Person
            
        Returns:
            datetime.date: Zufälliges Geburtsdatum
        """
        if not age or age < 18:
            # Standardalter zwischen 25 und 45
            age = random.randint(25, 45)
        
        today = timezone.now().date()
        
        # Berechne das Geburtsjahr basierend auf dem Alter
        birth_year = today.year - age
        
        # Generiere ein zufälliges Datum im entsprechenden Jahr
        month = random.randint(1, 12)
        # Berücksichtige die unterschiedliche Anzahl von Tagen pro Monat
        if month in [4, 6, 9, 11]:
            day = random.randint(1, 30)
        elif month == 2:
            # Vereinfachte Schaltjahrberechnung
            if birth_year % 4 == 0 and (birth_year % 100 != 0 or birth_year % 400 == 0):
                day = random.randint(1, 29)
            else:
                day = random.randint(1, 28)
        else:
            day = random.randint(1, 31)
        
        try:
            return datetime(birth_year, month, day).date()
        except ValueError:
            # Fallback bei ungültigem Datum
            return datetime(birth_year, 1, 1).date()
    
    def _generate_about_me(self, name, age=None):
        """
        Wählt eine zufällige Profilbeschreibung aus
        
        Args:
            name (str): Name der Person
            age (int, optional): Alter der Person
            
        Returns:
            str: Zufällige Profilbeschreibung
        """
        # Wähle eine zufällige Beschreibung
        description = random.choice(PROFILE_DESCRIPTIONS)
        
        # Ersetze Platzhalter, falls vorhanden
        if "{name}" in description:
            description = description.replace("{name}", name)
        
        if "{alter}" in description and age:
            description = description.replace("{alter}", str(age))
        elif "{alter}" in description:
            # Fallback, wenn kein Alter angegeben ist
            description = description.replace("{alter}", str(random.randint(25, 45)))
        
        return description
    
    def _get_profile_folders(self):
        """
        Findet alle Profilordner im angegebenen Verzeichnis
        
        Returns:
            list: Liste von Tupeln (Ordnerpfad, Geschlecht)
        """
        profile_folders = []
        
        # Durchsuche die Geschlechterordner
        for gender_dir in ["female", "male", "other"]:
            gender_path = os.path.join(self.profiles_dir, gender_dir)
            if not os.path.exists(gender_path):
                continue
            
            # Bestimme das Geschlecht basierend auf dem Ordnernamen
            gender = GenderChoices.FEMALE if gender_dir == "female" else (
                GenderChoices.MALE if gender_dir == "male" else GenderChoices.FEMALE  # Default zu FEMALE für "other"
            )
            
            # Durchsuche die Profilordner
            for profile_dir in os.listdir(gender_path):
                profile_path = os.path.join(gender_path, profile_dir)
                if os.path.isdir(profile_path):
                    profile_folders.append((profile_path, gender, profile_dir))
        
        return profile_folders
    
    def _get_profile_age(self, profile_path, profile_name):
        """
        Versucht, das Alter aus den Metadaten zu extrahieren
        
        Args:
            profile_path (str): Pfad zum Profilordner
            profile_name (str): Name des Profilordners
            
        Returns:
            int or None: Alter der Person oder None, wenn nicht gefunden
        """
        # Versuche, das Alter aus den Metadaten zu extrahieren
        for profile_id, profile_info in self.metadata.items():
            # Prüfe, ob der Profilname im Pfad der lokalen Bilder vorkommt
            local_images = profile_info.get("local_images", [])
            if local_images and any(profile_name in img_path for img_path in local_images):
                return profile_info.get("age")
        
        return None
    
    def _get_profile_images(self, profile_path):
        """
        Findet alle Bilder im angegebenen Profilordner
        
        Args:
            profile_path (str): Pfad zum Profilordner
            
        Returns:
            list: Liste von Bildpfaden
        """
        image_paths = []
        
        for file_name in os.listdir(profile_path):
            file_path = os.path.join(profile_path, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_paths.append(file_path)
        
        return image_paths
    
    def import_profile(self, profile_path, gender, profile_name):
        """
        Importiert ein einzelnes Profil in die Dating-Plattform
        
        Args:
            profile_path (str): Pfad zum Profilordner
            gender (str): Geschlecht der Person
            profile_name (str): Name des Profilordners
            
        Returns:
            tuple: (Erfolg (bool), Benutzer-Objekt oder None, Anzahl importierter Bilder)
        """
        # Finde alle Bilder im Profilordner
        image_paths = self._get_profile_images(profile_path)
        if not image_paths:
            print(f"Keine Bilder für Profil '{profile_name}' gefunden")
            return False, None, 0
        
        # Generiere Benutzerdaten
        username = self._generate_username()
        email = self._generate_email(username)
        
        # Extrahiere das Alter aus den Metadaten oder verwende einen Standardwert
        age = self._get_profile_age(profile_path, profile_name)
        birth_date = self._generate_birth_date(age)
        
        # Generiere eine Selbstbeschreibung
        display_name = username.split('_')[0].capitalize()
        about_me = self._generate_about_me(display_name)
        
        # Bestimme den Ort und die Postleitzahl
        if self.city and self.city in GERMAN_CITIES:
            city = self.city
            # Generiere eine zufällige Postleitzahl für die angegebene Stadt
            plz_range = GERMAN_CITIES[city]["plz_range"]
            # Konvertiere Strings zu Integers für random.randint
            min_plz = int(plz_range[0])
            max_plz = int(plz_range[1])
            postal_code = str(random.randint(min_plz, max_plz))
        else:
            # Wähle eine zufällige Stadt
            city = random.choice(list(GERMAN_CITIES.keys()))
            # Generiere eine zufällige Postleitzahl für die zufällige Stadt
            plz_range = GERMAN_CITIES[city]["plz_range"]
            # Konvertiere Strings zu Integers für random.randint
            min_plz = int(plz_range[0])
            max_plz = int(plz_range[1])
            postal_code = str(random.randint(min_plz, max_plz))
        
        # Erstelle Fake-Benutzer
        try:
            user = User.objects.create(
                username=username,
                email=email,
                first_name=display_name,  # Verwende den ersten Teil des Benutzernamens als Vornamen
                is_fake=True,  # Markiere als Fake-Profil
                gender=GenderChoices.FEMALE,  # Immer weiblich
                seeking=GenderChoices.MALE,  # Sucht nach Männern
                birth_date=birth_date,
                city=city,
                postal_code=postal_code,
                country="Deutschland",  # Standardwert
                about_me=about_me,
                assigned_moderator=self.moderator
            )
            
            # Setze ein zufälliges Passwort
            user.set_password(f"fake_{random.randint(10000, 99999)}")
            user.save()
            
            print(f"Benutzer '{username}' erstellt (ID: {user.id}, Alter: {age or 'unbekannt'})")
            
            # Importiere Bilder
            imported_images = 0
            for img_path in image_paths:
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
    
    def import_all_profiles(self, max_profiles=None):
        """
        Importiert alle Profile aus dem angegebenen Verzeichnis
        
        Args:
            max_profiles (int, optional): Maximale Anzahl zu importierender Profile
            
        Returns:
            tuple: (Anzahl erfolgreicher Importe, Anzahl fehlgeschlagener Importe)
        """
        success_count = 0
        failure_count = 0
        total_images = 0
        
        # Finde alle Profilordner
        profile_folders = self._get_profile_folders()
        
        # Begrenze die Anzahl der Profile, falls angegeben
        if max_profiles and max_profiles > 0:
            profile_folders = profile_folders[:max_profiles]
        
        print(f"Importiere {len(profile_folders)} Profile...")
        
        for profile_path, gender, profile_name in profile_folders:
            success, user, image_count = self.import_profile(profile_path, gender, profile_name)
            
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
    parser = argparse.ArgumentParser(description="Erweiterter Profil-Importer für Dating-Plattform")
    
    parser.add_argument("profiles_dir", help="Pfad zum Verzeichnis mit den Profilen")
    parser.add_argument("-m", "--moderator", help="Benutzername des Moderators für die Fake-Profile")
    parser.add_argument("-n", "--number", type=int, help="Maximale Anzahl zu importierender Profile")
    parser.add_argument("-c", "--city", help="Stadt, die für alle Profile verwendet werden soll")
    parser.add_argument("--nicknames", action="store_true", help="Internet-Nicknames statt echter Namen verwenden")
    
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
    
    # Prüfe, ob das Profilverzeichnis existiert
    if not os.path.exists(args.profiles_dir):
        print(f"Fehler: Profilverzeichnis '{args.profiles_dir}' nicht gefunden")
        sys.exit(1)
    
    print("Erweiterter Profil-Importer für Dating-Plattform")
    print("==============================================")
    print(f"Profilverzeichnis: {args.profiles_dir}")
    print(f"Moderator: {args.moderator or 'Keiner'}")
    print(f"Stadt: {args.city or 'Zufällig'}")
    print(f"Namenstyp: {'Internet-Nicknames' if args.nicknames else 'Echte Namen'}")
    print(f"Max. Profile: {args.number or 'Alle'}")
    print("==============================================")
    
    # Starte den Import
    importer = EnhancedProfileImporter(
        args.profiles_dir,
        args.moderator,
        args.city,
        args.nicknames
    )
    importer.import_all_profiles(args.number)
