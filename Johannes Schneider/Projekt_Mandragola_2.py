from lxml import etree
from collections import Counter
import csv

# Namespace definieren für TEI (Text Encoding Initiative) XML-Dokumente
namespace = {'tei': 'http://www.tei-c.org/ns/1.0'}

# XML-Dokument parsen --> Download Mandragola from DraCor (https://www.dracor.org)
treeText = etree.parse(r"Machiavelli_Mandragola_DraCor.xml")

# Wortfelder definieren
semantic_fields = {
    'Politik und Macht': ['potere', 'signore', 'padrone', 're', 'mondo', 'maestro', 'parigi', 'firenze', 'onore', 'italia', 'danari', 'ducato', 'ducati', 'governa', 'governare'],
    'Intrige und Täuschung': ['inganno', 'sciocchezza', 'inganni', 'pozione', 'cervello', 'maschera', 'errore', 'sciocco', 'sciocchezza', 'sospetto', 'medicina', 'mandragola'],
    'Liebe und Leidenschaft': ['amore', 'desiderio', 'piacere', 'cuore', 'amante', 'letto', 'liuto', 'spogliare', 'rapporto', 'notte'],
    'Religion und Moral': ['dio', 'chiesa', 'santo', 'fede', 'inferno', 'virtù', 'madonna', 'iddio', 'frate', 'san', 'confessoro', 'diavol', 'diavolo', 'diavolerie', 'anima'],
    'Familie': ['padre', 'madre', 'marito', 'donna', 'donne', 'figliuolo', 'figliuola', 'figliuoli', 'matrimonio', 'moglie', 'casa']
}

# CSV-Datei erstellen und Header schreiben
f = open(r"Wortfelder_Akt_Häufigkeit.csv", "w", encoding="utf-8")

csv.register_dialect("custom", delimiter=",",
                     skipinitialspace=True, lineterminator='\n')
writer = csv.writer(f, dialect="custom")
# Spaltenüberschriften
writer.writerow(['Akt'] + list(semantic_fields.keys()))

# Häufigkeit der Wortfelder nach Akten analysieren
acts = treeText.findall('.//tei:div[@type="act"]', namespaces=namespace)
act_number = 1

# Iteration über alle Akte
for act in acts:
    # Extrahieren des Aktnamens
    head = act.find('.//tei:head', namespaces=namespace)
    if head is not None:
        act_name = head.text
        # Extrahieren der Textzeilen innerhalb des Akts
        act_lines = act.xpath(
            './/tei:l/text() | .//tei:p/text()', namespaces=namespace)

        hitList = []
        for line in act_lines:
            # Wörter durch Leerzeichen und Apostroph trennen
            wordlist = line.lower().replace("'", " ").split()
            for word in wordlist:
                # Interpunktion entfernen und Wort zur Liste hinzufügen
                trimmedWord = word.translate(
                    str.maketrans('', '', '.,;!?\"-–:«»—'))
                hitList.append(trimmedWord)

        # Häufigkeit der Wörter zählen
        word_counter = Counter(hitList)

        # Häufigkeit der Wortfelder analysieren
        field_counter = {
            semantic_field: 0 for semantic_field in semantic_fields}

        # Zählen der Wortfrequenzen in den definierten Wortfeldern
        for word in hitList:
            for semantic_field, words in semantic_fields.items():
                if word in words:
                    field_counter[semantic_field] += 1

        # Ergebnisse in die CSV-Datei schreiben
        writer.writerow([act_name] + [field_counter[semantic_field]
                        for semantic_field in semantic_fields])

        act_number += 1

f.close()

print("Die Ergebnisse wurden erfolgreich als CSV-Datei gespeichert.")
