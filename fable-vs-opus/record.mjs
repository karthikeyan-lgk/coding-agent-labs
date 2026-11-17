// Record a run's index.html to MP4, frame by frame on a virtual clock.
//   node record.mjs <run dir> [seconds=30] [fps=30] [width=1920] [height=1080]
// Time-based APIs (performance.now, Date.now, requestAnimationFrame, setTimeout/setInterval, CSS and Web
// Animations) are driven by our clock, so a busy machine can't drop or smear frames: frame N always shows t = N/fps.
// Sound is not recorded (AudioContext keeps real time); the page's own audio is noted, not captured.
import { spawn } from "node:child_process";
import { existsSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import puppeteer from "puppeteer-core";
import { VIRTUAL_CLOCK } from "./clock.mjs";

const [dirArg, secArg, fpsArg, wArg, hArg] = process.argv.slice(2);
if (!dirArg) { console.error("usage: node record.mjs <run dir> [seconds] [fps] [width] [height]"); process.exit(2); }
const dir = resolve(dirArg);
const html = join(dir, "index.html");
if (!existsSync(html)) { console.error(`no ${html}`); process.exit(1); }
const seconds = Number(secArg ?? 30), fps = Number(fpsArg ?? 30);
const width = Number(wArg ?? 1920), height = Number(hArg ?? 1080);
const out = join(dir, "recording.mp4");



const browser = await puppeteer.launch({
  executablePath: process.env.CHROME ?? "/usr/bin/google-chrome",
  headless: true,
  args: ["--autoplay-policy=no-user-gesture-required", "--hide-scrollbars", "--mute-audio", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"],
});
const log = [];
try {
  const page = await browser.newPage();
  page.on("console", (m) => { if (m.type() === "error" || m.type() === "warn") log.push(`${m.type()}: ${m.text()}`); });
  page.on("pageerror", (e) => log.push(`pageerror: ${e.message}`));
  await page.setViewport({ width, height, deviceScaleFactor: 1 });
  await page.evaluateOnNewDocument(VIRTUAL_CLOCK);
  await page.goto(`file://${html}`, { waitUntil: "load", timeout: 60000 });
  const webgl = await page.evaluate(() => !!document.createElement("canvas").getContext("webgl2"));
  // Let fonts and first-frame setup settle without moving the clock.
  await page.evaluate(() => document.fonts?.ready);

  const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(fps), "-i", "-",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], { stdio: ["pipe", "inherit", "inherit"] });
  const frames = Math.round(seconds * fps);
  for (let i = 0; i < frames; i++) {
    await page.evaluate((dt) => window.__vt.advance(dt), i === 0 ? 0 : 1000 / fps);
    const png = await page.screenshot({ type: "png", optimizeForSpeed: true });
    if (!ff.stdin.write(png)) await new Promise((r) => ff.stdin.once("drain", r));
    if (i % (fps * 5) === 0) process.stderr.write(`frame ${i}/${frames}\n`);
  }
  ff.stdin.end();
  await new Promise((r, j) => ff.on("close", (c) => (c === 0 ? r() : j(new Error(`ffmpeg exit ${c}`)))));
  writeFileSync(join(dir, "recording.log"), [`webgl2: ${webgl}`, `seconds: ${seconds} fps: ${fps} size: ${width}x${height}`, ...log].join("\n") + "\n");
  console.log(`${out} (${frames} frames, webgl2 ${webgl}, ${log.length} console errors/warnings)`);
} finally {
  await browser.close();
}
