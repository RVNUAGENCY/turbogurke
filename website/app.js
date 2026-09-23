(function () {
  const D = window.LEAGUE_DATA;
  const DDRAGON = "https://ddragon.leagueoflegends.com/cdn/14.24.1/img/champion/";
  const TIER_COLORS = {
    Iron: "#6b5d57", Bronze: "#a0643c", Silver: "#8c9aa8", Gold: "#d4a32a", Platinum: "#2fa89a",
    Emerald: "#16a34a", Diamond: "#5b7cf0", Master: "#a855f7", Grandmaster: "#e0424f", Challenger: "#f5c542",
  };

  const $ = (sel) => document.querySelector(sel);
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const pct = (w, g) => (g ? Math.round((w / g) * 100) : 0);
  const kda = (k, d, a) => (d ? ((k + a) / d).toFixed(2) : "Perfekt");
  const champImg = (id, name, cls) =>
    `<img class="${cls}" src="${DDRAGON}${esc(id)}.png" alt="${esc(name)}" loading="lazy"
      onerror="this.outerHTML='<span class=&quot;${cls}&quot;>${esc(name).slice(0, 2)}</span>'" />`;

  // ---------- Profil ----------
  const p = D.player;
  $("#riot-id").textContent = p.riotId;
  $("#riot-tag").textContent = "#" + p.tag;
  $("#region").textContent = p.region;
  $("#level").textContent = "Lvl " + p.level;
  $("#roles").innerHTML = `Main <strong>${esc(p.mainRole)}</strong> · Zweitrolle <strong>${esc(p.secondRole)}</strong> · Peak <strong>${esc(D.peak)}</strong>`;
  $("#profile-links").innerHTML = [
    p.twitch && `<a class="btn primary" href="${esc(p.twitch)}" target="_blank" rel="noopener">Twitch</a>`,
    p.opgg && `<a class="btn" href="${esc(p.opgg)}" target="_blank" rel="noopener">OP.GG</a>`,
    p.ugg && `<a class="btn" href="${esc(p.ugg)}" target="_blank" rel="noopener">U.GG</a>`,
  ].filter(Boolean).join("");

  const pill = $("#live-pill");
  pill.href = p.twitch || "#";
  pill.textContent = p.live ? "Live" : "Offline";
  pill.classList.toggle("is-live", !!p.live);

  // ---------- KPIs (aus den letzten Matches + Rang) ----------
  const solo = D.ranked[0];
  const soloGames = solo.wins + solo.losses;
  const m = D.matches;
  const sum = (f) => m.reduce((s, x) => s + f(x), 0);
  const recentWins = m.filter((x) => x.result === "win").length;
  const avgK = sum((x) => x.k) / m.length, avgD = sum((x) => x.d) / m.length, avgA = sum((x) => x.a) / m.length;
  const lpNet = sum((x) => x.lp || 0);

  const kpis = [
    { label: "Winrate", value: pct(solo.wins, soloGames) + "%", sub: `${solo.wins} S · ${solo.losses} N`, cls: pct(solo.wins, soloGames) >= 50 ? "good" : "bad" },
    { label: "Ø KDA", value: kda(avgK, avgD, avgA), sub: `${avgK.toFixed(1)} / ${avgD.toFixed(1)} / ${avgA.toFixed(1)}` },
    { label: "Letzte " + m.length, value: `${recentWins}–${m.length - recentWins}`, sub: `${lpNet >= 0 ? "+" : ""}${lpNet} LP`, cls: lpNet >= 0 ? "good" : "bad" },
    { label: "Spiele", value: soloGames, sub: "Solo/Duo diese Season" },
  ];
  $("#kpis").innerHTML = kpis.map((k) => `
    <div class="card kpi">
      <div class="kpi-label">${esc(k.label)}</div>
      <div class="kpi-value ${k.cls || ""}">${esc(k.value)}</div>
      <div class="kpi-sub">${esc(k.sub)}</div>
    </div>`).join("");

  // ---------- Rang-Karten ----------
  $("#rank-cards").innerHTML = D.ranked.map((r) => {
    const g = r.wins + r.losses, wr = pct(r.wins, g);
    const apex = ["Master", "Grandmaster", "Challenger"].includes(r.tier);
    return `
    <article class="card rank">
      <div class="emblem" style="--tier:${TIER_COLORS[r.tier] || "#555"}">${esc(r.tier[0])}${apex ? "" : esc(r.division)}</div>
      <div class="rank-body">
        <div class="rank-queue">${esc(r.queue)}</div>
        <div class="rank-tier">${esc(r.tier)} ${apex ? "" : esc(r.division)} <span class="muted" style="font-size:.7em">· ${r.lp} LP</span></div>
        <div class="rank-meta"><span>${apex ? "LP" : "Bis zum Aufstieg"}</span><span>${apex ? r.lp : `${r.lp}/100`}</span></div>
        <div class="bar" role="img" aria-label="${r.lp} von 100 LP"><span style="width:${Math.min(r.lp, 100)}%"></span></div>
        <div class="rank-meta"><span>${r.wins} S · ${r.losses} N</span><span class="${wr >= 50 ? "good" : "bad"}">${wr}% WR</span></div>
      </div>
    </article>`;
  }).join("") + `<p class="peak">Season-Peak: <strong>${esc(D.peak)}</strong></p>`;

  // ---------- LP-Chart ----------
  function drawChart() {
    const box = $("#lp-chart");
    const data = D.lpHistory;
    const W = box.clientWidth || 600, H = Math.max(box.clientHeight, 220);
    const pad = { t: 12, r: 12, b: 26, l: 40 };
    const vals = data.map((d) => d.lp);
    let lo = Math.min(...vals), hi = Math.max(...vals);
    const span = hi - lo || 1;
    lo = Math.floor((lo - span * 0.15) / 25) * 25; hi = Math.ceil((hi + span * 0.1) / 25) * 25;
    const x = (i) => pad.l + (i / (data.length - 1)) * (W - pad.l - pad.r);
    const y = (v) => pad.t + (1 - (v - lo) / (hi - lo)) * (H - pad.t - pad.b);
    const ticks = 4, step = (hi - lo) / ticks;
    const pts = data.map((d, i) => `${x(i).toFixed(1)},${y(d.lp).toFixed(1)}`);
    const every = Math.ceil(data.length / (W < 500 ? 4 : 7));

    box.innerHTML = `
      <svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="LP-Verlauf von ${data[0].lp} auf ${data[data.length - 1].lp}">
        <defs><linearGradient id="lpFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#b8f018" stop-opacity=".28"/><stop offset="1" stop-color="#b8f018" stop-opacity="0"/>
        </linearGradient></defs>
        <g class="grid axis">${Array.from({ length: ticks + 1 }, (_, i) => {
          const v = lo + i * step, yy = y(v).toFixed(1);
          return `<line x1="${pad.l}" x2="${W - pad.r}" y1="${yy}" y2="${yy}"/><text x="${pad.l - 8}" y="${yy}" text-anchor="end" dominant-baseline="middle">${Math.round(v)}</text>`;
        }).join("")}</g>
        <g class="axis">${data.map((d, i) => ((i % every === 0 && data.length - 1 - i >= every / 2 + 0.5) || i === data.length - 1)
          ? `<text x="${x(i)}" y="${H - 6}" text-anchor="middle">${esc(d.label)}</text>` : "").join("")}</g>
        <path class="area" d="M${pts[0]} L${pts.join(" L")} L${x(data.length - 1)},${H - pad.b} L${x(0)},${H - pad.b} Z"/>
        <polyline class="line" points="${pts.join(" ")}"/>
        <line class="cross" x1="0" x2="0" y1="${pad.t}" y2="${H - pad.b}" style="display:none"/>
        <circle class="dot hover-dot" r="5" style="display:none"/>
        <circle class="dot" r="5" cx="${x(data.length - 1)}" cy="${y(vals[vals.length - 1])}"/>
        <rect x="${pad.l}" y="0" width="${W - pad.l - pad.r}" height="${H}" fill="transparent" class="hit"/>
      </svg>
      <div class="tooltip"></div>`;

    const svg = box.querySelector("svg"), tip = box.querySelector(".tooltip");
    const cross = svg.querySelector(".cross"), hd = svg.querySelector(".hover-dot");
    const hide = () => { tip.style.opacity = 0; cross.style.display = hd.style.display = "none"; };
    svg.querySelector(".hit").addEventListener("pointermove", (e) => {
      const r = svg.getBoundingClientRect();
      const mx = ((e.clientX - r.left) / r.width) * W;
      const i = Math.max(0, Math.min(data.length - 1, Math.round(((mx - pad.l) / (W - pad.l - pad.r)) * (data.length - 1))));
      const cx = x(i), cy = y(data[i].lp);
      cross.setAttribute("x1", cx); cross.setAttribute("x2", cx); cross.style.display = "";
      hd.setAttribute("cx", cx); hd.setAttribute("cy", cy); hd.style.display = "";
      const diff = i ? data[i].lp - data[i - 1].lp : 0;
      tip.innerHTML = `${esc(data[i].label)} · <strong>${data[i].lp} LP</strong>${i ? ` <span class="${diff >= 0 ? "good" : "bad"}">(${diff >= 0 ? "+" : ""}${diff})</span>` : ""}`;
      tip.style.left = (cx / W) * 100 + "%"; tip.style.top = (cy / H) * 100 + "%"; tip.style.opacity = 1;
    });
    svg.querySelector(".hit").addEventListener("pointerleave", hide);

    const delta = vals[vals.length - 1] - vals[0];
    const chip = $("#lp-delta");
    chip.textContent = `${delta >= 0 ? "▲ +" : "▼ "}${delta} LP`;
    chip.className = "chip " + (delta >= 0 ? "up" : "down");
  }
  drawChart();
  let rt; window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(drawChart, 120); });

  // ---------- Champions ----------
  $("#champ-grid").innerHTML = [...D.champions].sort((a, b) => b.games - a.games).map((c) => {
    const wr = pct(c.wins, c.games);
    return `
    <article class="card champ">
      ${champImg(c.name, c.display, "champ-icon")}
      <div>
        <div class="champ-name">${esc(c.display)}</div>
        <div class="champ-games">${c.games} Spiele · ${c.wins} S / ${c.games - c.wins} N</div>
      </div>
      <div class="wr-row">
        <div class="rank-meta"><span>Winrate</span><span class="${wr >= 50 ? "good" : "bad"}">${wr}%</span></div>
        <div class="bar"><span style="width:${wr}%;${wr < 50 ? "background:var(--loss)" : ""}"></span></div>
      </div>
      <div class="champ-stats">
        <div class="stat"><div class="stat-label">KDA</div><div class="stat-value">${kda(c.k, c.d, c.a)}</div></div>
        <div class="stat"><div class="stat-label">K/D/A</div><div class="stat-value">${c.k}/${c.d}/${c.a}</div></div>
        <div class="stat"><div class="stat-label">CS/Min</div><div class="stat-value">${c.cs}</div></div>
      </div>
    </article>`;
  }).join("");

  // ---------- Matches ----------
  $("#form-strip").innerHTML = `<span class="label">Form</span>` + m.map((x) =>
    `<span class="pip ${x.result}" title="${esc(x.display)} · ${x.result === "win" ? "Sieg" : "Niederlage"}">${x.result === "win" ? "S" : "N"}</span>`).join("");

  function renderMatches(filter) {
    const list = m.filter((x) => filter === "all" || x.result === filter);
    $("#match-list").innerHTML = list.length ? list.map((x) => `
      <li class="match ${x.result}">
        <div class="m-res-col">
          <div class="m-result">${x.result === "win" ? "Sieg" : "Niederlage"}</div>
          <div class="m-sub">${esc(x.queue)} · ${esc(x.ago)}</div>
        </div>
        ${champImg(x.champ, x.display, "match-icon")}
        <div>
          <div class="m-kda">${x.k} / <span class="d">${x.d}</span> / ${x.a}</div>
          <div class="m-sub">${esc(x.display)} · ${kda(x.k, x.d, x.a)} KDA</div>
        </div>
        <div class="m-extra">
          <div class="m-sub">${x.cs} CS · ${esc(x.duration)}</div>
        </div>
        <div class="m-lp ${x.lp >= 0 ? "good" : "bad"}">${x.lp >= 0 ? "+" : ""}${x.lp} LP</div>
      </li>`).join("") : `<li class="empty">Keine Matches in diesem Filter.</li>`;
  }
  renderMatches("all");
  document.querySelectorAll(".filter").forEach((btn) => btn.addEventListener("click", () => {
    document.querySelectorAll(".filter").forEach((b) => { b.classList.remove("is-active"); b.setAttribute("aria-selected", "false"); });
    btn.classList.add("is-active"); btn.setAttribute("aria-selected", "true");
    renderMatches(btn.dataset.filter);
  }));

  // ---------- Stream-Plan ----------
  const today = ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"][new Date().getDay()];
  $("#schedule").innerHTML = D.schedule.map((s) => `
    <div class="card slot ${s.day === today ? "today" : ""}">
      <div class="slot-day">${esc(s.day)}</div>
      <div>
        <div class="slot-time">${esc(s.time)} Uhr${s.day === today ? ' <span class="chip up">Heute</span>' : ""}</div>
        <div class="slot-title">${esc(s.title)}</div>
      </div>
    </div>`).join("");

  // ---------- Aktiver Nav-Link beim Scrollen ----------
  const links = [...document.querySelectorAll(".nav a")];
  const obs = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (e.isIntersecting) links.forEach((l) => l.classList.toggle("is-current", l.getAttribute("href") === "#" + e.target.id));
  }), { rootMargin: "-40% 0px -55% 0px" });
  ["overview", "champions", "matches", "stream"].forEach((id) => obs.observe(document.getElementById(id)));
})();
