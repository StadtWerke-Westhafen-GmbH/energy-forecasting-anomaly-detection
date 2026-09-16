import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {chromium} from '@playwright/test';

const origin=process.env.SWW_PREVIEW_URL||'http://127.0.0.1:4173';
const walk=async dir=>(await Promise.all((await fs.readdir(dir,{withFileTypes:true})).map(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]))).flat();

test('all shipped previews load offline; dashboard keyboard navigation works', {timeout:180000}, async()=>{
 const browser=await chromium.launch({channel:process.env.CI?undefined:'msedge',headless:true});
 try{
  const context=await browser.newContext({viewport:{width:1440,height:1000}});
  const external=[];const errors=[];const broken=[];
  await context.route('**/*',route=>{
   const url=route.request().url();
   if(url.startsWith(origin)||url.startsWith('data:')||url.startsWith('blob:'))return route.continue();
   external.push(url);return route.abort();
  });
  const page=await context.newPage();
  page.on('pageerror',e=>errors.push(e.message));
  page.on('response',r=>{if(r.status()>=400)broken.push(r.status()+' '+r.url());});
  const base=path.resolve('brand');
  const pages=(await walk(path.join(base,'design-system'))).filter(f=>f.endsWith('.html'));
  for(const file of pages){
   const url=origin+'/'+path.relative(base,file).replaceAll('\\','/');
   await page.goto(url);await page.waitForLoadState('networkidle');
   assert.equal(await page.locator('body').count(),1,url);
  }
  assert.deepEqual(external,[],'Unexpected external resource requests');
  assert.deepEqual(broken,[],'Broken local asset references');
  assert.deepEqual(errors,[],'Browser JavaScript errors');
  await page.goto(origin+'/design-system/templates/eda-charts/index.html');
  await page.waitForFunction(()=>document.querySelectorAll('.js-plotly-plot').length===15);
  await fs.mkdir('.build/screenshots',{recursive:true});
  await page.screenshot({path:'.build/screenshots/charts.png',fullPage:true});
  await page.goto(origin+'/design-system/ui_kits/energie-cockpit/index.html');
  await page.getByText('Portfolio-Übersicht 03/2025',{exact:true}).waitFor();
  assert.ok(await page.locator('.js-plotly-plot').count()>=2);
  await page.screenshot({path:'.build/screenshots/dashboard.png',fullPage:true});
  await page.getByRole('button',{name:'Zähler-Detail',exact:true}).click();
  await page.getByRole('button',{name:'Anomalie-Ticket anlegen',exact:true}).click();
  const dialog=page.getByRole('dialog');await dialog.waitFor();
  assert.equal(await dialog.evaluate(el=>el.contains(document.activeElement)),true);
  await page.keyboard.press('Shift+Tab');
  assert.equal(await dialog.evaluate(el=>el.contains(document.activeElement)),true,'Focus must remain inside modal');
  await page.keyboard.press('Escape');assert.equal(await dialog.count(),0);
  await page.setViewportSize({width:390,height:844});
  await page.goto(origin+'/design-system/index.html');
  await page.screenshot({path:'.build/screenshots/portal-mobile.png',fullPage:true});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));
  await page.setViewportSize({width:1440,height:1000});
  await page.screenshot({path:'.build/screenshots/portal.png',fullPage:true});
  console.log(`Checked ${pages.length} HTML previews, all 15 charts, and dialog keyboard behaviour.`);
 }finally{await browser.close();}
});
