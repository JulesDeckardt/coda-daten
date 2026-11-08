# coda-daten

Öffentliche Listendaten für Coda, eine private App für Filme, Serien und Bücher: Buchpreise, Bestenlisten,
Neuerscheinungen. Keine Schlüssel, keine persönlichen Daten.

Der Auftrag `Nachtrag` läuft montags und donnerstags (Neues) und in geraden Wochen sonntags (alles) und schreibt
`nachtrag.json`. Die App liest die Datei höchstens alle 12 Stunden und behält den letzten Stand.
