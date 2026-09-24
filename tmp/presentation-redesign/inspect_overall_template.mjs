import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const root=path.resolve('../..');
const deck=await PresentationFile.importPptx(await FileBlob.load(path.join(root,'docs/Copy of Praesentationsvorlage_IHK.pptx')));
const dir=path.resolve('overall-template-preview');await fs.mkdir(dir,{recursive:true});
for(const n of [1,5,7,8,9,10]){
 const png=await deck.export({slide:deck.slides.items[n-1],format:'png',scale:1});
 await fs.writeFile(path.join(dir,`slide-${n}.png`),new Uint8Array(await png.arrayBuffer()));
}
console.log(`Read-only review: ${deck.slides.items.length} slides, six previews.`);
