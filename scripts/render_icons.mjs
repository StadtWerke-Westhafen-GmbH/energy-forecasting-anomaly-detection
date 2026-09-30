/**
 * Rendert Lucide-Icons (node_modules/lucide-static, ISC) als transparente PNGs.
 * Aufruf: node scripts/render_icons.mjs <zielordner> '<json: [{"name":"gauge","color":"#084878"}]>' [px]
 * Dateiname: <name>__<farbe ohne #>.png. Bereits vorhandene Dateien werden übersprungen.
 */
import {chromium} from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [outDir, spec, sizeArg] = process.argv.slice(2);
const size = Number(sizeArg || 192);
const items = JSON.parse(spec);
await fs.mkdir(outDir, {recursive: true});

const todo = [];
for (const {name, color} of items) {
  const file = path.join(outDir, `${name}__${color.replace('#', '')}.png`);
  try { await fs.access(file); } catch { todo.push({name, color, file}); }
}
if (todo.length) {
  const browser = await chromium.launch();
  const page = await browser.newPage({viewport: {width: size, height: size}, deviceScaleFactor: 1});
  for (const {name, color, file} of todo) {
    const svg = (await fs.readFile(path.join(root, 'node_modules/lucide-static/icons', `${name}.svg`), 'utf8'))
      .replace(/<!--.*?-->/s, '')
      .replace('stroke="currentColor"', `stroke="${color}"`)
      .replace(/width="24"/, `width="${size}"`).replace(/height="24"/, `height="${size}"`);
    await page.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await page.locator('svg').screenshot({path: file, omitBackground: true});
  }
  await browser.close();
}
console.log(`${items.length} Icons bereit (${todo.length} neu gerendert)`);
