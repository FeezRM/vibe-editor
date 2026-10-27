#!/usr/bin/env node
/**
 * brand.mjs — the customisation layer.
 *
 *   node scripts/brand.mjs scaffold create an empty brand/ to fill in (never overwrites)
 *   node scripts/brand.mjs init     interactive wizard -> brand/brand.json
 *   node scripts/brand.mjs build    brand.json -> brand/tokens.css
 *   node scripts/brand.mjs show     print the resolved config
 *   node scripts/brand.mjs check    validate without writing
 *
 * `build` does NOT duplicate the design system. It loads the skin stylesheet from
 * scripts/tokens/tokens-<skin>.css and substitutes values inside its
 * :root block, so every class definition stays in exactly one place. Add a rule to the
 * skin file and it flows through automatically.
 *
 * No dependencies. Node 22+.
 */

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { createInterface } from "node:readline/promises";
import { stdin, stdout } from "node:process";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const BRAND_DIR = join(ROOT, "brand");
const CONFIG = join(BRAND_DIR, "brand.json");
const OUT = join(BRAND_DIR, "tokens.css");
const SKIN = (s) =>
  join(ROOT, "scripts", "tokens", `tokens-${s}.css`);

/* viral is the default: it is the one derived by measurement from reels that
   actually performed (measured from reels that performed). analog and digital
   are kept for projects already built against them. */
const SKINS = ["viral", "analog", "digital"];

/* ------------------------------------------------------------------ output -- */
const c = {
  dim: (s) => `\x1b[2m${s}\x1b[0m`,
  bold: (s) => `\x1b[1m${s}\x1b[0m`,
  green: (s) => `\x1b[32m${s}\x1b[0m`,
  yellow: (s) => `\x1b[33m${s}\x1b[0m`,
  red: (s) => `\x1b[31m${s}\x1b[0m`,
  cyan: (s) => `\x1b[36m${s}\x1b[0m`,
};
const ok = (m) => console.log(`  ${c.green("[ok]")} ${m}`);
const warn = (m) => console.log(`  ${c.yellow("[!]")}  ${m}`);
const note = (m) => console.log(`       ${c.dim(m)}`);
const step = (m) => console.log(`\n${c.cyan("==>")} ${c.bold(m)}`);

/* ------------------------------------------------------------------ colour -- */
const HEX = /^#[0-9a-fA-F]{6}$/;

function hexToRgb(hex) {
  const h = hex.replace("#", "");
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ];
}
const rgba = (hex, a) => {
  const [r, g, b] = hexToRgb(hex);
  return `rgba(${r}, ${g}, ${b}, ${a})`;
};

/** Relative luminance + contrast ratio, so we can warn on unreadable palettes. */
function luminance(hex) {
  const [r, g, b] = hexToRgb(hex).map((v) => {
    const s = v / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function contrast(a, b) {
  const [x, y] = [luminance(a), luminance(b)].sort((p, q) => q - p);
  return (x + 0.05) / (y + 0.05);
}

/** Shift a hex toward white/black by ratio (-1..1). Used to derive accent hi/lo. */
function shift(hex, amount) {
  const [r, g, b] = hexToRgb(hex);
  const t = amount > 0 ? 255 : 0;
  const k = Math.abs(amount);
  const mix = (v) => Math.round(v + (t - v) * k);
  return (
    "#" +
    [mix(r), mix(g), mix(b)]
      .map((v) => v.toString(16).padStart(2, "0"))
      .join("")
  );
}

/* ------------------------------------------------------------------ starter - */
/* Everything `scaffold` writes lives here, so the command works even when brand/
   does not exist at all (fresh clone with the folder deleted, or a fork that
   gitignores it). Values are house defaults; the free text is deliberately blank
   so nobody ships someone else's brand by accident. */

const STARTER_CONFIG = {
  name: "My Channel",
  // NOT cosmetic. Every rebuilt app mockup — profile, comment sheet, follow
  // card, reel cover — carries this handle. Left blank the skills have nothing
  // to put in a mockup, and the one thing they must never do is borrow a handle
  // out of samples/, which belongs to a real person.
  creator: { handle: "" },
  skin: "viral",
  palette: {
    ground: "#0A0A0B",
    ink: "#FFFFFF",
    accent: "#FFC531",
    signalDown: "#EB0408",
    signalUp: "#00E800",
  },
  fonts: {
    display: ["Anton", "Archivo Black", "sans-serif"],
    caption: ["Anton", "sans-serif"],
    engrave: ["Inter", "sans-serif"],
    mono: ["JetBrains Mono", "monospace"],
  },
  type: {
    trackDisplay: "-0.010em",
    trackCaps: "0.020em",
    trackEngrave: "0.060em",
    trackCaption: "-0.015em",
    captionUppercase: true,
    displayUppercase: true,
  },
  canvas: {
    width: 1080,
    height: 1920,
    fps: 30,
    marginX: 72,
    safeTop: 240,
    safeBottom: 420,
    captionTop: 920,
    captionBottom: 1130,
  },
  texture: { grainOpacity: 0.06, vignetteDrop: 0.35, contourOpacity: 0, stutterFps: 0 },
  density: {
    maxGraphicsPer30s: 12,
    graphicGapSeconds: [2, 4],
    interruptIntervalSeconds: [1, 2],
    maxStaticShotSeconds: 3,
    maxAccentElementsPerFrame: 3,
  },
  voice: {
    preserveSpeakerGrammar: true,
    captionCase: "upper",
    maxWordsPerCaptionGroup: 4,
    maxEmphasisWordsPerLine: 2,
  },
  export: {
    resolution: "1080x1920",
    codec: "H.264",
    bitrateMbps: 20,
    audioKbps: 320,
    outputDir: "exports/",
  },
  tracks: {
    video: ["A-roll", "B-roll / cutaways", "primary graphics", "secondary graphics"],
    audio: ["voice", "voice alt", "SFX", "SFX", "music", "spare"],
  },
};

const STARTER_BRAND_MD = `# BRAND — your custom instructions

Free-text house rules for **your** channel. Every \`ig-*\` skill reads this file before it
plans or builds anything, and **what you write here beats the repo defaults.**

\`brand.json\` next door holds the machine-readable values (colours, fonts, numbers) that
generate \`tokens.css\`. This file holds everything that isn't a number: voice, subject
matter, what you refuse to put on screen, how you sign off.

Every section below is empty on purpose — fill in the ones you care about and delete the
rest. An empty section means "use the repo default." There is no schema here: write like
you'd brief a human editor.

---

## Who this is for

<!-- One or two lines. Who's on camera, what the channel is about, who watches it. -->

---

## Voice

<!-- How the words should sound on screen. The single most-violated rule is transcribers
     "correcting" a speaker into someone else. Say plainly what must be preserved.
     e.g. "Captions are my exact words — keep the slang and the contractions." -->

---

## Subject matter

<!-- What the content is actually about. This drives which graphics get chosen: the SHOW
     step reaches for different devices for a money claim vs. a code demo. -->

---

## Banned on screen

<!-- Hard "never do this" list, checked before render. Be specific — a vague ban is
     unenforceable. e.g. "no emoji", "no luxury b-roll", "no bounce or elastic easing". -->

---

## Required on screen

<!-- Anything that must appear. Most channels want nothing here — zero chrome is the
     default and usually the right call. Leave empty unless you truly need it. -->

---

## The CTA

<!-- How videos end. One CTA, always. -->

---

## Sound

<!-- Music taste and SFX palette. Name real files if you have a library. -->

---

## Anything else

<!-- Free space. Recurring notes, pet peeves, things you keep having to correct.
     If you find yourself repeating a note to the agent, write it here instead. -->
`;

/**
 * Create brand/ with a blank config to customise. Never overwrites: an existing
 * brand.json or BRAND.md is left exactly as it is, so setup can run this on every
 * invocation.
 */
async function scaffold({ quiet = false } = {}) {
  if (!quiet) step("Preparing brand/");
  await mkdir(BRAND_DIR, { recursive: true });

  const created = [];
  const kept = [];

  if (existsSync(CONFIG)) {
    kept.push("brand/brand.json");
  } else {
    // $schema only helps if the schema file is actually next door.
    const config = existsSync(join(BRAND_DIR, "brand.schema.json"))
      ? { $schema: "./brand.schema.json", ...STARTER_CONFIG }
      : { ...STARTER_CONFIG };
    await writeFile(CONFIG, JSON.stringify(config, null, 2) + "\n", "utf8");
    created.push("brand/brand.json");
  }

  const brandMd = join(BRAND_DIR, "BRAND.md");
  if (existsSync(brandMd)) {
    kept.push("brand/BRAND.md");
  } else {
    await writeFile(brandMd, STARTER_BRAND_MD, "utf8");
    created.push("brand/BRAND.md");
  }

  if (!quiet) {
    created.forEach((f) => ok(`${f} created`));
    kept.forEach((f) => note(`${f} already exists — left untouched`));
    if (created.length) {
      note("Fill it in:  node scripts/brand.mjs init   (colours, fonts, fps)");
      note("Then write brand/BRAND.md — voice, banned visuals, CTA.");
    }
  }
  return { created, kept };
}

/* ------------------------------------------------------------------- config - */
async function load() {
  if (!existsSync(CONFIG)) {
    throw new Error(
      `No brand config at brand/brand.json.\n` +
        `       Run: node scripts/brand.mjs scaffold   (blank files to edit)\n` +
        `       or:  node scripts/brand.mjs init       (interactive wizard)`
    );
  }
  let raw;
  try {
    raw = JSON.parse(await readFile(CONFIG, "utf8"));
  } catch (e) {
    throw new Error(`brand/brand.json is not valid JSON — ${e.message}`);
  }
  return raw;
}

function validate(b) {
  const errors = [];
  const warnings = [];

  if (!SKINS.includes(b.skin))
    errors.push(`skin must be one of ${SKINS.join(", ")} (got ${JSON.stringify(b.skin)})`);

  const p = b.palette ?? {};
  for (const key of ["ground", "ink", "accent"]) {
    if (!p[key]) errors.push(`palette.${key} is required`);
    else if (!HEX.test(p[key]))
      errors.push(`palette.${key} must be a 6-digit hex like #C9A24B (got "${p[key]}")`);
  }
  for (const key of ["groundLift", "ink2", "accentHi", "accentLo", "signalDown", "signalUp"]) {
    if (p[key] && !HEX.test(p[key])) errors.push(`palette.${key} must be a 6-digit hex`);
  }

  if (errors.length) return { errors, warnings };

  // House rules, enforced as warnings so a fork can knowingly break them.
  // The off-white/off-black rule belongs to the instrument skins. The viral
  // skin impersonates real app UI, which uses pure white on near-black, so
  // warning about it there would be wrong.
  if (b.skin !== "viral") {
    if (p.ground.toLowerCase() === "#000000")
      warnings.push("palette.ground is pure black — it reads flat and digital. Prefer a warm near-black.");
    if (p.ink.toLowerCase() === "#ffffff")
      warnings.push("palette.ink is pure white — prefer a warm off-white.");
  }

  const inkOnGround = contrast(p.ink, p.ground);
  if (inkOnGround < 7)
    warnings.push(
      `ink on ground contrast is ${inkOnGround.toFixed(1)}:1 — below 7:1, captions will struggle at scroll speed.`
    );
  const accentOnGround = contrast(p.accent, p.ground);
  if (accentOnGround < 3)
    warnings.push(
      `accent on ground contrast is ${accentOnGround.toFixed(1)}:1 — the accent will disappear over dark footage.`
    );

  if (luminance(p.ground) > luminance(p.ink))
    warnings.push("ground is lighter than ink — this system is built dark-on-light-text. Light themes are untested.");

  const f = b.fonts ?? {};
  for (const k of ["display", "caption", "engrave", "mono"]) {
    if (!Array.isArray(f[k]) || f[k].length === 0)
      errors.push(`fonts.${k} must be a non-empty array (first entry = preferred family)`);
    else if (f[k].length === 1)
      warnings.push(`fonts.${k} has no fallback — add a free family so renders degrade instead of breaking.`);
  }

  const handle = (b.creator?.handle ?? "").trim();
  if (!handle)
    warnings.push(
      "creator.handle is empty — every app mockup needs an account handle, and a blank one means the agent either invents one or borrows a real person's out of samples/."
    );
  else if (handle.startsWith("@"))
    warnings.push('creator.handle should not include the leading @ — mockups add it where the real UI shows one.');

  const cv = b.canvas ?? {};
  if (cv.captionTop != null && cv.captionBottom != null && cv.height) {
    const lo = cv.captionTop / cv.height;
    const hi = cv.captionBottom / cv.height;
    if (lo > 0.62)
      warnings.push(
        `caption band starts at ${(lo * 100).toFixed(0)}% of frame — bottom-third captions force viewers to choose between the face and the words.`
      );
    if (hi > 0.82) warnings.push("caption band runs into the platform UI strip.");
  }

  return { errors, warnings };
}

/**
 * Fill in anything the user left out, deriving what can be derived.
 * Only derives from a VALID source hex — otherwise a single typo in `accent`
 * cascades into three bogus "accentHi must be hex" errors that bury the real one.
 */
function resolveDefaults(b) {
  const p = { ...(b.palette ?? {}) };
  const from = (src, amount) => (HEX.test(src ?? "") ? shift(src, amount) : undefined);
  p.groundLift ??= from(p.ground, 0.06);
  p.ink2 ??= from(p.ink, -0.18);
  p.accentHi ??= from(p.accent, 0.38);
  p.accentLo ??= from(p.accent, -0.34);
  p.signalDown ??= "#5C1A1A";
  p.signalUp ??= "#1F3D2B";
  for (const k of Object.keys(p)) if (p[k] === undefined) delete p[k];
  return { ...b, palette: p };
}

/* -------------------------------------------------------------------- build - */
/** Replace `--name: value;` inside the FIRST :root block only. */
function setVars(css, vars) {
  const start = css.indexOf(":root");
  if (start === -1) throw new Error("skin stylesheet has no :root block");
  const open = css.indexOf("{", start);
  let depth = 0, end = -1;
  for (let i = open; i < css.length; i++) {
    if (css[i] === "{") depth++;
    else if (css[i] === "}") { depth--; if (depth === 0) { end = i; break; } }
  }
  if (end === -1) throw new Error("unterminated :root block in skin stylesheet");

  let block = css.slice(open, end);
  const missed = [];
  for (const [name, value] of Object.entries(vars)) {
    const re = new RegExp(`(--${name}\\s*:)([^;]*)(;)`);
    if (re.test(block)) block = block.replace(re, `$1 ${value}$3`);
    else missed.push(name);
  }
  return { css: css.slice(0, open) + block + css.slice(end), missed };
}

function varsFrom(b) {
  const p = b.palette, f = b.fonts, t = b.type ?? {}, cv = b.canvas ?? {},
        tx = b.texture ?? {};
  const stack = (arr) =>
    arr.map((n) => (/^[a-z-]+$/.test(n) ? n : `'${n}'`)).join(", ");

  const v = {
    ground: p.ground,
    "ground-lift": p.groundLift,
    ink: p.ink,
    "ink-2": p.ink2,
    accent: p.accent,
    "accent-hi": p.accentHi,
    "accent-lo": p.accentLo,
    "ink-dim": rgba(p.ink, 0.55),
    "ink-ghost": rgba(p.ink, 0.18),
    "ink-trace": rgba(p.ink, 0.08),
    plate: rgba(p.ground, 0.88),
    stroke: rgba(p.ink, 0.14),
    "sig-down": p.signalDown,
    "sig-up": p.signalUp,
    "font-display": stack(f.display),
    "font-caption": stack(f.caption),
    "font-engrave": stack(f.engrave),
    "font-mono": stack(f.mono),
  };

  if (t.trackDisplay) v["track-display"] = t.trackDisplay;
  if (t.trackCaps) v["track-caps"] = t.trackCaps;
  if (t.trackEngrave) v["track-engrave"] = t.trackEngrave;
  if (t.trackCaption) v["track-caption"] = t.trackCaption;

  if (cv.width) v.w = `${cv.width}px`;
  if (cv.height) v.h = `${cv.height}px`;
  if (cv.marginX != null) v["margin-x"] = `${cv.marginX}px`;
  if (cv.safeTop != null) v["safe-top"] = `${cv.safeTop}px`;
  if (cv.safeBottom != null) v["safe-bottom"] = `${cv.safeBottom}px`;
  if (cv.captionTop != null) v["caption-top"] = `${cv.captionTop}px`;
  if (cv.captionBottom != null) v["caption-bottom"] = `${cv.captionBottom}px`;

  if (tx.grainOpacity != null) v["grain-opacity"] = String(tx.grainOpacity);
  if (tx.vignetteDrop != null) v["vignette-drop"] = String(tx.vignetteDrop);
  if (tx.contourOpacity != null) v["contour-opacity"] = String(tx.contourOpacity);
  if (tx.stutterFps != null) v["stutter-fps"] = String(tx.stutterFps);

  return v;
}

async function build({ quiet = false } = {}) {
  const b = resolveDefaults(await load());
  const { errors, warnings } = validate(b);
  if (errors.length) {
    console.log(c.red("\nbrand.json has errors:\n"));
    errors.forEach((e) => console.log(`  ${c.red("x")} ${e}`));
    console.log();
    process.exit(1);
  }

  const skinPath = SKIN(b.skin);
  if (!existsSync(skinPath))
    throw new Error(`skin stylesheet not found: ${skinPath}`);

  const skinCss = await readFile(skinPath, "utf8");
  const { css, missed } = setVars(skinCss, varsFrom(b));

  const header = `/* ============================================================
   GENERATED — do not edit.

   Source : brand/brand.json  (edit that, then re-run)
   Skin   : ${b.skin}
   Brand  : ${b.name ?? "unnamed"}
   Rebuild: node scripts/brand.mjs build

   Copy this into a project as tokens.css. Free-text house rules that
   are not values live in brand/BRAND.md and are read by the skills.
   ============================================================ */\n\n`;

  await mkdir(BRAND_DIR, { recursive: true });
  await writeFile(OUT, header + css, "utf8");

  if (!quiet) {
    step("Building brand tokens");
    ok(`brand/tokens.css written (${b.skin} skin, accent ${b.palette.accent})`);
    if (missed.length)
      warn(`not present in this skin, skipped: ${missed.join(", ")}`);
    warnings.forEach(warn);
    note("Copy into a project:  cp brand/tokens.css projects/<slug>/tokens.css");
  }
  return { b, warnings };
}

/* --------------------------------------------------------------------- init - */
async function init() {
  // The wizard needs a real terminal. Piped/redirected stdin closes readline
  // mid-question and throws "readline was closed", which reads like a crash.
  if (!stdin.isTTY) {
    console.log(`
  ${c.yellow("init needs an interactive terminal.")}

  Run it directly in a shell:
      node scripts/brand.mjs init

  Or skip the wizard entirely — edit ${c.cyan("brand/brand.json")} by hand, then:
      node scripts/brand.mjs build
`);
    process.exit(1);
  }

  const rl = createInterface({ input: stdin, output: stdout });
  const ask = async (q, def) => {
    const a = (await rl.question(`  ${q} ${c.dim(`[${def}]`)} `)).trim();
    return a === "" ? def : a;
  };
  const askHex = async (q, def) => {
    for (;;) {
      let a = await ask(q, def);
      if (!a.startsWith("#")) a = "#" + a;
      if (HEX.test(a)) return a;
      console.log(`     ${c.red("need a 6-digit hex like #C9A24B")}`);
    }
  };

  console.log(`
  ${c.bold("VIBE EDITOR — brand setup")}
  ${c.dim("Press Enter to accept each default. Everything is editable later")}
  ${c.dim("in brand/brand.json, and the free-text rules live in brand/BRAND.md.")}
`);

  const base = existsSync(CONFIG)
    ? resolveDefaults(JSON.parse(await readFile(CONFIG, "utf8")))
    : null;
  if (base) warn("brand/brand.json exists — these answers will overwrite it.\n");

  // No config yet: scaffold brand/ first so BRAND.md lands too, and answer from
  // the starter rather than reading a file that isn't there.
  if (!base) await scaffold({ quiet: true });
  const d = base ?? resolveDefaults(STARTER_CONFIG);

  const name = await ask("Brand / channel name:", d.name ?? "My Channel");
  const handle = (await ask(
    "Account handle, no @ (every app mockup carries it):",
    d.creator?.handle || ""
  )).replace(/^@/, "");

  let skin = "";
  while (!SKINS.includes(skin))
    skin = (await ask(
      "Skin — viral (app UI + real metrics, the default), analog (warm instrument), digital (terminal):",
      d.skin)).toLowerCase();

  console.log(`\n  ${c.dim("Palette — three roles carry the whole system.")}`);
  const ground = await askHex("Ground (near-black, never pure #000):", d.palette.ground);
  const ink = await askHex("Ink (off-white, never pure #FFF):", d.palette.ink);
  const accent = await askHex("Accent (the ONE colour that marks what matters):", d.palette.accent);

  console.log(`\n  ${c.dim("Fonts — first name wins; the rest are fallbacks.")}`);
  console.log(`  ${c.dim("Licensed faces must be installed on this machine. Never use @font-face.")}`);
  const display = await ask("Display / headline family:", d.fonts.display[0]);
  const caption = await ask("Caption family:", d.fonts.caption[0]);
  const engrave = await ask("Label / numeral family:", d.fonts.engrave[0]);
  const mono = await ask("Readout / mono family:", d.fonts.mono[0]);

  console.log(`\n  ${c.dim("Delivery.")}`);
  const fps = Number(await ask("Sequence fps (must match your Premiere sequence):", String(d.canvas.fps)));

  await rl.close();

  const keepTail = (arr, first) => {
    const tail = arr.slice(1);
    return tail.includes(first) ? [first, ...tail.filter((x) => x !== first)] : [first, ...tail];
  };

  const out = {
    ...d,
    name,
    creator: { ...(d.creator ?? {}), handle },
    skin,
    palette: { ...d.palette, ground, ink, accent, groundLift: undefined, ink2: undefined, accentHi: undefined, accentLo: undefined },
    fonts: {
      display: keepTail(d.fonts.display, display),
      caption: keepTail(d.fonts.caption, caption),
      engrave: keepTail(d.fonts.engrave, engrave),
      mono: keepTail(d.fonts.mono, mono),
    },
    canvas: { ...d.canvas, fps: Number.isFinite(fps) ? fps : d.canvas.fps },
  };
  // strip the undefined derived keys so build() re-derives them from the new accent
  for (const k of Object.keys(out.palette))
    if (out.palette[k] === undefined) delete out.palette[k];

  await writeFile(CONFIG, JSON.stringify(out, null, 2) + "\n", "utf8");

  step("Writing brand config");
  ok("brand/brand.json");
  const { warnings } = await build({ quiet: true });
  ok("brand/tokens.css");
  warnings.forEach(warn);

  if (!handle)
    warn("no handle set — add creator.handle to brand/brand.json before building any mockup.");

  console.log(`
  ${c.bold("Done.")} Two more things worth doing:

    1. Edit ${c.cyan("brand/BRAND.md")} — voice, banned visuals, CTA, subject matter.
       That file is free text and the skills read it before planning anything.

    2. Copy the tokens into a project when you scaffold one:
       ${c.dim("cp brand/tokens.css projects/<slug>/tokens.css")}

  Re-run ${c.cyan("node scripts/brand.mjs build")} after any edit to brand.json.
`);
}

/* --------------------------------------------------------------------- show - */
async function show() {
  const b = resolveDefaults(await load());
  const { errors, warnings } = validate(b);
  step(`Brand: ${b.name ?? "unnamed"} (${b.skin} skin)`);
  console.log(`
  handle   ${b.creator?.handle ? "@" + b.creator.handle : c.yellow("(not set — mockups have no account to show)")}

  ground   ${b.palette.ground}      ink      ${b.palette.ink}
  accent   ${b.palette.accent}      hi/lo    ${b.palette.accentHi} / ${b.palette.accentLo}

  display  ${b.fonts.display.join(", ")}
  caption  ${b.fonts.caption.join(", ")}
  engrave  ${b.fonts.engrave.join(", ")}
  mono     ${b.fonts.mono.join(", ")}

  canvas   ${b.canvas.width}x${b.canvas.height} @ ${b.canvas.fps}fps
  captions y ${b.canvas.captionTop}-${b.canvas.captionBottom}  (${((b.canvas.captionTop / b.canvas.height) * 100).toFixed(0)}-${((b.canvas.captionBottom / b.canvas.height) * 100).toFixed(0)}% of frame)
  contrast ink/ground ${contrast(b.palette.ink, b.palette.ground).toFixed(1)}:1   accent/ground ${contrast(b.palette.accent, b.palette.ground).toFixed(1)}:1
`);
  errors.forEach((e) => console.log(`  ${c.red("x")} ${e}`));
  warnings.forEach(warn);
  if (!errors.length && !warnings.length) ok("no issues");
}

/* --------------------------------------------------------------------- main - */
const cmd = process.argv[2] ?? "build";
try {
  if (cmd === "init") await init();
  else if (cmd === "scaffold") await scaffold();
  else if (cmd === "build") await build();
  else if (cmd === "show") await show();
  else if (cmd === "check") {
    const b = resolveDefaults(await load());
    const { errors, warnings } = validate(b);
    step("Checking brand config");
    errors.forEach((e) => console.log(`  ${c.red("x")} ${e}`));
    warnings.forEach(warn);
    if (!errors.length && !warnings.length) ok("valid, no warnings");
    if (errors.length) process.exit(1);
  } else {
    console.log(`
  usage: node scripts/brand.mjs <command>

    scaffold create brand/ with blank files to customise (never overwrites)
    init     interactive wizard -> brand/brand.json + brand/tokens.css
    build    brand/brand.json  -> brand/tokens.css   (default)
    show     print the resolved config
    check    validate without writing
`);
    process.exit(1);
  }
} catch (e) {
  console.log(`\n  ${c.red("error:")} ${e.message}\n`);
  process.exit(1);
}
