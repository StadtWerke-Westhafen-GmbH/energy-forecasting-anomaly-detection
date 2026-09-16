/** Check the actual report offline; add rendered PNG fallbacks to the CI notebook. */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import {chromium} from '@playwright/test';

const folder = path.resolve('.build/eda-ci');
const report = await fs.readFile(path.join(folder, 'eda_ci.html'));
const server = http.createServer((request, response) => {
  if (request.url !== '/') return response.writeHead(404).end();
  response.writeHead(200, {'Content-Type': 'text/html; charset=utf-8'}).end(report);
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
let browser;
try {
  browser = await chromium.launch({channel: process.env.CI ? undefined : 'msedge', headless: true});
  const context = await browser.newContext({viewport: {width: 1280, height: 1000}, deviceScaleFactor: 1.5});
  const external = [], errors = [];
  await context.route('**/*', route => {
    const url = route.request().url();
    if (url.startsWith(origin) || url.startsWith('data:') || url.startsWith('blob:')) return route.continue();
    external.push(url);
    return route.abort();
  });
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(origin, {waitUntil: 'load'});
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => {
    const charts = [...document.querySelectorAll('.sww-chart .js-plotly-plot')];
    return charts.length === 32 && charts.every(chart => chart._fullLayout);
  });
  // Render the actual notebook table output on its own, without the report's white page.
  // Host rules deliberately have greater specificity than a plain '.sww-table td'.
  const savedNotebook = JSON.parse(await fs.readFile('ipynb/eda_ci.ipynb', 'utf8'));
  const htmlOutputs = savedNotebook.cells.flatMap(cell => cell.outputs || [])
    .map(output => output.data?.['text/html'] || '')
    .map(html => Array.isArray(html) ? html.join('') : html);
  const tableHtml = htmlOutputs.find(html => html.includes('<div class="sww-table">'));
  assert.ok(tableHtml, 'Notebook must contain a styled table output');
  const {tokens} = JSON.parse(await fs.readFile('src/energy_analytics/visualization/_tokens.json', 'utf8'));
  const rgb = token => `rgb(${tokens[token].slice(1).match(/../g).map(part => parseInt(part, 16)).join(', ')})`;
  const tablePage = await context.newPage();
  for (const mode of ['light', 'dark']) {
    await tablePage.emulateMedia({colorScheme: mode});
    await tablePage.setContent((htmlOutputs.find(html => html.includes('font-family:"IBM Plex Sans"')) || '')
      + `<div class="notebook-output">${tableHtml}</div><table class="host-table"><tr><td>Editor table</td></tr></table>`);
    const hostBackground = mode === 'dark' ? '#071725' : '#FFFFFF';
    const hostText = mode === 'dark' ? '#EEEEEE' : '#222222';
    await tablePage.addStyleTag({content: `
      body {margin:24px;background:${hostBackground};color:${hostText};color-scheme:${mode}}
      .notebook-output table th,.notebook-output table td,.host-table td {
        background:transparent;color:${hostText}
      }
      .notebook-output table tbody tr:nth-child(even) {background:rgba(128,128,128,.12)}
      .notebook-output table tbody tr:hover td {background:rgba(128,128,128,.2)}
    `});
    const first = tablePage.locator('.sww-table tbody tr').nth(0).locator('td').first();
    const second = tablePage.locator('.sww-table tbody tr').nth(1).locator('td').first();
    const colours = async locator => locator.evaluate(element => {
      const style = getComputedStyle(element);
      return {background: style.backgroundColor, text: style.color};
    });
    await tablePage.mouse.move(0, 0);
    assert.deepEqual(await colours(first), {background: rgb('surface-card'), text: rgb('text-primary')}, `${mode}: odd row`);
    assert.deepEqual(await colours(second), {background: rgb('surface-sunken'), text: rgb('text-primary')}, `${mode}: even row`);
    for (const header of await tablePage.locator('.sww-table th').all()) {
      assert.deepEqual(await colours(header), {background: rgb('surface-brand-strong'), text: rgb('text-inverse')}, `${mode}: header`);
    }
    for (const cell of [first, second]) {
      await cell.hover();
      assert.deepEqual(await colours(cell), {background: rgb('surface-accent-subtle'), text: rgb('text-primary')}, `${mode}: hover`);
    }
    assert.deepEqual(await colours(tablePage.locator('.host-table td')), {
      background: 'rgba(0, 0, 0, 0)', text: mode === 'dark' ? 'rgb(238, 238, 238)' : 'rgb(34, 34, 34)',
    }, 'SWW styles must not change unrelated editor tables');
    await tablePage.mouse.move(0, 0);
    await tablePage.locator('.sww-table').screenshot({path: path.join(folder, `table-${mode}.png`)});
  }
  await tablePage.close();
  console.log('Notebook table colours verified on light/dark hosts, including stripes and hover.');
  assert.equal(await page.evaluate(() => document.fonts.check('12px "IBM Plex Sans"')), true);
  assert.equal(await page.evaluate(() => document.fonts.check('600 24px "Geist Mono"')), true);
  assert.equal(await page.locator('.sww-cover').count(), 1);
  assert.equal(await page.locator('.sww-chapter').count(), 6);
  assert.deepEqual(await page.locator('.sww-metric strong').allTextContents(), ['16.800', '700', '24']);
  for (const link of await page.locator('.sww-navigation a').all()) {
    assert.equal(await page.locator(await link.getAttribute('href')).count(), 1, 'Broken chapter link');
  }
  await page.locator('.sww-cover').screenshot({path: path.join(folder, 'cover.png')});
  await page.locator('.sww-chapter').first().screenshot({path: path.join(folder, 'chapter-01.png')});
  await page.evaluate(() => Promise.all([...document.querySelectorAll('.js-plotly-plot')]
    .map(chart => window.Plotly.Plots.resize(chart))));
  await fs.mkdir(path.join(folder, 'charts'), {recursive: true});
  await page.screenshot({path: path.join(folder, 'report-top.png')});
  const charts = page.locator('.sww-chart');
  async function checkBranding(chart, index) {
    const result = await chart.evaluate(element => {
      const plot = element.querySelector('.js-plotly-plot');
      const marks = plot.layout.images.filter(image => image.name === 'sww-brand-logo');
      const image = element.querySelector('.imagelayer image');
      if (!image || marks.length !== 1) return {valid: false};
      const logo = image.getBoundingClientRect();
      const bounds = plot.getBoundingClientRect();
      const area = plot._fullLayout._size;
      const aspect = image.getAttribute('preserveAspectRatio') || 'xMidYMid';
      const source = [...element.querySelectorAll('.annotation')]
        .find(node => node.textContent.includes('Quelle:')).getBoundingClientRect();
      return {
        valid: marks[0].source.startsWith('data:image/png;base64,')
          && marks[0].sizing === 'contain' && aspect !== 'none' && !aspect.includes('slice')
          && marks[0].sizex === 0.10 && logo.width > 0 && logo.height >= 32 && logo.height <= 37,
        outsideData: logo.top >= bounds.top + area.t + area.h,
        insideFigure: logo.bottom <= bounds.bottom && logo.right <= bounds.right,
        separateFromSource: source.right + 12 <= logo.left,
      };
    });
    assert.deepEqual(result, {
      valid: true, outsideData: true, insideFigure: true, separateFromSource: true,
    }, `Brand footer layout in chart ${index + 1}`);
  }
  for (let index = 0; index < 32; index++) {
    const chart = charts.nth(index);
    await checkBranding(chart, index);
    const overlap = await chart.evaluate(element => {
      const title = element.querySelector('.g-gtitle');
      const legend = element.querySelector('.legend');
      if (!title || !legend) return false;
      return legend.getBoundingClientRect().top < title.getBoundingClientRect().bottom;
    });
    assert.equal(overlap, false, `Title and legend overlap in chart ${index + 1}`);
    await chart.screenshot({path: path.join(folder, 'charts', `chart-${String(index + 1).padStart(2, '0')}.png`)});
    console.log(`Rendered ${index + 1}/32: ${(await chart.locator('.gtitle').textContent()).trim()}`);
  }
  await page.setViewportSize({width: 390, height: 844});
  await page.evaluate(() => Promise.all([...document.querySelectorAll('.js-plotly-plot')]
    .map(chart => window.Plotly.Plots.resize(chart))));
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1),
    'Mobile page must not scroll horizontally; wide charts have their own scroll container');
  await page.locator('.sww-cover').screenshot({path: path.join(folder, 'cover-mobile.png')});
  for (let index = 0; index < 32; index++) await checkBranding(charts.nth(index), index);
  await page.setViewportSize({width: 1280, height: 1000});
  await page.evaluate(() => Promise.all([...document.querySelectorAll('.js-plotly-plot')]
    .map(chart => window.Plotly.Plots.resize(chart))));
  const exported = await charts.first().evaluate(async element => {
    const plot = element.querySelector('.js-plotly-plot');
    return window.Plotly.toImage(plot, {format: 'png', width: 1120, height: Math.round(plot._fullLayout.height), scale: 1.5});
  });
  await fs.writeFile(path.join(folder, 'chart-01-standalone.png'), Buffer.from(exported.split(',')[1], 'base64'));
  assert.deepEqual(external, [], 'Report must not load remote fonts or scripts');
  assert.deepEqual(errors, [], 'Browser errors');
  const notebookPath = path.resolve('ipynb/eda_ci.ipynb');
  const notebook = JSON.parse(await fs.readFile(notebookPath, 'utf8'));
  let index = 0;
  for (const cell of notebook.cells) {
    for (const output of cell.outputs || []) {
      if (!output.data?.['application/vnd.plotly.v1+json']) continue;
      const filename = `chart-${String(++index).padStart(2, '0')}.png`;
      output.data['image/png'] = (await fs.readFile(path.join(folder, 'charts', filename))).toString('base64');
      output.metadata ||= {};
      output.metadata['image/png'] = {width: 1120};
    }
  }
  assert.equal(index, 32);
  await fs.writeFile(notebookPath, JSON.stringify(notebook, null, 1) + '\n');
  console.log('32 charts checked at desktop/mobile widths; original logos remain outside data areas.');
  console.log('Offline cover and standalone chart export checked; PNG previews embedded in notebook.');
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
}
