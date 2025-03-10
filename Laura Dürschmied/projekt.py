# Import-Section
from lxml import etree
from collections import Counter, defaultdict
import re
import statistics

# XML-Dokument parsen --> Download L'Avare from DraCor (https://www.dracor.org)
treeText = etree.parse("Moliere_Avare_DraCor.xml")

# Initialisierung der Zählvariablen
counter_argent = 0
counter_avarice = 0
counter_amour = 0
counter_questions = 0
counter_exclamations = 0
question_lengths = []

# Zugriff auf alle Sätze in der XML-Datei (XPath)
bodyText = treeText.xpath(".//s")

# Durchlauf durch alle Sätze
for elem in bodyText:
    text = elem.text.strip() if elem.text else ""

    if "argent" in text:  # für die Schlüsselwörter Geld, Geiz und Liebe, die als Schlüsselkonzepte des Werkes gesehen werden, werden jeweils Zählervariablen initialisiert, bei diesem Wort gibt es keine Varianten oder Zusammensetzungen, deshalb wird hier auf einen regulären Ausdruck verzichtet
        counter_argent += 1

    # hier wird das Ende des Wortes flexibel dargestellt, um sowohl Nomen als auch Adjektive zu finden
    if re.search(r"\bavar\w*\b", text):
        counter_avarice += 1

    # hier wird ein regulärer Ausdruck verwendet, um auch Wörter mit demselben Wortstamm, z.B. Adjektive zu finden, da diese ebenfalls zum Wortfeld gehören
    if re.search(r"\bamour[\s!,.;?]", text):
        counter_amour += 1

    if "?" in text:  # Die Satztypen werden durch ihr finales Satzzeichen gekennzeichnet, daher kann das Zählen der Fragezeichen mit der Anzahl der direkten Fragen gleichgesetzt werden
        counter_questions += 1
        question_lengths.append(len(text.split()))

    if "!" in text:  # Durch das Zählen der Ausrufezeichen werden die direkten Ausrufe gezählt, was für Emotionalität des Textes stehen kann.
        counter_exclamations += 1

# Berechnungen zu Satzlängen
if question_lengths:
    # Die durchschnittliche Länge der Fragen in Wörtern wird auf zwei Nachkommastellen gerundet
    question_length_average = round(statistics.mean(question_lengths), 2)
    # Die Länge der kürzesten Frage
    question_length_minimum = min(question_lengths)
else:
    question_length_average = 0
    question_length_minimum = 0

# Gesamtanzahl der Sätze
total_sentences = len(bodyText)

# Relativer Anteil von Fragen und Ausrufen
# Der Anteil von Fragen ergibt sich aus der Anzahl von Fragen geteilt durch die Gesamtzahl aller Sätze
question_ratio = round(counter_questions /
                       total_sentences * 100, 2) if total_sentences else 0
exclamation_ratio = round(counter_exclamations /
                          total_sentences * 100, 2) if total_sentences else 0

# Ausgabe in eine Datei statt nur in der Konsole
output_lines = [
    # auf die vorher befüllten Variablen wird zugegriffen
    f"Die durchschnittliche Fragenlänge ist: {question_length_average} Wörter",
    f"Das Wort 'argent' kommt {counter_argent} Mal im Text vor.",
    f"Das Wort 'avarice' kommt {counter_avarice} Mal im Text vor.",
    f"Das Wort 'amour' kommt {counter_amour} Mal im Text vor.",
    f"Es gibt {counter_questions} Fragen, das sind {question_ratio}% aller Sätze.",
    f"Es gibt {counter_exclamations} Ausrufe, das sind {exclamation_ratio}% aller Sätze."
]

# Satzarten analysieren (Durchschnittslängen nach Satztyp)
sentence_types = defaultdict(list)

for elem in bodyText:
    text = elem.text.strip() if elem.text else ""
    sentences = re.findall(r'([^.!?]+[.!?])', text)

    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            punctuation = sentence[-1]
            word_count = len(re.findall(r'\w+', sentence))
            sentence_types[punctuation].append(word_count)

# Durchschnittliche Satzlängen nach Satztyp berechnen
average_lengths = {punct: round(sum(lengths) / len(lengths), 2)
                   for punct, lengths in sentence_types.items() if lengths}

for punct, avg_length in average_lengths.items():
    output_lines.append(
        f"Durchschnittliche Satzlänge für '{punct}': {avg_length} Wörter")

# Partizipien erkennen (PPA-Formen)
participienlist = []  # eine leere Liste wird erstellt

for elem in bodyText:
    words = elem.text.split() if elem.text else []
    # Die Wortformen, die auf -ant enden, werden an die Liste angehängt
    participienlist.extend(
        [word for word in words if re.match(r".+ant\b", word)])

# Bereinigung und Analyse der Partizipien
unique_participien = sorted(set(word.lower() for word in participienlist))
output_lines.append(f"Es gibt {len(participienlist)} Partizipien im Text.")
output_lines.append(
    f"Es gibt {len(unique_participien)} verschiedene Partizipien im Text.")


# Ergebnisse in eine Datei schreiben
with open("literaturanalyse_ergebnisse.txt", "w", encoding="utf-8") as file:
    for line in output_lines:
        file.write(line + "\n")

print("Analyse abgeschlossen. Ergebnisse in 'literaturanalyse_ergebnisse.txt' gespeichert.")
