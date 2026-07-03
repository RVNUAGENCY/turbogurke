# TURBOGURKE — Twitch-Overlay-Paket im GTA-Stil

## Rolle & Kontext
Du bist Brand- und Broadcast-Designer für den deutschen Gaming-Streamer **TURBOGURKE**. Entwirf ein komplettes Twitch-Overlay-Paket im Look von Grand Theft Auto (GTA V/VI). Aufbau wie ein klassisches Premium-Overlay-Bundle: **alle Screens teilen sich EINE zusammenhängende illustrierte Szene** — pro Screen ändern sich nur Bildausschnitt und Headline.

## Die Szene (Herzstück)
Eine nächtliche GTA-Straßenszene im Cel-Shading-Stil (dicke schwarze Outlines, wie die vorhandenen Emotes): Los-Santos-artige Straße, Fassaden in Dunkelnavy/Teal, Neonschilder und Leuchtreklamen — das größte Schild ist **„TURBOGURKE" in Pricedown als Neon-Leuchtreklame**. Das Gurken-Maskottchen (mit Wasserpistole) lehnt irgendwo in der Szene, ein Auto parkt am Straßenrand, Comic-Explosions-Akzente am Himmel/als Deko. Neon-Lime dominiert die Lichtstimmung.

## Marke (verbindlich)
- Schriftzug exakt **„TURBOGURKE"** in Versalien — **ohne „21"** (der alte Name „TurboGurke21" ist tot).
- **Typografie:** Headlines/Wordmark in **Pricedown** (GTA-Font). Fertig gerenderte Wordmark-PNGs liegen im Repo unter `brand/wordmark/` (`turbogurke-wordmark-lime-glow.png`, `-lime.png`, `-white.png`) — direkt verwenden statt den Font nachzubauen. UI-/Fließtext: schmale cleane Sans (z. B. Barlow Condensed).
- **Basis-Palette:** Neon-Lime `#B0F010`–`#C0F020` (dominante Neonfarbe), Highlight `#E0F040`, Gurken-Grün `#30B000`, Dunkelgrün `#007000`, Dunkelnavy `#1E2F3F`, Teal `#1F6050`, Schwarz `#000000`, Weiß `#F0F0F0`. Zusätzliche Akzentfarben (Neon-Pink, Cyan, Rot fürs WASTED-Element usw.) sind erlaubt — solange **Neon-Lime klar die dominante Markenfarbe bleibt**.
- **Explosionen statt Blitze:** Die Blitz-Motive der alten Assets sind Legacy. Deko-Effekte sind Comic-Explosionen (Cel-Shading, dicke Outlines).
- **Maskottchen:** grinsende grüne Essiggurke, dunkle Biker-Jacke mit Lime-Piping, glühende Augen — hält als offizielles Markenelement eine **Comic-Wasserpistole**.
- Nicht verwenden: „21" im Schriftzug, den alten Graffiti-Font, Blitz-Deko.

## Referenz-Assets (GitHub, raw laden)
`https://raw.githubusercontent.com/RVNUAGENCY/turbogurke/main/` + Ordner `brand/wordmark/` (fertige Pricedown-Wordmarks), `brand/badges/` (3 Sub-Badges), `brand/emotes/static/` (12 Emotes), `brand/emotes/animated/` (5 GIFs), `brand/logo/` (altes Logo — zeigt noch „TurboGurke21" im Graffiti-Font, nur als Stil-Referenz fürs Maskottchen nutzen, Schriftzug nie übernehmen).

## Deliverables (genau dieses Paket)
1. **Starting-Soon-Screen** 1920×1080 — Szene + große Pricedown-Headline „STARTING SOON", Platz für Countdown.
2. **Offline-Screen** 1920×1080 — Headline „OFFLINE".
3. **Ending-Soon-Screen** 1920×1080 — Headline „ENDING SOON".
4. **Be-Right-Back-Screen** 1920×1080 — Headline „RIGHT BACK".
   → Alle vier Screens nutzen dieselbe Szene mit unterschiedlichen Ausschnitten/Tageslicht-Nuancen; Headlines mit Neon-Glow und leichtem Glitch.
5. **Webcam-Frame (16:9) + großer Screen-/Gameplay-Frame** — Neon-Rahmen mit Lime-Glow auf Navy, dazu eine schmale Label-Leiste (Name/!commands).
6. **Alert-Boxen (6):** New Follower, New Subscriber, Viewer Raid, New Cheer, New Donation, Viewer Host — einheitliches Design (Navy-Panel, Lime-Neonrand, Pricedown-Label, Slot für `{name}`/`{count}`), animierbar gedacht.
7. **„STAY CONNECTED"-Socials-Banner** — Pricedown-Schriftzug + Icon-Reihe (Discord, YouTube, TikTok, X/Insta).
8. **Kanal-Panels (8, 320 px breit):** About Me, Achievements, All Links, Specs, Bits, Donations, Charity, Contact — im GTA-Pausemenü-Button-Stil.
9. **Animierter Stinger (Szenenübergang):** **WASTED-Style, aber flashy** — das Bild desaturiert schlagartig (GTA-Death-Screen-Effekt) mit kurzem Kamera-Shake/Glitch, dann slammt der Pricedown-Schriftzug „TURBOGURKE" mit Wucht ins Bild — dahinter eine Comic-Explosion, die das Frame füllt und den Szenenwechsel kaschiert. Gern mit dem klassischen WASTED-Rot-Ton im Desaturierungs-Moment, Auflösung in Lime. ~0,5–1 s, als Keyframe-Sequenz (4–6 Frames) konzipieren.

## Technik / OBS-Praxis
Frames, Alerts und Banner auf transparentem Hintergrund; sichere Ränder ~5 %; Texte auch in 480p lesbar (fette Outlines, hoher Kontrast); Glow als Akzent, nie flächig; alle animierten Teile als Keyframe-Konzepte anlegen. Screen-Headlines englisch (wie oben), sonstige Texte deutsch.

## Selbstcheck vor Abgabe
Prüfe jedes Frame: keine „21", Wordmark/Headlines in Pricedown (Renders aus `brand/wordmark/` genutzt), keine Blitz-Deko, Neon-Lime dominiert, konsistente Szene über alle Screens.

## Ausblick (mitdenken, nicht bauen)
Aus demselben Design-System entsteht als Nächstes ein Discord-Server-Branding (Server-Icon, Banner, Rollen-Icons) — Szene, Farb-Tokens und Komponenten so anlegen, dass sie sich direkt übertragen lassen.
