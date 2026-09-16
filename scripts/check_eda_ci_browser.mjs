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
  assert.equal(await page.evaluate(() => document.fonts.check('12px "IBM Plex Sans"')), true);
  await page.evaluate(() => Promise.all([...document.querySelectorAll('.js-plotly-plot')]
    .map(chart => window.Plotly.Plots.resize(chart))));
  await fs.mkdir(path.join(folder, 'charts'), {recursive: true});
  await page.screenshot({path: path.join(folder, 'report-top.png')});
  const charts = page.locator('.sww-chart');
  for (let index = 0; index < 32; index++) {
    const chart = charts.nth(index);
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
  console.log('32 charts rendered offline; PNG previews embedded for non-interactive notebook viewers.');
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
}
