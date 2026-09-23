// ============================================================
//  TURBOGURKE — League-Daten
//  Nur diese Datei anpassen, der Rest der Seite baut sich selbst.
//  (Aktuell Beispielwerte — trag deine echten Zahlen ein.)
// ============================================================

window.LEAGUE_DATA = {
  player: {
    riotId: "TURBOGURKE",
    tag: "EUW",
    region: "EUW",
    level: 412,
    mainRole: "Mid",
    secondRole: "Jungle",
    // Links für die Buttons oben (leer lassen = Button ausblenden)
    opgg: "https://www.op.gg/summoners/euw/TURBOGURKE-EUW",
    ugg: "https://u.gg/lol/profile/euw1/TURBOGURKE-EUW/overview",
    twitch: "https://twitch.tv/turbogurke",
    live: false,
  },

  // Ranglisten — tier: Iron | Bronze | Silver | Gold | Platinum | Emerald | Diamond | Master | Grandmaster | Challenger
  ranked: [
    { queue: "Solo/Duo", tier: "Emerald", division: "II", lp: 64, wins: 118, losses: 101 },
    { queue: "Flex",     tier: "Platinum", division: "I", lp: 22, wins: 31,  losses: 27 },
  ],
  peak: "Diamond IV",

  // LP-Verlauf der letzten Tage (Solo/Duo). Label + Gesamt-LP-Wert.
  // Gesamt-LP = fortlaufende Zahl, damit Auf-/Abstiege sichtbar sind (z. B. Emerald IV 0 LP = 0).
  lpHistory: [
    { label: "01.09.", lp: 112 }, { label: "03.09.", lp: 141 }, { label: "05.09.", lp: 128 },
    { label: "07.09.", lp: 166 }, { label: "09.09.", lp: 190 }, { label: "11.09.", lp: 172 },
    { label: "13.09.", lp: 205 }, { label: "15.09.", lp: 231 }, { label: "17.09.", lp: 219 },
    { label: "19.09.", lp: 248 }, { label: "21.09.", lp: 264 },
  ],

  // Champion-Pool — name = Data-Dragon-ID (z. B. "MonkeyKing" für Wukong, "Kaisa" für Kai'Sa)
  champions: [
    { name: "Ahri",       display: "Ahri",     games: 64, wins: 38, k: 7.1, d: 4.2, a: 8.3, cs: 7.9 },
    { name: "Sylas",      display: "Sylas",    games: 41, wins: 23, k: 8.4, d: 5.6, a: 6.1, cs: 7.2 },
    { name: "LeeSin",     display: "Lee Sin",  games: 33, wins: 16, k: 6.2, d: 5.1, a: 9.4, cs: 5.8 },
    { name: "Viktor",     display: "Viktor",   games: 28, wins: 17, k: 6.8, d: 3.9, a: 7.7, cs: 8.4 },
    { name: "Yone",       display: "Yone",     games: 19, wins: 8,  k: 7.9, d: 6.3, a: 4.8, cs: 7.6 },
    { name: "Nidalee",    display: "Nidalee",  games: 14, wins: 9,  k: 7.3, d: 4.4, a: 7.0, cs: 6.1 },
  ],

  // Letzte Matches — result: "win" | "loss"
  matches: [
    { champ: "Ahri",   display: "Ahri",    result: "win",  queue: "Solo/Duo", k: 11, d: 3, a: 9,  cs: 231, duration: "28:14", ago: "vor 2 Std.",  lp: +22 },
    { champ: "Ahri",   display: "Ahri",    result: "win",  queue: "Solo/Duo", k: 6,  d: 2, a: 14, cs: 245, duration: "31:40", ago: "vor 3 Std.",  lp: +21 },
    { champ: "Sylas",  display: "Sylas",   result: "loss", queue: "Solo/Duo", k: 5,  d: 7, a: 4,  cs: 188, duration: "26:02", ago: "vor 5 Std.",  lp: -18 },
    { champ: "Viktor", display: "Viktor",  result: "win",  queue: "Solo/Duo", k: 8,  d: 1, a: 10, cs: 276, duration: "33:51", ago: "gestern",     lp: +23 },
    { champ: "LeeSin", display: "Lee Sin", result: "loss", queue: "Flex",     k: 3,  d: 6, a: 11, cs: 142, duration: "29:30", ago: "gestern",     lp: -16 },
    { champ: "Ahri",   display: "Ahri",    result: "win",  queue: "Solo/Duo", k: 13, d: 4, a: 7,  cs: 212, duration: "25:18", ago: "vor 2 Tagen", lp: +22 },
    { champ: "Yone",   display: "Yone",    result: "loss", queue: "Solo/Duo", k: 7,  d: 9, a: 3,  cs: 201, duration: "30:05", ago: "vor 2 Tagen", lp: -19 },
    { champ: "Sylas",  display: "Sylas",   result: "win",  queue: "Solo/Duo", k: 9,  d: 4, a: 12, cs: 198, duration: "27:47", ago: "vor 3 Tagen", lp: +20 },
  ],

  // Stream-Plan
  schedule: [
    { day: "Mo", time: "19:00", title: "Ranked Grind" },
    { day: "Mi", time: "19:00", title: "Ranked Grind" },
    { day: "Fr", time: "20:00", title: "Clash / Flex mit Community" },
    { day: "So", time: "16:00", title: "Coaching & VOD-Review" },
  ],
};
