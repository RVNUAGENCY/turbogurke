#!/usr/bin/env node
/**
 * Climb Journal — Riot-API-Proxy & Static Server (zero dependencies, Node >= 18)
 *
 *   RIOT_API_KEY=RGAPI-... node server.js        → http://localhost:3000
 *
 * Der Key bleibt auf dem Server; der Browser spricht nur mit /api/*.
 * Match-Details werden in ./cache/ abgelegt (Matches sind unveränderlich) — spart Rate-Limit.
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

/* ---------- config ---------- */
const ROOT = __dirname;
const envFile = path.join(ROOT, '.env');
if (fs.existsSync(envFile)) {
  for (const line of fs.readFileSync(envFile, 'utf8').split('\n')) {
    const m = line.match(/^\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*?)\s*$/i);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2].replace(/^["']|["']$/g, '');
  }
}
const KEY = process.env.RIOT_API_KEY || '';
const PORT = Number(process.env.PORT || 3000);
const CACHE_DIR = path.join(ROOT, 'cache');
fs.mkdirSync(CACHE_DIR, { recursive: true });

const PLATFORMS = {
  euw1: 'europe', eun1: 'europe', tr1: 'europe', ru: 'europe', me1: 'europe',
  na1: 'americas', br1: 'americas', la1: 'americas', la2: 'americas',
  kr: 'asia', jp1: 'asia',
  oc1: 'sea', sg2: 'sea', tw2: 'sea', vn2: 'sea', ph2: 'sea', th2: 'sea',
};
const POS = { TOP: 'Top', JUNGLE: 'Jungle', MIDDLE: 'Mid', BOTTOM: 'ADC', UTILITY: 'Support' };
const CHAMP_FIX = {
  MonkeyKing: 'Wukong', Nunu: 'Nunu & Willump', Renata: 'Renata Glasc', Chogath: "Cho'Gath", Kaisa: "Kai'Sa",
  KSante: "K'Sante", Velkoz: "Vel'Koz", Khazix: "Kha'Zix", RekSai: "Rek'Sai", Belveth: "Bel'Veth", Kogmaw: "Kog'Maw",
  FiddleSticks: 'Fiddlesticks', Leblanc: 'LeBlanc', JarvanIV: 'Jarvan IV', DrMundo: 'Dr. Mundo',
};
const champName = n => CHAMP_FIX[n] || n.replace(/([a-z])([A-Z])/g, '$1 $2');

/* ---------- riot fetch with rate-limit handling ---------- */
let queue = Promise.resolve();
const gap = ms => new Promise(r => setTimeout(r, ms));
async function riot(url, attempt = 0) {
  // serialise requests with a small gap: dev keys allow 20/s & 100/2min
  const run = queue.then(async () => {
    const res = await fetch(url, { headers: { 'X-Riot-Token': KEY } });
    await gap(60);
    return res;
  });
  queue = run.catch(() => {});
  const res = await run;
  if (res.status === 429 && attempt < 3) {
    const wait = Number(res.headers.get('retry-after') || 2) * 1000;
    await gap(wait);
    return riot(url, attempt + 1);
  }
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    const err = new Error(`Riot ${res.status} for ${url.replace(/\?.*$/, '')}: ${body.slice(0, 200)}`);
    err.status = res.status;
    throw err;
  }
  return res.json();
}
function cached(key, loader) {
  const f = path.join(CACHE_DIR, key.replace(/[^\w.-]/g, '_') + '.json');
  if (fs.existsSync(f)) return Promise.resolve(JSON.parse(fs.readFileSync(f, 'utf8')));
  return loader().then(d => { fs.writeFileSync(f, JSON.stringify(d)); return d; });
}

/* ---------- api handlers ---------- */
async function summoner(q) {
  const platform = (q.get('region') || 'euw1').toLowerCase();
  const routing = PLATFORMS[platform];
  if (!routing) throw Object.assign(new Error('Unbekannte Region'), { status: 400 });
  const name = q.get('name'), tag = q.get('tag');
  if (!name || !tag) throw Object.assign(new Error('name und tag erforderlich'), { status: 400 });
  const acc = await riot(`https://${routing}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/${encodeURIComponent(name)}/${encodeURIComponent(tag)}`);
  const sum = await riot(`https://${platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/${acc.puuid}`);
  let entries = [];
  try { entries = await riot(`https://${platform}.api.riotgames.com/lol/league/v4/entries/by-puuid/${acc.puuid}`); }
  catch (e) { if (sum.id) entries = await riot(`https://${platform}.api.riotgames.com/lol/league/v4/entries/by-summoner/${sum.id}`); else throw e; }
  const solo = entries.find(e => e.queueType === 'RANKED_SOLO_5x5');
  const flex = entries.find(e => e.queueType === 'RANKED_FLEX_SR');
  const norm = e => e && { tier: e.tier[0] + e.tier.slice(1).toLowerCase(), rank: e.rank, lp: e.leaguePoints, wins: e.wins, losses: e.losses };
  return { puuid: acc.puuid, gameName: acc.gameName, tagLine: acc.tagLine, level: sum.summonerLevel, iconId: sum.profileIconId, platform, solo: norm(solo), flex: norm(flex) };
}

async function matches(q) {
  const platform = (q.get('region') || 'euw1').toLowerCase();
  const routing = PLATFORMS[platform];
  const puuid = q.get('puuid');
  if (!routing || !puuid) throw Object.assign(new Error('puuid und region erforderlich'), { status: 400 });
  const count = Math.min(40, Number(q.get('count') || 20));
  const queueId = q.get('queue') || '420';
  const known = new Set((q.get('known') || '').split(',').filter(Boolean));
  const ids = await riot(`https://${routing}.api.riotgames.com/lol/match/v5/matches/by-puuid/${puuid}/ids?queue=${queueId}&start=0&count=${count}`);
  const fresh = ids.filter(id => !known.has(id));
  const out = [];
  for (const id of fresh) {
    const m = await cached(id, () => riot(`https://${routing}.api.riotgames.com/lol/match/v5/matches/${id}`));
    const me = m.info.participants.find(p => p.puuid === puuid);
    if (!me) continue;
    let cs10 = null, gold10diff = null;
    if (m.info.gameDuration >= 600) {
      try {
        const tl = await cached(id + '_tl', () => riot(`https://${routing}.api.riotgames.com/lol/match/v5/matches/${id}/timeline`));
        const fr = tl.info.frames[10];
        const opp = m.info.participants.find(p => p.teamId !== me.teamId && p.teamPosition === me.teamPosition);
        if (fr) {
          const f = fr.participantFrames[me.participantId];
          cs10 = f.minionsKilled + f.jungleMinionsKilled;
          if (opp) gold10diff = f.totalGold - fr.participantFrames[opp.participantId].totalGold;
        }
      } catch (e) { /* timeline optional */ }
    }
    const opp = m.info.participants.find(p => p.teamId !== me.teamId && p.teamPosition === me.teamPosition);
    const remake = m.info.gameDuration < 300 || me.gameEndedInEarlySurrender;
    out.push({
      riotId: id,
      date: new Date(m.info.gameStartTimestamp).toISOString().slice(0, 10),
      ts: m.info.gameStartTimestamp,
      duration: m.info.gameDuration,
      queue: m.info.queueId,
      champ: champName(me.championName),
      role: POS[me.teamPosition] || '',
      enemy: opp ? champName(opp.championName) : '',
      result: remake ? 'Remake' : me.win ? 'Win' : 'Loss',
      k: me.kills, d: me.deaths, a: me.assists,
      cs: me.totalMinionsKilled + me.neutralMinionsKilled,
      cs10, gold10diff,
      vision: me.visionScore,
      dmg: me.totalDamageDealtToChampions,
      deathsEarly: null,
    });
  }
  return { ids, games: out };
}

/* ---------- http ---------- */
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.json': 'application/json', '.css': 'text/css', '.png': 'image/png', '.md': 'text/plain; charset=utf-8' };
http.createServer(async (req, res) => {
  const u = new URL(req.url, `http://${req.headers.host}`);
  const json = (code, obj) => { res.writeHead(code, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }); res.end(JSON.stringify(obj)); };
  try {
    if (u.pathname === '/api/health') return json(200, { ok: true, keyConfigured: Boolean(KEY) });
    if (u.pathname.startsWith('/api/')) {
      if (!KEY) return json(503, { error: 'RIOT_API_KEY fehlt. In .env eintragen und Server neu starten.' });
      if (u.pathname === '/api/summoner') return json(200, await summoner(u.searchParams));
      if (u.pathname === '/api/matches') return json(200, await matches(u.searchParams));
      return json(404, { error: 'Unbekannter Endpoint' });
    }
    // static
    let p = u.pathname === '/' ? '/index.html' : u.pathname;
    const file = path.normalize(path.join(ROOT, p));
    if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end('Not found'); }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(file)] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  } catch (e) {
    const status = e.status === 404 ? 404 : e.status === 403 ? 403 : e.status === 429 ? 429 : 500;
    const hint = e.status === 403 ? ' — Key abgelaufen oder ungültig? Development-Keys laufen nach 24 h ab.' : e.status === 404 ? ' — Riot-ID (Name#TAG) oder Region prüfen.' : '';
    json(status, { error: e.message + hint });
  }
}).listen(PORT, () => {
  console.log(`Climb Journal läuft auf http://localhost:${PORT}`);
  if (!KEY) console.log('⚠  RIOT_API_KEY fehlt — Live-Sync deaktiviert. .env anlegen: RIOT_API_KEY=RGAPI-...');
});
