from lxml import etree
import csv

# XML-Datei einlesen --> Download Much Ado About Nothing von DraCor (https://www.dracor.org)
tree = etree.parse(r"Shakespeare_MuchAdoAboutNothing_DraCor.xml")

# Funktion zum Umwandeln von Listen aus xml-Elementen in Listen aus den Textelementen


def ListToText(list):
    return [element.text for element in list]

# Funktion zum Umwandeln von 2-dimensionalen Listen aus xml-Elementen in eine 2-dimensionale Liste aus den Textelementen


def TwoDListToText(list):
    return [ListToText(sentence) for sentence in list]

# Funktion zum Umwandeln von 3-dimensionalen Listen aus xml-Elementen in eine 3-dimensionale Liste aus den Textelementen


def ThreeDListToText(list):
    return [TwoDListToText(paragraph) for paragraph in list]

# Funktion, die den Sprecher zurück gibt für ein gegebenes w-Element
# Angepasste Version von Prompt 1 (siehe unten)


def get_speaker(word_element):
    # sp-Element ist parent von p-Element ist parent von w-Element
    sp_element = word_element.getparent().getparent()
    # Name des Sprechers als w-Element
    speaker_element = sp_element.find('.//speaker/w')
    if speaker_element is not None:
        return speaker_element.text
    return None  # Falls es keinen Sprecher gibt, wird None zurückgegeben


# Erstellen von Python-Listen aus der xml-Datei
fullSpokenText = []  # Liste aus allen Wörtern
sentenceList = []    # 2-dimensionale Liste aus allen Sätzen mit allen Wörtern
# 3-dimensionale Liste aus allen Paragraphen mit allen Sätzen (mit allen Wörtern)
paragraphsList = []

# Angepasste Version von Prompt 2
for sp in tree.xpath('.//sp'):  # Iteriert durch alle sp-Elemente in dem Dokument
    speaker = sp.xpath('.//speaker/w')
    sentences = []  # Liste von Sätzen für die paragraphsList
    current_sentence = []  # Liste von Wörtern für die sentenceList

    for p in sp.findall('.//p'):  # Iteriert durch alle paragraph-Elemente unter sp
        # und dann durch alle Elemente in p (Wörter, Satzzeichen, Leerzeichen, etc.)
        for element in p:
            if element.tag == 'w':
                fullSpokenText.append(element)
                # fügt den 1-dimensionalen Listen die Wörter des Satzes hinzu
                current_sentence.append(element)
            # Fügt den Satz nach einem beendenden Satzzeichen der sentences Liste hinzu
            elif element.tag == 'pc' and element.text in {'.', '!', '?'}:
                if current_sentence:
                    sentences.append(current_sentence)
                    current_sentence = []

        if current_sentence != None:  # Überprüfen, falls es in einem p-Element keine Wort-Elemente gibt => safety
            sentences.append(current_sentence)
            current_sentence = []

    if sentences:
        sentenceList.extend(sentences)  # sentenceList um den Satz erweitern
        paragraphsList.append(sentences)  # paragraphsList den Satz hinzufügen


# Figura Etymologica
figEtyList = []  # Liste von figurae etymologicae (?)
sentenceContextList = []  # Liste der gesammten Sätze, in denen das Stilmittel vorkommt
speakerList = []  # Liste der Sprecher der Sätze
# Set von einigen Ausnahmen, die nicht betrachtet werden sollen (z.B. "I", "me")
wrongType = {'#pno', '#pns', '#vvz', '#vvn', '#vvi', '#vvb', '#vvg'}

# Durch die Satz-Liste wird iteriert, da nur Stilmittel innerhalb eines Satzes beachtet werden sollen (und nicht z.B. über mehrere Sätze)
for sentence in sentenceList:
    # Iteriert durch die Anzahl der Wörter-1 => -1, da das aktuelle Wort mit Index i mit den nächsten mit Index i+1 verglichen wird
    for i in range(len(sentence)-1):
        figEty = []  # aktuelles Stilmittel

        # Zum Ausprobieren: eine if-Bedinung auskommentieren, eine einkommentieren
        # Erste if-Bedingung überprüft auch ob es das selbe Wort hintereinander ist und eine der Ausnahmen eintritt
        # if((sentence[i].get('lemma') == sentence[i+1].get('lemma') and sentence[i].tag == 'w') and (sentence[i].text.lower() != sentence[i+1].text.lower()) and (sentence[i].get('ana') not in wrongType)):
        if (sentence[i].get('lemma') == sentence[i+1].get('lemma') and sentence[i].tag == 'w'):
            # Die zwei Wörter, auf die die if-Bedingung zutrifft, werden als Liste gespeichert
            figEty = [[sentence[i], sentence[i+1]]]
            # Diese Liste wird dann der gesammten (2-dimensionalen) Liste hinzugefügt
            figEtyList.append(figEty)
            sentenceContextList.append(sentence)
            speakerList.append(get_speaker(sentence[i]))

# Erstellen der csv Datei
f_figEty = open("figuraeEtymologica.csv", "w", encoding="utf-8")
csv.register_dialect("custom", delimiter=",",
                     skipinitialspace=True, lineterminator='\n')
writer = csv.writer(f_figEty, dialect="custom")
# Spalten werden benannt
writer.writerow(['Figura', 'Speaker', 'Sentence'])

for i in range(len(figEtyList)):  # Iteriert len(figEtyList)-mal
    # Alle 3 Listen verweisen bei dem selben Index auf die selbe Stelle im Text
    writer.writerow([TwoDListToText(figEtyList[i]),
                    speakerList[i], ListToText(sentenceContextList[i])])

# Alliterations
# Gleiche Listenstruktur wie bei figura etymologica => setzt die zwei identischen Listen wieder auf []
allitList = []
sentenceContextList = []
speakerList = []

for sentence in sentenceList:  # Wieder wird durch die 2-dimensionale Liste iteriert, da nur Stilmittel innerhalb eines Satzes beachtet werden sollen
    allitPairs = []  # aktuelle Alliteration
    # Iteriert durch die Anzahl der Wörter-1 => -1, da das aktuelle Wort mit Index i mit den nächsten mit Index i+1 verglichen wird
    for i in range(len(sentence) - 1):
        # Wort Elemente werden der Einfachheit halber definiert
        firstWord = sentence[i]
        secondWord = sentence[i + 1]

        # Erster Buchstabe beider Wörter wird (unabhängig vom case) verglichen
        if firstWord.text[0].lower() == secondWord.text[0].lower():
            allitPairs.append([firstWord, secondWord])

    if allitPairs != []:  # Falls eine Alliteration gefunden wurde...
        # ... wird sie, der gesammte Satz und der Sprecher des Satzes den zugehörigen Listen hinzugefügt
        allitList.append(allitPairs)
        sentenceContextList.append(sentence)
        speakerList.append(get_speaker(sentence[0]))

# Passende csv Datei mit writer werden erstellt
f_allit = open("alliterations.csv", "w", encoding="utf-8")
csv.register_dialect("custom", delimiter=",",
                     skipinitialspace=True, lineterminator='\n')
writer = csv.writer(f_allit, dialect="custom")
# Spalten werden benannt
writer.writerow(['Alliteration', 'Speaker', 'Sentence'])

# Funktioniert identisch zur for-loop der figura etymologica, nur mit der neuen Liste
for i in range(len(allitList)):
    writer.writerow([TwoDListToText(allitList[i]),
                    speakerList[i], ListToText(sentenceContextList[i])])


# Anapher
# Ähnliche Listenstruktur wie bei Alliteration => setzt die zwei identischen Listen wieder auf []
anaphora = []
anaphoras = []
sentenceContextList = []
speakerList = []

# Iteriert durch die Anzahl der Sätze -1 => -1, da der Satz mit Index i und der nächste Satz mit Index i+1 miteinander verglichen werden
for i in range(len(sentenceList)-1):
    sentencePair = []
    # Vergleicht die ersten Wörter zwei aufeinander folgender Sätze
    if (sentenceList[i][0].text == sentenceList[i+1][0].text):
        # Erstellt eine Liste mit den zwei Sätzen der Anapher
        sentencePair = [ListToText(sentenceList[i]),
                        ListToText(sentenceList[i+1])]
        # Erstellt eine Liste mit den zwei Anfangswörtern
        anaphora = [sentenceList[i][0].text, sentenceList[i+1][0].text]
        # Fügt diese Liste der Liste aller Anaphern hinzu
        anaphoras.append(anaphora)
        sentenceContextList.append(sentencePair)
        speakerList.append(get_speaker(sentenceList[i+1][0]))
        anaphora = []

# Passende csv Datei und writer werden erstellt
f_ana = open("anaphoras.csv", "w", encoding="utf-8")
csv.register_dialect("custom", delimiter=",",
                     skipinitialspace=True, lineterminator='\n')
writer = csv.writer(f_ana, dialect="custom")
# Spalten werden benannt
writer.writerow(['Anaphora', 'Speaker of second sentence', 'Sentence'])
# Sprecher des zweiten Satzes wird hinzugefügt, da er rhethorisch auf den Vorherigen aufbaut (falls er von einer anderen Figur gesprochen wird)

# Funktioniert identisch zur for-loop der Alliteration, nur mit der neuen Liste
for i in range(len(anaphoras)-1):
    writer.writerow([anaphoras[i], speakerList[i], sentenceContextList[i]])

# Epiphora
# Ähnliche Listenstruktur wie bei Anapher => setzt die zwei identischen Listen wieder auf []
epiphora = []
epiphoras = []
sentenceContextList = []
speakerList = []

# Iteriert durch die Anzahl der Sätze -1 => -1, da der Satz mit Index i und der nächste Satz mit Index i+1 miteinander verglichen werden
for i in range(len(sentenceList)-1):
    sentencePair = []
    # Vergleicht die letzten Wörter zwei aufeinander folgender Sätze
    if (sentenceList[i][-1].text == sentenceList[i+1][-1].text):
        # Erstellt eine Liste mit den zwei Sätzen der Epipher
        sentencePair = [ListToText(sentenceList[i]),
                        ListToText(sentenceList[i+1])]
        # Erstellt eine Liste mit den zwei Endwörtern
        epiphora = [sentenceList[i][-1].text, sentenceList[i+1][-1].text]
        # Fügt diese Liste der Liste aller Anaphern hinzu
        epiphoras.append(epiphora)
        sentenceContextList.append(sentencePair)
        speakerList.append(get_speaker(sentenceList[i+1][-1]))
        epiphora = []

# Passende csv Datei und writer werden erstellt
f_ana = open("epiphoras.csv", "w", encoding="utf-8")
csv.register_dialect("custom", delimiter=",",
                     skipinitialspace=True, lineterminator='\n')
writer = csv.writer(f_ana, dialect="custom")
# Spalten werden benannt
writer.writerow(['Epiphora', 'Speaker of second sentence', 'Sentence'])

# Funktioniert identisch zur for-loop der Anapher, nur mit der neuen Liste
for i in range(len(epiphoras)-1):
    writer.writerow([epiphoras[i], speakerList[i], sentenceContextList[i]])

# # Promt 1, deepseek-r1, 03.02.2024, 17:10
# You are a professor of digital humanities and specialize in the analysis of dramas in Python using xml and the Python extension lxml. You get a play which follows the TEI standard. A simplified version of a sentence looks like this:
# <sp>
# 	<speaker>
# 		<w>Leonato<\w>
# 	<\speaker>
# 	<p>
# 		<w>I<\w>
# 		<w>learn<\w>
# 		<w>in<\w>
# 		<w>this<\w>
# 		<w>letter<\w>
# 	<\p>
# <\sp>
# You are given the task to write a function get_speaker(word_element) that returns the w-element of the speaker of any given w-element in p. In this simplified example this would be "Leonato".
#
# Prompt 2, deepseek-r1, 03.02.2024, 17:26, continuation of prompt 1
# You now want to create a one dimensional list of all the spoken text elements without spaces or punctuation. Also you want a two dimensional list which has each sentence as a own list (not only seperated by the sp, but also by punctuation like ".", "!" and "?") and a three dimensional list, which has a list of sentences spoken by the same person grouped together (like [[sentences by person A], [sentences by person B], [sentences by person A]], where the sentences are a two dimensional list of the previous type).
