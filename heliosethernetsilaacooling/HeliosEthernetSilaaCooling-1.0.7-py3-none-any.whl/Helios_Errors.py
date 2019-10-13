"""
@ Stefanie Fiedler 2019
@ Alexander Teubert 2019
Version vom 26.09.2019

for Hochschule Anhalt, University of Applied Sciences
in coorperation with axxeo GmbH

This module converts the integer-coded responses of the Helios KWL to the error
requests, issued by the master
"""
def errortable(error_string):
    #check, if the error code correlates to a given error message

    table = {
    1 : 'Drehzahlfehler Lüfter \"Zuluft\" (Aussenluft)',
    2 : 'Drehzahlfehler Lüfter \"Abluft\" (Fortluft)',
    4 : 'SD-Karten Fehler beim Schreiben der E-Eprom-Daten bei \"FLASH-Ringpuffer VOLL\"',
    5 : "Bus Überstrom",
    7 : 'BASIS: 0-Xing Fehler VHZ EH  (0-Xing = Zero-Crossing, Null-Durchgangskennung)',
    8 : "Erw. Modul (VHZ): 0-Xing Fehler VHZ EH",
    9 : "Erw. Modul (NHZ): 0-Xing Fehler NHZ EH",
    10 : 'BASIS: Interner Temp-Sensorfehler - (T1) -Aussenluft- (fehlt od. Kabelbruch)',
    11 : "BASIS: Interner Temp-Sensorfehler - (T2) -Zuluft- (fehlt od. Kabelbruch)",
    12 : "BASIS: Interner Temp-Sensorfehler - (T3) -Abluft- (fehlt od. Kabelbruch)",
    13 : "BASIS: Interner Temp-Sensorfehler - (T4) -Fortluft- (fehlt od. Kabelbruch)",
    14 : "BASIS: Interner Temp-Sensorfehler - (T1) -Aussenluft- (Kurzschluss)",
    15 : "BASIS: Interner Temp-Sensorfehler - (T2) -Zuluft- (Kurzschluss)",
    16 : "BASIS: Interner Temp-Sensorfehler - (T3) -Abluft- (Kurzschluss)",
    17 : "BASIS: Interner Temp-Sensorfehler - (T4) -Fortluft- (Kurzschluss)",
    18 : "Erw. Modul als VHZ konfiguriert, aber nicht vorh. oder ausgefallen",
    19 : "Erw. Modul als NHZ konfiguriert, aber nicht vorh. oder ausgefallen",
    20 : "Erw. Modul (VHZ): Kanalfühler (T5) -Aussenluft- (fehlt od. Kabelbruch)",
    21 : "Erw. Modul (NHZ): Kanalfühler (T6) -Zuluft- (fehlt od. Kabelbruch)",
    22 : "Erw. Modul (NHZ): Kanalfühler (T7) -Rücklauf-WW-Register- (fehlt od. Kabelbruch)",
    23 : "Erw. Modul (VHZ): Kanalfühler (T5) -Aussenluft- (Kurzschluss)",
    24 : "Erw. Modul (NHZ): Kanalfühler (T6) -Zuluft- (Kurzschluss)",
    25 : "Erw. Modul (NHZ): Kanalfühler (T7) -Rücklauf-WW-Register- (Kurzschluss)",
    26 : "Erw. Modul (VHZ): Sicherheitsbegrenzer automatisch",
    27 : "Erw. Modul (VHZ): Sicherheitsbegrenzer manuell",
    28 : "Erw. Modul (NHZ): Sicherheitsbegrenzer automatisch",
    29 : "Erw. Modul (NHZ): Sicherheitsbegrenzer manuell",
    30 : "Erw. Modul (NHZ): Frostschutz WW-Reg. gemessen über WW-Rücklauf (T7) (Schaltschwelle per Variablenliste einstellbar z.B. < 7°C)",
    31 : "Erw. Modul (NHZ): Frostschutz WW-Reg. gemessen über Zuluft-Fühler (T6) (Schaltschwelle per Variablenliste einstellbar z.B. < 7°C)",
    32 : "Frostschutz externes WW Reg.: ( fest < 5°C nur PHI), gemessen entweder über (1.) Erw. Modul (NHZ): Zuluftkanal-Fühler (T6) oder (2.) BASIS: Zuluftkanal-Fühler (T2)"}

    return table[int(error_string)];

def warningtable(error_string):
    #check, if the warning code correlates to a given error message

    table = {1 : 'Interner Feuchtefuehler liefert keinen Wert',}

    return table[int(error_string)];

def infotable(error_string):
    #check, if the information code correlates to a given error message

    table = {
    1 : 'Filterwechsel',
    2 : 'Frostschutz WT',
    3 : 'SD-Karten Fehler',
    4 : 'Ausfallen des Externen Moduls (weitere Info in LOG-File)'}

    return table[int(error_string)];
