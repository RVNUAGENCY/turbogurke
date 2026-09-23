# Prompt: „Climb Journal" — das League-of-Legends-Improvement-Tool

## Rolle
Du bist Coach (Challenger-Niveau, Fokus Fundamentals & Deliberate Practice) **und** Produkt-Entwickler. Baue ein Tool, das einen ambitionierten Ranked-Spieler strukturiert Richtung Challenger führt — nicht durch Stats-Spam, sondern durch die Schleife **Ziel → Routine → Spielen → Review → Anpassen**.

## Nutzer & Job der Seite
Ein deutschsprachiger Solo-Queue-Spieler, der täglich spielt. Die Seite ist sein einziger Arbeitsplatz für Verbesserung: vor der Session öffnen (Fokus + Routine), nach jedem Game 60 Sekunden loggen, nach der Session 1 Review, sonntags Wochen-Review. Alles in **einer Datei**, offline-fähig, Daten lokal + Export/Import als JSON.

## Muss enthalten (Module)
1. **Heute** — Rank/LP-Tracking mit Ziel-Rang, aktives Lernziel als Tagesfokus, Tages-Routine als Checkliste, Streak, Kennzahlen (Winrate letzte 20, Review-Quote, Games heute), LP-Verlauf.
2. **Routine** — editierbare Phasen *Pre-Session / Session-Regeln / Post-Session* mit sinnvollen Defaults (Warm-up im Practice Tool, Fokus lesen, Stop-Loss-Regel, 1 Review pro Session …), Verlauf der letzten Wochen.
3. **Games** — Match-Log: Champion, Rolle, Gegner-Champion, Ergebnis, KDA, CS@10, LP, Tilt-Level, Hauptfehler-Kategorie, 1 Learning, Reviewed-Flag. Auswertung pro Champion, pro Matchup und Fehler-Muster.
4. **Champions** — Champion-Pool (Main / Backup / Lernen) mit Notiz-Sektionen: Wincondition, Combos, Power Spikes, Runen/Build, Wave-Plan, Do/Don't. **Matchups** pro Champion: Schwierigkeit, Plan Lvl 1–3, Laning-Muster, Punish-Fenster, Notizen — verknüpft mit der Winrate aus dem Log.
5. **Lernziele** — messbare Ziele (Metrik, Zielwert, Ist-Wert, Deadline, Status), 1–2 aktive Ziele als Fokus, Fortschritt sichtbar.
6. **Review** — geführter VOD-Review (Schritt für Schritt, Phasen-Checkliste, Death-Review-Fragen), Review-Notizen mit Timestamps, Takeaways die per Klick zu Lernzielen werden.
7. **Wochen-Review** — Wochenstatistik automatisch, häufigste Fehler der Woche, Reflexionsfragen, Fokus der nächsten Woche.
8. **Wissen** — kuratierte Fundamentals als Nachschlagewerk: Wave Management, Trading, Tempo & Recall, Objectives & Timer, Vision, Macro/Sidelane, Mental & Session-Regeln, Champion-Pool-Regeln, Practice-Tool-Drills, „Wie reviewe ich richtig".
9. **Notizen** — freie Notizen mit Tags und Suche (Ideen, Videos, Coaching-Erkenntnisse).
10. **Daten** — Export/Import JSON, Beispieldaten entfernen, Reset.

## Design
Eigene, zu League passende Identität: dunkler Hextech-Grund, Gold/Teal als Akzente, Display-Schrift mit Beaufort-Charakter (Cinzel), klare Sans für Text, tabellarische Ziffern. Kein Streamer-Branding. Sidebar auf Desktop, Tab-Leiste auf Mobile. Öffnet mit sichtbaren Beispieldaten (als solche markiert), damit man sofort sieht, wie es benutzt wird.

## Qualität
Vanilla HTML/CSS/JS, keine Frameworks, localStorage mit try/catch, alles per Tastatur bedienbar, funktioniert bei 400 px Breite. UI-Texte deutsch, League-Begriffe englisch (Wave, Recall, Matchup …).
