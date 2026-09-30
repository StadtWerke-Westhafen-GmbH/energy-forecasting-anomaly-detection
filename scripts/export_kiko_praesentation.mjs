/**
 * Rendert Kikos Foliensatz als PNG je Folie und als PDF (1280 × 720).
 * PNGs sind für das Einfügen in die gemeinsame Präsentation gedacht: ohne Seitenzahl
 * (KEEP_NUM=1 behält sie), exakt 2560 × 1440 px, ASCII-Dateinamen.
 */
import {chromium} from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dir = path.join(root, 'docs/presentation/kiko');
const deck = path.join(dir, 'Kiko_ML_Canvas_Methodik_Prueffall.html');
const pngDir = path.join(dir, process.env.PNG_DIR || 'folien');

const ascii = s => s.replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/Ä/g, 'Ae')
  .replace(/Ö/g, 'Oe').replace(/Ü/g, 'Ue').replace(/ß/g, 'ss').replace(/[^\w -]/g, '').trim().replace(/\s+/g, '_');

await fs.mkdir(pngDir, {recursive: true});
// Alte Exporte entfernen, damit umbenannte Folien keine Leichen hinterlassen
for (const f of await fs.readdir(pngDir)) if (f.endsWith('.png')) await fs.rm(path.join(pngDir, f));

const browser = await chromium.launch();
const page = await browser.newPage({viewport: {width: 1328, height: 800}, deviceScaleFactor: 2});
await page.goto(pathToFileURL(deck).href);
await page.evaluate(() => document.fonts.ready);

const problems = [];
const slides = await page.locator('section.slide').all();
// Prüfung im Originallayout
for (const slide of slides) {
  const label = await slide.getAttribute('data-screen-label');
  const overflow = await slide.evaluate(el => {
    const box = el.getBoundingClientRect();
    const foot = el.querySelector('footer')?.getBoundingClientRect();
    const name = c => `${c.tagName.toLowerCase()}.${c.className?.baseVal ?? c.className}`;
    const outside = [...el.querySelectorAll('*')].filter(c => {
      const r = c.getBoundingClientRect();
      return r.width && (r.right > box.right + 1 || r.bottom > box.bottom + 1);
    });
    // Inhalte dürfen nicht näher als 8 px an die Fußzeile heranreichen
    const onFooter = foot ? [...el.querySelectorAll('.body *, .takeaway, .label-strip, .split-r *')].filter(c => {
      const r = c.getBoundingClientRect();
      return r.width && r.bottom > foot.top - 8 && !c.closest('footer');
    }) : [];
    // Inhalte, die unter einen nachfolgenden Streifen (Kernaussage, Label-Leiste) laufen
    const strips = [...el.querySelectorAll('.takeaway, .label-strip')].map(s => s.getBoundingClientRect().top);
    const underStrip = [...el.querySelectorAll('.body *')].filter(c => {
      const r = c.getBoundingClientRect();
      return r.width && strips.some(top => r.bottom > top + 1 && r.top < top);
    });
    return [...outside, ...onFooter, ...underStrip].map(name).slice(0, 5);
  });
  if (overflow.length) problems.push(`${label}: ${overflow.join(', ')}`);
}

// PNG-Export: ohne Deck-Beiwerk, damit jede Folie auf ganzen Pixeln liegt
await page.addStyleTag({content: `.deck-intro,.backup-sep{display:none!important}.deck{gap:0!important;padding:0!important}
  ${process.env.KEEP_NUM ? '' : '.ft .num{visibility:hidden}'}`});
for (const [i, slide] of slides.entries()) {
  const label = ascii(await slide.getAttribute('data-screen-label'));
  const box = await slide.boundingBox();
  if (box.y % 1 || box.width !== 1280 || box.height !== 720) problems.push(`${label}: Box ${JSON.stringify(box)}`);
  await slide.screenshot({path: path.join(pngDir, `${String(i + 1).padStart(2, '0')}_${label}.png`)});
}
if (!process.env.SKIP_PDF) {
  await page.addStyleTag({content: '.ft .num{visibility:visible}'});
  await page.emulateMedia({media: 'print'});
  await page.pdf({path: path.join(dir, 'Kiko_ML_Canvas_Methodik_Prueffall.pdf'), width: '1280px', height: '720px', printBackground: true});
}
await browser.close();
console.log(`${slides.length} Folien exportiert nach ${path.relative(root, pngDir)}`);
if (problems.length) { console.log('Probleme:\n' + problems.join('\n')); process.exitCode = 1; }
