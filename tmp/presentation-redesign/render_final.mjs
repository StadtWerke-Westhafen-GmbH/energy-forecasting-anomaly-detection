import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {GlobalFonts} from '@napi-rs/canvas';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const dir=path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/,'$1'));
const root=path.resolve(dir,'../..');
const fontDir=path.join(root,'brand/design-system/dist/fonts');
const {FontLibrary}=await import(pathToFileURL(path.join(dir,'node_modules/@oai/artifact-tool/node_modules/skia-canvas/lib/index.js')).href);
for(const [slug,name,weights] of [['ibm-plex-sans','IBM Plex Sans',[400,500,600,700]],['geist-mono','Geist Mono',[400,500,600]]]){
 const files=weights.map(w=>path.join(fontDir,`${slug}-${w}.ttf`));
 files.forEach(f=>GlobalFonts.registerFromPath(f,name));FontLibrary.use(name,files);
}
const p=await PresentationFile.importPptx(await FileBlob.load(path.join(root,'docs/presentation/Modellierung_Anomaliepruefung_IHK_SWW.pptx')));
const output=path.join(dir,'final-render');await fs.mkdir(output,{recursive:true});
for(let i=0;i<p.slides.items.length;i++){
 const png=await p.export({slide:p.slides.items[i],format:'png',scale:1.5});
 await fs.writeFile(path.join(output,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
console.log(`Final deck imported and ${p.slides.items.length} slides rendered.`);
