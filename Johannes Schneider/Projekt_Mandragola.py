from lxml import etree
from collections import Counter
import csv

# Namespace definieren für TEI (Text Encoding Initiative) XML-Dokumente
namespace = {'tei': 'http://www.tei-c.org/ns/1.0'}

# XML-Dokument parsen --> Download Mandragola from DraCor (https://www.dracor.org)
treeText = etree.parse(r"Machiavelli_Mandragola_DraCor.xml")

# Extraktion der Textzeilen innerhalb der <text> Tags
listLines = treeText.xpath(
    './/tei:text//tei:l/text() | .//tei:text//tei:p/text()', namespaces=namespace)

# Liste zum Speichern der verarbeiteten Wörter
hitList = []

# for-Schleife über jede Textzeile
for line in listLines:
    # Wörter durch Leerzeichen und Apostroph trennen
    wordlist = line.lower().replace("'", " ").split()
    for word in wordlist:
        # Interpunktion entfernen und Wort zur Liste hinzufügen
        trimmedWord = word.translate(str.maketrans('', '', '.,;!?\"-–:«»—'))
        hitList.append(trimmedWord)

# Häufigkeit der Wörter zählen
word_counter = Counter(hitList)

# CSV-Datei erstellen und Wörter mit ihren Häufigkeiten speichern
f = open(r"WordOccurence.csv", "w", encoding="utf-8")

csv.register_dialect("custom", delimiter=",",
                     skipinitialspace=True, lineterminator='\n')
writer = csv.writer(f, dialect="custom")
# Spaltenüberschriften
writer.writerow(['Word', 'Count'])

# Schreiben der Wörter und ihrer Häufigkeiten in die CSV-Datei
for word, count in word_counter.items():
    writer.writerow([word, count])
f.close()

# Ausgabe der Top 500 Wörter und ihrer Häufigkeiten
print("Frequenzanalyse (Top 500 Wörter):")
for trimmedWord, count in word_counter.most_common(500):
    print(f"{trimmedWord}: {count}")
