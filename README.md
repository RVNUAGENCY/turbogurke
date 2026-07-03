# TURBOGURKE — Brand Assets

Offizielle Brand-Assets für **TURBOGURKE** (Twitch). Maskottchen: eine grinsende Turbo-Gurke mit Neon-Energie und dunkler Jacke.

> **Wichtig:** Die Marke heißt ab jetzt nur noch **TURBOGURKE** — ohne „21". Das alte Logo (`brand/logo/`) zeigt noch den alten Schriftzug „TurboGurke21" und dient nur als Stil-Referenz.

## Farbpalette

| Farbe | Hex | Verwendung |
|---|---|---|
| Neon-Lime (Glow) | `#B0F010` – `#C0F020` | Explosionen, Glow, Akzente, Schrift |
| Neon-Lime Hell | `#E0F040` | Highlights, Funken |
| Gurken-Grün | `#30B000` | Maskottchen-Körper, Flächen |
| Dunkelgrün | `#007000` | Schattierungen |
| Dunkelnavy | `#1E2F3F` | Jacke, dunkle Flächen, Panels |
| Teal | `#1F6050` | Sekundärflächen (Schild-Hintergrund) |
| Schwarz | `#000000` | Outlines, Hintergründe |
| Weiß | `#F0F0F0` | Zähne, Augen, Kontraste |

**Akzentfarben frei** (Stand Juli 2026): Das frühere Rot-Verbot ist aufgehoben. Zusätzliche Akzente (Neon-Pink, Cyan, Rot z. B. für WASTED-Elemente) sind erlaubt, solange Neon-Lime die dominante Markenfarbe bleibt.

**Keine Blitze mehr.** Die Blitz-Motive in den alten Assets sind Legacy — neue Designs verwenden stattdessen **Comic-Explosionen** (Cel-Shading, dicke schwarze Outlines) in Neon-Lime/Grün/Weiß.

**Wasserpistole statt Blaster.** Das Maskottchen hält als offizielles Markenelement eine Comic-Wasserpistole — sie ersetzt den alten Blaster (Legacy). Farblich bevorzugt in Markenfarben, Akzentfarben erlaubt.

**Typografie:** Wordmark und Headlines in **Pricedown** (GTA-Font) — fertige Renders in `brand/wordmark/` direkt verwenden; nicht mehr der alte Graffiti-Font des Logos. UI-/Fließtext in einer schmalen, cleanen Sans (z. B. Barlow Condensed).

Fertig gerenderte Pricedown-Wordmarks (transparente PNGs) liegen in `brand/wordmark/` (Lime mit Glow, Lime, Weiß). Die Font-Datei selbst liegt **nicht** im Repo — die [Typodermic-Lizenz](https://typodermicfonts.com/pricedown/) erlaubt gerenderte Logos, aber keine Weitergabe der TTF. Font offiziell laden: https://typodermicfonts.com/pricedown/

## Struktur

```
brand/
├── logo/                  # Hauptlogo 2000px (alte Version mit „21" + rotem Blaster — nur Stil-Referenz)
├── badges/                # 3 Sub-Badges (je 18/36/72/1000px)
│   ├── badge-1  → Gurken-Gesicht (freundlich)
│   ├── badge-2  → Gurke mit Jacke, zeigt auf dich
│   └── badge-3  → Gurke mit Blaster (alter Blaster, siehe Maskottchen-Update)
└── emotes/
    ├── static/            # 12 Emotes (je 28/56/112/1000px), u. a. „BIDDE?", King, Flex, Deal-with-it
    └── animated/          # 5 animierte GIF-Emotes
```

## Design-Richtung

- Look & Feel: **GTA-inspiriert** (Heist/Wanted-HUD-Ästhetik, Pricedown-Typografie, Loading-Screen-Illustrationen), kombiniert mit dem Neon-Lime-Glow der Marke
- Effekte: Explosionen statt Blitze
- Geplante Ableitungen: Twitch-Stream-Overlay-Paket, danach Discord-Server-Branding

Der fertige Design-Brief liegt in [`claude-design-prompt.md`](claude-design-prompt.md).
