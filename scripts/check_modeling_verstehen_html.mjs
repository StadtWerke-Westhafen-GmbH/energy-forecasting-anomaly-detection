/** Visual smoke test for the custom HTML outputs in notebook 13. */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {chromium} from '@playwright/test';

const root = path.resolve('.');
const notebookPath = path.join(root, 'notebooks', '13_modellierung_von_grund_auf_verstehen.ipynb');
const outputDir = path.join(root, '.build', 'modeling-learning-html');
const notebook = JSON.parse(await fs.readFile(notebookPath, 'utf8'));

function htmlOutputs(cellId) {
  const cell = notebook.cells.find(candidate => candidate.id === cellId);
  assert.ok(cell, `Missing cell: ${cellId}`);
  return (cell.outputs || [])
    .map(output => output.data?.['text/html'] || '')
    .map(html => Array.isArray(html) ? html.join('') : html)
    .filter(Boolean);
}

function plotlyOutputs(cellId) {
  const cell = notebook.cells.find(candidate => candidate.id === cellId);
  assert.ok(cell, `Missing cell: ${cellId}`);
  const outputs = (cell.outputs || [])
    .filter(candidate => candidate.data?.['application/vnd.plotly.v1+json'])
    .map(output => output.data['application/vnd.plotly.v1+json']);
  assert.ok(outputs.length, `Missing Plotly output: ${cellId}`);
  return outputs;
}

const units = htmlOutputs('learn-units-cards');
assert.equal(units.length, 2, 'Unit explanation should contain cards and one formula output');
assert.ok(units.every(html => html.includes('<style>')), 'Every learning output needs local CSS');
const [metricFigure, ...extraMetricFigures] = plotlyOutputs('learn-metrics-example');
assert.equal(extraMetricFigures.length, 0, 'Metric explanation should stay focused on MAE and RMSE');
assert.deepEqual(metricFigure.data.map(trace => trace.text), [
  ['10 kWh', '10 kWh'],
  ['10 kWh', '20 kWh'],
]);
assert.ok(metricFigure.layout.title.text.includes('RMSE macht den großen Einzelfehler sichtbar'));

await fs.mkdir(outputDir, {recursive: true});
let browser;
try {
  browser = await chromium.launch({channel: process.env.CI ? undefined : 'msedge', headless: true});
  const context = await browser.newContext({viewport: {width: 1180, height: 760}, deviceScaleFactor: 1.25});
  const page = await context.newPage();

  for (const mode of ['light', 'dark']) {
    const hostBackground = mode === 'dark' ? '#071725' : '#f3f6f9';
    const hostText = mode === 'dark' ? '#d9e5ef' : '#141a21';
    await page.emulateMedia({colorScheme: mode});
    await page.setContent(`
      <style>
        body {margin:24px;background:${hostBackground};color:${hostText};font-family:Segoe UI,sans-serif;}
        .output {margin-bottom:14px;}
      </style>
      <main><div class="output">${units[0]}</div><div class="output">${units[1]}</div></main>
    `);

    assert.equal(await page.locator('.learn-card').count(), 3);
    assert.equal(await page.locator('.learn-formula').count(), 1);
    assert.equal(
      await page.locator('.learn-grid').evaluate(element => getComputedStyle(element).display),
      'grid',
    );
    const cardTops = await page.locator('.learn-card').evaluateAll(elements =>
      elements.map(element => Math.round(element.getBoundingClientRect().top)),
    );
    assert.equal(new Set(cardTops).size, 1, `${mode}: unit cards should form one desktop row`);
    assert.equal(
      await page.locator('.learn-card').first().evaluate(element => getComputedStyle(element).backgroundColor),
      'rgb(255, 255, 255)',
      `${mode}: cards need an opaque CI surface`,
    );
    assert.equal(
      await page.locator('.learn-formula strong').evaluate(element => getComputedStyle(element).display),
      'block',
      `${mode}: formula and explanation must not run together`,
    );
    const formulaParts = await page.locator('.learn-formula').evaluate(element => {
      const formula = element.querySelector('strong').getBoundingClientRect();
      const explanation = element.querySelector('span').getBoundingClientRect();
      return {formulaBottom: formula.bottom, explanationTop: explanation.top};
    });
    assert.ok(formulaParts.explanationTop > formulaParts.formulaBottom, `${mode}: formula spacing`);
    assert.ok(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1),
      `${mode}: desktop output must not scroll horizontally`,
    );
    await page.screenshot({path: path.join(outputDir, `units-${mode}.png`), fullPage: true});
  }

  await page.setViewportSize({width: 1365, height: 820});
  await page.setContent(`
    <style>body{margin:0;background:#fff}#chart{width:1365px;height:760px}</style>
    <div id="chart" role="img" aria-label="Vergleich von MAE und RMSE"></div>
  `);
  await page.addScriptTag({path: path.join(root, 'node_modules', 'plotly.js-dist-min', 'plotly.min.js')});
  await page.evaluate(async figure => {
    await window.Plotly.newPlot('chart', figure.data, figure.layout, {
      displayModeBar: false,
      responsive: false,
      staticPlot: true,
    });
  }, metricFigure);
  assert.equal(await page.locator('#chart .trace.bars').count(), 2);
  assert.ok(
    await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1),
    'RMSE comparison must not scroll horizontally',
  );
  await page.locator('#chart').screenshot({path: path.join(outputDir, 'rmse-comparison-light.png')});
  await page.setViewportSize({width: 390, height: 900});
  await page.setContent(`<style>body{margin:16px;background:#071725}</style>${units.join('')}`);
  const mobileCardTops = await page.locator('.learn-card').evaluateAll(elements =>
    elements.map(element => Math.round(element.getBoundingClientRect().top)),
  );
  assert.equal(new Set(mobileCardTops).size, 3, 'Mobile output should stack the cards');
  assert.ok(
    await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1),
    'Mobile output must not scroll horizontally',
  );
  await page.screenshot({path: path.join(outputDir, 'units-mobile-dark.png'), fullPage: true});
  console.log('Notebook learning outputs verified on light, dark and mobile hosts.');
} finally {
  if (browser) await browser.close();
}
