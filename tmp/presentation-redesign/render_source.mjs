import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob, PresentationFile} from '@oai/artifact-tool';
const root=path.resolve('../..');
const out=path.resolve('source-render');
await fs.mkdir(out,{recursive:true});
const p=await PresentationFile.importPptx(await FileBlob.load(path.join(root,'docs/presentation/Modellierung_Anomaliepruefung_IHK.pptx')));
for(let i=0;i<p.slides.items.length;i++){
  const b=await p.export({slide:p.slides.items[i],format:'png',scale:1});
  await fs.writeFile(path.join(out,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await b.arrayBuffer()));
  console.log(`Rendered ${i+1}`);
}
console.log('DONE');
