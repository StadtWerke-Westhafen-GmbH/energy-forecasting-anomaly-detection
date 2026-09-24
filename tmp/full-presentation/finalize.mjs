import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const dir=path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/,'$1'));
const root=path.resolve(dir,'../..');
const skill='C:/Users/Kiko/.codex/plugins/cache/openai-primary-runtime/presentations/26.915.20218/skills/presentations';
process.env.RUNTIME_NODE_MODULES='C:/Users/Kiko/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const referencePath=path.join(root,'docs/Copy of Praesentationsvorlage_IHK.pptx');
const m=JSON.parse(await fs.readFile(path.join(dir,'manifest.json'),'utf8'));
const version=process.argv[2]||'v1';
const result=await finalizePresentation({
 workspaceDir:root,candidatePath:path.join(dir,'candidate.pptx'),
 finalPath:path.join(root,'docs/presentation/Gesamtpraesentation_IHK_SWW.pptx'),
 pythonExecutable:'C:/Users/Kiko/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...m.tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],
 explicitTotalSlideCount:m.slides,
 requiredNativeChartOwnerSlides:m.chartOwners,
 requiredNativeTableOwnerSlides:m.tableOwners,
 materializeLiteralChartWorkbooks:true,
 fontPolicy:{basis:'design',families:['IBM Plex Sans','Geist Mono']},
 verifyArtifactToolImport:true,
 receiptPath:path.join(dir,`final-${version}.validation.json`),
});
console.log(JSON.stringify(result));
