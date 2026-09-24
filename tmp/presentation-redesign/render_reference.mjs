import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';
import sharp from 'sharp';
const root=path.resolve('../..');
const out=path.resolve('reference-render');
await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});
const page=await browser.newPage({viewport:{width:1280,height:720},deviceScaleFactor:1});
for(const name of ['TitleSlide','SectionSlide','ChartSlide','KpiSlide']){
 await page.goto(pathToFileURL(path.join(root,`brand/design-system/slides/${name}.html`)).href);
 await page.evaluate(()=>document.fonts.ready);
 if(name==='ChartSlide')await page.waitForTimeout(1000);
 await page.screenshot({path:path.join(out,`${name}.png`)});
 console.log(name);
}
await browser.close();
for(let batch=0;batch<3;batch++){
 const composite=[];
 for(let j=0;j<6;j++){
  const n=batch*6+j+1;
  const input=await sharp(path.resolve(`source-render/slide-${String(n).padStart(2,'0')}.png`)).resize(640,360).toBuffer();
  composite.push({input,left:(j%2)*640,top:Math.floor(j/2)*360});
 }
 await sharp({create:{width:1280,height:1080,channels:4,background:'#eeeeee'}}).composite(composite).png().toFile(path.resolve(`source-render/montage-${batch+1}.png`));
}
