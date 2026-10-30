// Rendert Standbilder und Animationen des Konzeptmodells (three.js im Headless-Chromium).
// Aufruf: node render.mjs [stills|tip|turn|explode|scenario|all]
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {execSync} from 'node:child_process';
import {createRequire} from 'node:module';
const {chromium} = createRequire(import.meta.url)('playwright');

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const OUT = path.join(ROOT, 'out');
const IMG = path.join(ROOT, 'docs', 'img');
const mode = process.argv[2] || 'all';
const ONLY = process.argv[4] ? process.argv[4].split(',') : null;
const PORT = +(process.argv[3] || 8765);
const [W, H] = mode === 'stills' ? [1600, 900] : [1280, 720];
const FPS = mode === 'scenario' ? 20 : 25;
fs.mkdirSync(IMG, {recursive: true});

const types = {'.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.stl': 'application/octet-stream'};
const server = http.createServer((req, res) => {
  const f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, {'Content-Type': types[path.extname(f)] || 'application/octet-stream'});
  fs.createReadStream(f).pipe(res);
}).listen(PORT);

const check = JSON.parse(fs.readFileSync(path.join(OUT, 'check_report.json')));
const stab = check.stability;
function interpStab(th) {
  let a = stab[0], b = stab[stab.length - 1];
  for (let i = 0; i < stab.length - 1; i++) if (stab[i].theta <= th && stab[i + 1].theta >= th) { a = stab[i]; b = stab[i + 1]; break; }
  const t = b.theta > a.theta ? (th - a.theta) / (b.theta - a.theta) : 0;
  const L = (k) => a[k] + (b[k] - a[k]) * t;
  return {F: L('zylinderkraft_beladen_N'), Lc: L('zylinderlaenge_mm'),
          kipp: Math.min(...Object.values(a.kippgrenze_beladen_deg))};
}
const sweepClr = (th) => {
  let best = check.sweep[0];
  for (const s of check.sweep) if (Math.abs(s.theta - th) < Math.abs(best.theta - th)) best = s;
  return best;
};
const ease = (t) => t < 0 ? 0 : t > 1 ? 1 : t * t * (3 - 2 * t);
const lerp = (a, b, t) => a + (b - a) * t;

const browser = await chromium.launch({args: ['--use-gl=angle', '--use-angle=swiftshader', '--ignore-gpu-blocklist']});
const page = await browser.newPage({viewport: {width: W, height: H}});
page.on('console', (m) => { if (m.type() === 'error') console.log('PAGE', m.text()); });
page.on('pageerror', (e) => console.log('PAGEERR', e.message));
await page.goto(`http://localhost:${PORT}/render/scene.html`);
await page.waitForFunction(() => window.ready === true);
console.log('Teile geladen:', await page.evaluate(() => window.init()));

async function shot(file, state, cam, hud = {}) {
  await page.evaluate(([s, c, h]) => { setPose(s); setCam(c); setHud(h); render(); }, [state, cam, hud]);
  await page.screenshot({path: file});
}

const CAM = {
  front34: {pos: [2900, 2300, 1700], target: [0, 0, 420], fov: 32},
  rear34: {pos: [-2900, -2200, 1800], target: [-50, 0, 420], fov: 32},
  side: {pos: [0, -9000, 520], target: [0, 0, 520], ortho: 820},
  front: {pos: [9000, 0, 520], target: [0, 0, 520], ortho: 620},
  top: {pos: [1, 0, 9000], target: [0, 0, 0], ortho: 820},
};

async function stills() {
  const base = {theta: 0, payload: {show: true, scale: 1}};
  const S = [
    ['01_ansicht_vorn_34.png', base, CAM.front34, {title: 'Mist-Shuttle V1 – Konzept', sub: 'Autonomer Elektro-Kipper für den Pferdestall · Technikseite vorn',
      labels: [{text: '3D-Lidar', at: [735, 175, 990]}, {text: 'Akku 48 V', at: [650, 180, 720]}, {text: 'Steuerung + Hydraulik', at: [650, -180, 800]},
               {text: 'Teleskopzylinder', at: [575, 0, 760]}, {text: 'Mulde 0,32 m³', at: [-100, 0, 900]}, {text: 'Schaltleiste', at: [800, 200, 260]}]}],
    ['02_ansicht_hinten_34.png', base, CAM.rear34, {title: 'Ansicht hinten', sub: 'Pendelklappe (Heckklappe) · Kipplager · Heckkamera',
      labels: [{text: 'Pendelklappe', at: [-715, 0, 650]}, {text: 'Kipplager Ø25', at: [-690, -290, 330]}, {text: 'Heckkamera', at: [-770, 0, 230]}]}],
    ['03_seitenansicht.png', base, CAM.side, {title: 'Seitenansicht (orthografisch)', sub: 'Länge 1575 mm · Radstand 800 mm · Ladekante 820 mm · Bodenfreiheit 145 mm'}],
    ['04_frontansicht.png', base, CAM.front, {title: 'Frontansicht (orthografisch)', sub: 'Breite 790 mm → passt durch Boxentür 1,0–1,2 m'}],
    ['05_draufsicht.png', base, CAM.top, {title: 'Draufsicht (orthografisch)', sub: 'Skid-Steer: dreht auf der Stelle, Wendekreis Ø ≈ 1,75 m'}],
    ['06_gekippt_55grad.png', {theta: 55, payload: {show: false}}, {pos: [-2200, -3300, 1500], target: [-250, 0, 600], fov: 34},
      {title: 'Kippstellung 55°', sub: 'Zylinder voll ausgefahren · Pendelklappe hängt frei · Schwerpunkt bleibt zwischen den Achsen',
       labels: [{text: 'Pendelklappe öffnet durch Schwerkraft', at: [-1150, 0, 300]}, {text: '4-stufiger Teleskopzylinder', at: [100, 0, 1200]}]}],
    ['07_explosion.png', {theta: 0, explode: 1, payload: {show: false}}, {pos: [3600, 3000, 2300], target: [0, 0, 500], fov: 36, shadowHalf: 5},
      {title: 'Explosionsdarstellung', sub: 'Rahmen · Mulde · Pendelklappe · 4 Radantriebe · Teleskopzylinder · Technikboxen · Sensorik'}],
    ['08_schnitt_mitte.png', {theta: 0, clipY: 0, payload: {show: false}}, {pos: [400, -3600, 900], target: [0, 0, 420], fov: 34},
      {title: 'Schnitt in Fahrzeugmitte', sub: 'Lage von Kipplager, Unterrahmen, Querträgern, Radantrieben und Teleskopzylinder'}],
    ['09_detail_kipplager.png', {theta: 20, payload: {show: false}}, {pos: [-1500, -1000, 700], target: [-690, -250, 300], fov: 30},
      {title: 'Detail Kipplager', sub: 'Bolzen Ø25 in Lagerbock am Längsträger · Kipplasche an Unterrahmen · Pendelklappe'}],
    ['10_detail_antrieb.png', {theta: 0, payload: {show: false}, ghost: ['Reifen VR', 'Felge VR'],
      hide: ['Mulde', 'Ladung', 'Heckklappe', 'Klappen', 'Steuerungs', 'Akku', 'Rundum', 'Not-Halt', 'RTK', 'Frontkamera', 'Sensormast', '3D-Lidar', 'Teleskop', 'Zylinder-Kopf', 'Gummi']},
      {pos: [1300, -1700, 1100], target: [250, -150, 200], fov: 32},
      {title: 'Detail Radantrieb (Mulde und Technik ausgeblendet, Rad vorn rechts transparent)', sub: 'Je Rad: BLDC-Motor 750 W → Schneckengetriebe i≈40 → Welle Ø30 in Flanschlager → Felge'}],
    ['11_detail_zylinder.png', {theta: 30, payload: {show: false}}, {pos: [1900, -1500, 1300], target: [350, 0, 800], fov: 32},
      {title: 'Detail Kippzylinder (30°)', sub: 'Fußgabel am Querträger · Kopfgabel an Stirnwand · 4 Stufen Ø91/76/61/46'}],
  ];
  for (const [f, s, c, h] of S) { if (ONLY && !ONLY.some(o => f.startsWith(o))) continue; await shot(path.join(IMG, f), s, c, h); console.log('Bild', f); }
  // Größenvergleich mit Person (1,80 m)
  await page.evaluate(() => showPerson([-1350, 0]));
  await shot(path.join(IMG, '12_groessenvergleich.png'), {theta: 0, payload: {show: true, scale: 1}}, {pos: [0, -9000, 950], target: [-300, 0, 950], ortho: 1050},
    {title: 'Größenvergleich', sub: 'Person 1,80 m · Ladekante 820 mm (Mistgabel-Höhe) · Fahrzeughöhe bis Lidar 965 mm'});
  await page.evaluate(() => showPerson(null));
}

async function frames(name, n, fn) {
  const dir = path.join(OUT, 'frames', name);
  fs.rmSync(dir, {recursive: true, force: true}); fs.mkdirSync(dir, {recursive: true});
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    const {state, cam, hud, _heap} = await fn(i / FPS, i);
    await page.evaluate(([s, c, h, hp]) => { if (hp) setHeap([hp[0], hp[1]], hp[2]); setPose(s); setCam(c); setHud(h || {}); render(); }, [state, cam, hud, _heap]);
    await page.screenshot({path: path.join(dir, String(i).padStart(4, '0') + '.png')});
    if (i % 50 === 0) console.log(name, i, '/', n, ((Date.now() - t0) / 1000).toFixed(0) + 's');
  }
  const mp4 = path.join(IMG, name + '.mp4'), gif = path.join(IMG, name + '.gif');
  execSync(`ffmpeg -y -loglevel error -framerate ${FPS} -i ${dir}/%04d.png -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart ${mp4}`);
  execSync(`ffmpeg -y -loglevel error -framerate ${FPS} -i ${dir}/%04d.png -vf "fps=12,scale=720:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" ${gif}`);
  console.log('Video', mp4);
}

async function animTip() {
  const T = 11.0, stop = 55;
  await frames('anim_kippen', Math.round(T * FPS), (t) => {
    let th;
    if (t < 1) th = 0; else if (t < 4.5) th = stop * ease((t - 1) / 3.5); else if (t < 6.5) th = stop; else if (t < 10) th = stop * (1 - ease((t - 6.5) / 3.5)); else th = 0;
    // Ladung rutscht ab ca. 38° heraus
    const sl = t < 4.5 ? Math.max(0, (th - 38) / 17) * 0.35 : Math.min(1, 0.35 + (t - 4.5) / 1.6);
    const payload = {show: sl < 1, slide: sl * 1100, scale: 1 - sl * 0.9};
    const s = interpStab(th), c = sweepClr(th);
    const box = `Kippwinkel        ${th.toFixed(1)}°\nZylinderlänge    ${s.Lc.toFixed(0)} mm\nZylinderkraft    ${(s.F / 1000).toFixed(2)} kN (beladen)\nmin. Kippgrenze  ${s.kipp.toFixed(1)}° Hang\nAbstand Zyl.–Mulde ${c.clearance['Zylinder-Mulde']} mm\nKollisionen      ${c.collisions.length}`;
    const az = -125 + t * 4;
    const r = 3900;
    return {state: {theta: th, payload}, cam: {pos: [r * Math.cos(az * Math.PI / 180), r * Math.sin(az * Math.PI / 180), 1500], target: [-150, 0, 600], fov: 34},
      hud: {title: 'Kippvorgang 0° → 55° → 0°', sub: 'Einfachwirkender Teleskopzylinder · Absenken durch Eigengewicht · Werte aus der Kinematikprüfung', box}};
  });
}

async function animTurn() {
  const T = 9.0;
  await frames('anim_rundum', Math.round(T * FPS), (t) => {
    const az = 30 + 360 * t / T;
    const r = 3800;
    return {state: {theta: 0, payload: {show: true, scale: 1}}, cam: {pos: [r * Math.cos(az * Math.PI / 180), r * Math.sin(az * Math.PI / 180), 1700], target: [0, 0, 450], fov: 32},
      hud: {title: 'Mist-Shuttle V1 – Rundumansicht', sub: '790 × 1575 mm · Nutzlast ≈ 240 kg (0,32 m³) · 4 × 750 W Radantrieb · 48 V LiFePO4'}};
  });
}

async function animExplode() {
  const T = 8.0;
  await frames('anim_explosion', Math.round(T * FPS), (t) => {
    let e;
    if (t < 0.8) e = 0; else if (t < 3.3) e = ease((t - 0.8) / 2.5); else if (t < 5.3) e = 1; else if (t < 7.5) e = 1 - ease((t - 5.3) / 2.2); else e = 0;
    const az = 25 + t * 9, r = 4800;
    return {state: {theta: 0, explode: e, payload: {show: false}}, cam: {pos: [r * Math.cos(az * Math.PI / 180), r * Math.sin(az * Math.PI / 180), 2500], target: [0, 0, 520], fov: 34, shadowHalf: 5},
      hud: {title: 'Explosionsdarstellung', sub: 'Alle Teile über Bolzen, Lager oder Verschraubung mit dem Rahmen verbunden – keine freischwebenden Teile'}};
  });
}

// --- Einsatzszenario -----------------------------------------------------------
function buildPath() {
  // Segmente: {type:'wait'|'line'|'turn'|'tip', dur, ...}; Fahrzeugzustand x,y,yaw (Grad), wheelL/R (Grad)
  const R = 200, B = 700;
  const segs = [];
  let st = {x: 5900, y: 600, yaw: 90, wl: 0, wr: 0, th: 0, load: 0, slide: 0, heap: 0};
  const add = (dur, f, phase) => segs.push({dur, f, phase});
  const line = (dx, dy, v, phase) => { // fährt in Fahrzeugrichtung (v>0 vorwärts, v<0 rückwärts) zu Zielpunkt
    const d = Math.hypot(dx, dy), dur = d / Math.abs(v) / 1000;
    add(dur, (s0, u) => { const k = ease(u); const dist = d * k * Math.sign(v); return {...s0, x: s0.x + dx * k, y: s0.y + dy * k, wl: s0.wl + dist / R * 57.3, wr: s0.wr + dist / R * 57.3}; }, phase);
  };
  const turn = (dyaw, phase) => {
    const dur = Math.abs(dyaw) / 60;
    add(dur, (s0, u) => { const k = ease(u); const arc = (dyaw * k / 57.3) * B / 2; return {...s0, yaw: s0.yaw + dyaw * k, wl: s0.wl - arc / R * 57.3, wr: s0.wr + arc / R * 57.3}; }, phase);
  };
  add(2.6, (s0, u) => ({...s0, load: ease(u)}), 'Beladen von Hand vor der Box (Mistgabel)');
  add(0.6, (s0) => s0, 'Freigabe per Taster → Fahrt startet');
  line(0, -600, -0.8, 'Rückwärts aus der Boxentür');
  turn(-90, 'Wenden auf der Stelle');
  line(9600, 0, 1.6, 'Fahrt durch die Stallgasse (Video 2× beschleunigt)');
  line(5600, 0, 2.0, 'Fahrt über den Hof zur Mistplatte');
  turn(90, 'Ausrichten zur Mistplatte');
  line(0, -6200, -1.6, 'Rückwärts an den Misthaufen');
  add(3.4, (s0, u) => ({...s0, th: 55 * ease(u), slide: Math.max(0, (ease(u) - 0.65) / 0.35) * 0.4}), 'Abkippen (55°)');
  add(1.6, (s0, u) => ({...s0, th: 55, slide: 0.4 + 0.6 * u, heap: u, hx: s0.x - Math.cos(s0.yaw / 57.3) * 1250, hy: s0.y - Math.sin(s0.yaw / 57.3) * 1250}), 'Mist rutscht heraus, Pendelklappe öffnet');
  add(3.0, (s0, u) => ({...s0, th: 55 * (1 - ease(u)), load: 0, slide: 0}), 'Mulde senkt sich durch Eigengewicht');
  line(0, 6200, 1.6, 'Zurück zum Stall');
  turn(90, 'Wenden');
  line(-15200, 0, 2.0, 'Rückfahrt durch die Stallgasse');
  turn(-90, 'Bereit zum nächsten Beladen');
  line(0, 600, 0.6, 'Bereit zum nächsten Beladen');
  add(1.2, (s0) => s0, 'Bereit zum nächsten Beladen');
  // Zustand am Segmentanfang vorberechnen
  let s = st;
  for (const g of segs) { g.s0 = s; s = g.f(s, 1); }
  return segs;
}

async function animScenario() {
  const segs = buildPath();
  const T = segs.reduce((a, g) => a + g.dur, 0);
  let camPos = null, camTgt = null;
  await page.evaluate(() => { buildYard(); showPerson([5000, 2600]); });
  await frames('anim_einsatz', Math.round(T * FPS), (t) => {
    let acc = 0, g = segs[segs.length - 1], u = 1;
    for (const sg of segs) { if (t < acc + sg.dur) { g = sg; u = (t - acc) / sg.dur; break; } acc += sg.dur; }
    const s = g.f(g.s0, u);
    const yawR = s.yaw * Math.PI / 180;
    // Ladung
    let payload;
    if (s.load < 1 && s.slide === 0 && s.th === 0 && t < 4) payload = {show: s.load > 0.02, scale: s.load, slide: 0};
    else if (s.slide > 0) payload = {show: s.slide < 1, slide: s.slide * 1100, scale: 1 - s.slide * 0.9};
    else payload = {show: s.load > 0.5, scale: 1, slide: 0};
    // Kamera: weich nachgeführt, schräg von oben
    const tgt = [s.x, s.y, 500];
    const want = [s.x - 4200, s.y - 7600, 9800];
    if (!camPos) { camPos = want; camTgt = tgt; }
    camPos = camPos.map((v, i) => v + (want[i] - v) * 0.06); camTgt = camTgt.map((v, i) => v + (tgt[i] - v) * 0.12);
    return {state: {theta: s.th, payload, veh: [s.x, s.y, s.yaw], wheelL: s.wl, wheelR: s.wr},
      cam: {pos: camPos, target: camTgt, fov: 38, shadowHalf: 11},
      hud: {title: 'Einsatzszenario (Schema, Video teils beschleunigt)', sub: g.phase, box: `Zeit ${t.toFixed(1)} s\nKippwinkel ${s.th.toFixed(0)}°`},
      _heap: [s.hx || 0, s.hy || 0, s.heap]};
  });
}

if (mode === 'stills' || mode === 'all') await stills();
if (mode === 'turn' || mode === 'all') await animTurn();
if (mode === 'tip' || mode === 'all') await animTip();
if (mode === 'explode' || mode === 'all') await animExplode();
if (mode === 'scenario' || mode === 'all') await animScenario();
await browser.close(); server.close();
