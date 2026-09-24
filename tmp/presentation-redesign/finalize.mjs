import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const dir=path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/,'$1'));
const root=path.resolve(dir,'../..');
const skill='C:/Users/Kiko/.codex/plugins/cache/openai-primary-runtime/presentations/26.915.20218/skills/presentations';
process.env.RUNTIME_NODE_MODULES='C:/Users/Kiko/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const referencePath=path.join(root,'docs/presentation/Modellierung_Anomaliepruefung_IHK.pptx');
const result=await finalizePresentation({
 workspaceDir:root,candidatePath:path.join(dir,'candidate.pptx'),
 finalPath:path.join(root,'docs/presentation/Modellierung_Anomaliepruefung_IHK_SWW.pptx'),
 pythonExecutable:'C:/Users/Kiko/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[5,16,17].flatMap(n=>['--require-native-table-slide',String(n)])],
 explicitTotalSlideCount:18,
 requiredNativeChartOwnerSlides:[6,7,8,9,10,11,14,15,16,17],
 requiredNativeTableOwnerSlides:[5,16,17],
 materializeLiteralChartWorkbooks:true,
 fontPolicy:{basis:'reference',families:['IBM Plex Sans','Geist Mono'],referencePath,referenceSha256:createHash('sha256').update(await fs.readFile(referencePath)).digest('hex')},
 verifyArtifactToolImport:true,
 receiptPath:path.join(dir,'final-v3.validation.json'),
});
console.log(JSON.stringify(result));
