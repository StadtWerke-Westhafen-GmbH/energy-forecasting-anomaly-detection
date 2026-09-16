/** Serve only public design assets on loopback, not project data or .git. */
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../brand');
const port=Number(process.env.PORT||4173);
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.png':'image/png','.svg':'image/svg+xml','.woff2':'font/woff2','.ttf':'font/ttf','.md':'text/plain; charset=utf-8','.pptx':'application/vnd.openxmlformats-officedocument.presentationml.presentation','.potx':'application/vnd.openxmlformats-officedocument.presentationml.template','.docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document','.ipynb':'application/x-ipynb+json'};
const server=http.createServer(async(req,res)=>{
 try{
  const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  const requested=pathname==='/'?'/design-system/index.html':pathname;
  if(!/^\/(design-system|templates)\//.test(requested)||requested.split('/').some(p=>p.startsWith('.'))){res.writeHead(404).end();return;}
  let file=path.resolve(root,'.'+requested);
  if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}
  if((await fs.stat(file)).isDirectory())file=path.join(file,'index.html');
  res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'});
  res.end(await fs.readFile(file));
 }catch(e){res.writeHead(e.code==='ENOENT'?404:400).end();}
});
server.listen(port,'127.0.0.1',()=>console.log(`SWW Design System: http://127.0.0.1:${port}`));
