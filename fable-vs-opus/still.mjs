// Sharp stills of a run's index.html at given times, on the same virtual clock as record.mjs.
//   node still.mjs <run dir> <out dir> <t1,t2,...seconds> [width=1920] [height=1080] [scale=2]
// Device scale 2 by default, so a still shown at its CSS size on a Short stays crisp.
import { mkdirSync } from "node:fs";
import { join, resolve } from "node:path";
import puppeteer from "puppeteer-core";
import { VIRTUAL_CLOCK } from "./clock.mjs";

const [dirArg, outArg, timesArg, wArg, hArg, sArg] = process.argv.slice(2);
if (!dirArg || !outArg || !timesArg) { console.error("usage: node still.mjs <run dir> <out dir> <t1,t2,...> [w] [h] [scale]"); process.exit(2); }
const dir = resolve(dirArg), out = resolve(outArg);
mkdirSync(out, { recursive: true });
const times = timesArg.split(",").map(Number).sort((a, b) => a - b);
const width = Number(wArg ?? 1920), height = Number(hArg ?? 1080), scale = Number(sArg ?? 2);

const browser = await puppeteer.launch({
  executablePath: process.env.CHROME ?? "/usr/bin/google-chrome",
  headless: true,
  args: ["--hide-scrollbars", "--mute-audio", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"],
});
try {
  const page = await browser.newPage();
  await page.setViewport({ width, height, deviceScaleFactor: scale });
  await page.evaluateOnNewDocument(VIRTUAL_CLOCK);
  await page.goto(`file://${join(dir, "index.html")}`, { waitUntil: "load", timeout: 60000 });
  await page.evaluate(() => document.fonts?.ready);
  const step = Number(process.env.STEP_MS ?? 1000 / 30); // larger steps are faster; animations stay on the same clock
  let now = 0;
  for (const t of times) {
    while (now + step <= t * 1000) { await page.evaluate((dt) => window.__vt.advance(dt), step); now += step; }
    const file = join(out, `t${String(t).replace(".", "_")}.png`);
    await page.screenshot({ path: file, type: "png" });
    console.log(file);
  }
} finally {
  await browser.close();
}
