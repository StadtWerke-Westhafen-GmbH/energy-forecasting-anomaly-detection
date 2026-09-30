/**
 * Diagramme aus Kikos HTML-Deck als PNG für die Team-Präsentation (Google Slides).
 *
 * Google Slides wandelt PowerPoint-Diagramme beim Import in Bilder um und zeichnet sie dabei
 * selbst; darübergelegte Beschriftungen verrutschen. Deshalb setzt build_team_pptx.py an
 * diesen Stellen fertige Bilder ein. Jedes Inline-SVG ab 200 px Breite wird 3-fach
 * gerendert; charts.json hält Folie, SVG-Index (Reihenfolge wie querySelectorAll('svg'))
 * und das Rechteck relativ zur Folie fest.
 */
import {chromium} from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const deck = path.join(root, 'docs/presentation/kiko/Kiko_ML_Canvas_Methodik_Prueffall.html');
const outDir = path.join(root, 'docs/presentation/team/assets/charts');

await fs.mkdir(outDir, {recursive: true});
for (const f of await fs.readdir(outDir)) if (f.endsWith('.png')) await fs.rm(path.join(outDir, f));

const browser = await chromium.launch();
const page = await browser.newPage({viewport: {width: 1328, height: 800}, deviceScaleFactor: 3});
await page.goto(pathToFileURL(deck).href);
await page.evaluate(() => document.fonts.ready);

const charts = [];
const slides = await page.locator('section.slide').all();
for (const [s, slide] of slides.entries()) {
  const boxes = await slide.evaluate(el => {
    const base = el.getBoundingClientRect();
    return [...el.querySelectorAll('svg')].map((svg, i) => {
      const r = svg.getBoundingClientRect();
      return {svg: i, x: r.left - base.left, y: r.top - base.top, w: r.width, h: r.height};
    }).filter(b => b.w >= 200);
  });
  for (const b of boxes) {
    const file = `s${String(s + 1).padStart(2, '0')}_svg${String(b.svg).padStart(2, '0')}.png`;
    await slide.locator('svg').nth(b.svg).screenshot({path: path.join(outDir, file)});
    charts.push({slide: s, ...b, file});
  }
}
await fs.writeFile(path.join(outDir, 'charts.json'), JSON.stringify(charts, null, 1));
await browser.close();
console.log(`${charts.length} Diagramme → ${path.relative(root, outDir)}`);
