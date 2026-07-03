# TURBOGURKE — Twitch-Stream-Overlay im GTA-Stil

## Rolle & Kontext
Du bist Brand- und Broadcast-Designer für den deutschen Gaming-Streamer **TURBOGURKE**. Entwirf ein komplettes, in sich konsistentes Twitch-Overlay-Paket im Look von Grand Theft Auto (GTA V/VI): HUD-Ästhetik, Pricedown-Typografie, Loading-Screen-Illustrationen — aber zu 100 % in den Markenfarben, niemals in GTA-Orange oder Rot.

## Referenz-Assets (GitHub, raw laden)
`https://raw.githubusercontent.com/RVNUAGENCY/turbogurke/main/` + Ordner `brand/logo/`, `brand/badges/` (3 Sub-Badges), `brand/emotes/static/` (12 Emotes), `brand/emotes/animated/` (5 GIFs).

**Achtung — Alt-Branding in den Referenzen:**
- Das Logo (`brand/logo/turbogurke-logo-2000px.png`) zeigt noch den alten Namen „TurboGurke21", einen **roten Blaster** und einen Graffiti-Font. Nutze es ausschließlich als Stil-Referenz fürs Maskottchen (Linienführung, Cel-Shading, Glow) — niemals 1:1 einbinden.
- `badge-3-*.png` enthält denselben roten Blaster — nicht verwenden.
- `emote-anim-3.gif` zeigt den roten Blaster (plus Blitze) — nicht einbinden, auch nicht in Emote-Slots. `emote-anim-5.gif` enthält einen Stachelschläger — ebenfalls weglassen. Animierte Emotes generell vor Einbindung einzeln gegen die Don't-Liste prüfen.
- `emote-05` (rotes Herz) und `emote-12` (rote Rauten in der Krone) nur nach vollständiger Umfärbung auf die Palette verwenden, sonst weglassen.
- Die **Blitz-Motive** der alten Assets sind Legacy: In allen neuen Designs ersetzen **Comic-Explosionen** die Blitze.

## Harte Constraints (Do / Don't)
- **DO:** Schriftzug exakt „TURBOGURKE" in Versalien. Wordmark & Headlines im **GTA-Font** (Pricedown bzw. nächstliegende Alternative). Explosionen als wiederkehrendes Deko-Element: Cel-Shading-Comic-Explosionen mit dicken schwarzen Outlines in Neon-Lime/Grün/Weiß. Lime-Glow als Akzent. Die **Wasserpistole** ist offizielles Marken-Element: Das Maskottchen hält eine Comic-Wasserpistole — ausschließlich in Markenfarben (Lime/Teal/Navy).
- **DON'T:** Kein Rot und kein Orange in jeder Form. Keine echten Waffen — die einzige erlaubte „Waffe" ist die Wasserpistole in Markenfarben; der alte rote Blaster bleibt verboten. Keine „21" im Schriftzug. **Keine Blitze.** Nicht der alte Graffiti-Font. Keine Farben außerhalb der Palette.

## Farbpalette (verbindlich, Hex)
- Neon-Lime `#B0F010`–`#C0F020`: Explosionen, Glow, Headlines
- Highlight `#E0F040`: hellste Glanzpunkte, Explosions-Kerne
- Gurken-Grün `#30B000`: Maskottchen-Körper, Primärflächen
- Dunkelgrün `#007000`: Schatten
- Dunkelnavy `#1E2F3F`: Panels, Jacke
- Teal `#1F6050`: Sekundärflächen
- Schwarz `#000000`: Outlines, Hintergründe
- Weiß `#F0F0F0`: UI-Text, Kontraste

## Typografie
- **Display (Wordmark, Headlines, Alerts):** Pricedown (der GTA-Logo-Font) — Neon-Lime mit fetter schwarzer Outline und dezentem Glow.
- **UI-Text (HUD-Werte, Fließtext):** schmale, cleane Sans (z. B. Barlow Condensed) in Weiß.

## GTA-Übersetzung (Kern der Aufgabe)
- **Webcam-Rahmen** als GTA-Minimap: abgerundetes Rechteck, Lime-Rand, kleiner Spielerpfeil, dezente Straßen-Textur in Navy/Teal.
- **Alerts:** Sub = „MISSION PASSED"-Banner; Follow = „NEUER KOMPLIZE: {name}"; Raid = blinkende Wanted-Sterne + „FAHNDUNGSLEVEL STEIGT: {name} FÄHRT MIT {count} LEUTEN VOR"; Donation/Bits = GTA-Geld-Counter, der in Lime hochtickt („+€50"). Je 2–3 deutsche Textvarianten.
- **Sub-Goal:** 5 Wanted-Sterne, die sich mit dem Fortschritt Lime füllen.
- **Chat-Box:** GTA-Phone-UI — Navy-Panel `#1E2F3F`, Usernames in Neon-Lime, lesbar ab ~14 px.
- **BRB-Screen:** WASTED-Parodie — Bild desaturiert, riesiges **„EINGELEGT"** in Pricedown.
- **Starting-Soon-/Ende-Screen:** GTA-Loading-Screen-Art — Cel-Shading-Kacheln mit dem Maskottchen (Stil der Emotes: dicke Outlines, Lime-Glow, Explosionen im Hintergrund), Ladebalken in Lime, „GLEICH GEHT'S LOS" bzw. „STREAM BEENDET — MISSION PASSED" + Slot für Raid-Ziel.
- **Event-Ticker:** schmale HUD-Leiste unten im Stil der Geld-Anzeige (letzter Sub, letzte Dono).
- **Stinger-Transition:** Explosion-Burst-Wipe — eine limegrüne Comic-Explosion füllt das Bild (3–4 Keyframes, ~0,5–1 s).

## Deliverables (Priorität absteigend)
1. **Neues Logo/Wordmark-Lockup:** „TURBOGURKE" im GTA-Font, Maskottchen mit Wasserpistole in Markenfarben, Cel-Shading-Explosion statt Blitzen im Hintergrund.
2. **Ingame-Overlay** 1920×1080, transparent: schmale HUD-Rahmen an den Rändern, Minimap-Webcam in 16:9 **und** 4:5, Ticker, Sub-Goal-Sterne. Bildmitte und Spiel-HUD-Zonen (Minimap unten links, HP/Muni unten rechts) bleiben frei.
3. **Starting-Soon-, BRB-(„EINGELEGT")- und Ende-Screen** 1920×1080.
4. **Just-Chatting-Szene** — Cam groß, Chat-Spalte, Ticker.
5. **Alert-Set** (Follow / Sub / Resub / Raid / Bits / Donation), je ~800×300 als Browser-Source, mit Emote-Slot.
6. **Chat-Widget-Skin** (Phone-UI).
7. **Stinger-Transition** als Keyframe-Konzept.
8. **Kanal-Panels** (320 px breit): Über mich, Regeln, Specs, Socials, Spenden — im GTA-Pausemenü-Button-Stil.
9. **Offline-Banner** 1920×1080.
10. **Style-Guide-Frame:** Farb-Tokens, Typo-Hierarchie, Ecken-Radien, Outline-Stärken, Glow-Intensität als wiederverwendbare Design-Tokens.

## Technik / OBS-Praxis
Overlays auf transparentem Hintergrund; sichere Ränder ~5 %; Texte auch in 480p lesbar (fette Outlines, hoher Kontrast); Glow als Akzent, nie flächig; animierte Teile (Stinger, Explosions-Loops) als Keyframe-Konzepte anlegen. Alle Overlay-Texte auf Deutsch.

## Selbstcheck vor Abgabe
Prüfe jedes Frame: kein Rot/Orange, keine Blitze, keine „21", keine Waffe außer der Wasserpistole in Markenfarben, Wordmark im GTA-Font, ausschließlich Palette-Hex.

## Ausblick (mitdenken, nicht bauen)
Aus demselben Design-System entsteht als Nächstes ein Discord-Server-Branding (Server-Icon, Banner, Rollen-Icons) — Tokens und Komponenten so anlegen, dass sie sich direkt übertragen lassen.
