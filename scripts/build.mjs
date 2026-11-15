import {build} from 'esbuild';
import {gunzipSync} from 'node:zlib';
import {readFile,mkdir,writeFile,copyFile} from 'node:fs/promises';
import {validateCitation,promisePredatesOutcome,VIEW_LABELS} from '../worker/core.js';
const readJSON=async(name,fallback)=>{try{return JSON.parse(await readFile(`data/processed/${name}.json`,'utf8'));}catch{try{return JSON.parse(gunzipSync(await readFile(`data/processed/${name}.json.gz`)).toString('utf8'));}catch{return fallback;}}};
const companies=await readJSON('companies',[]),prices=await readJSON('prices',[]),announcements=await readJSON('announcements',[]),documents=await readJSON('documents-compact',await readJSON('documents',[])),universe=await readJSON('universe',companies),sourceChecks=await readJSON('source-checks',[]),research=await readJSON('research',{});
if(!companies.length)throw new Error('Run source ingestion before building: no portfolio companies found.');
const management=await readJSON('management-documents',[]),supplements=await readJSON('supplemental-documents',[]);
const references=await readJSON('reference-checks',{}),managementExtractions=await readJSON('prepared-management-enrichments',[]),enrichments={};
for(const row of [...(references.readyResultsEnrichments||[]),...managementExtractions]){enrichments[row.announcementId]={...row.enrichment,analysisMode:'prepared'};for(const id of row.relatedAnnouncementIds||[])enrichments[id]={...row.enrichment,analysisMode:'prepared'};}
const prepared={};for(const symbol of ['INFY','TCS','TITAN','POLYCAB']){const r=await readJSON(`prepared-research-${symbol}`,null);if(r)prepared[symbol]=r;}
const analyses={...prepared,...research};
const fullDocs=[...await readJSON('documents',documents),...management,...supplements];
const documentMap=new Map([...documents,...management,...supplements].map(d=>[d.id,{...d,pages:[...d.pages]}]));
function includeCitationPages(value){if(!value||typeof value!=='object')return;if(value.documentId&&Number.isInteger(value.page)){const source=fullDocs.find(d=>d.id===value.documentId),page=source?.pages.find(p=>p.page===value.page);if(page){if(!documentMap.has(source.id))documentMap.set(source.id,{...source,pages:[]});const d=documentMap.get(source.id);if(!d.pages.some(p=>p.page===page.page))d.pages.push(page);}}for(const v of Object.values(value))includeCitationPages(v);}
includeCitationPages(analyses);
includeCitationPages(enrichments);
for(const [symbol,report] of Object.entries(analyses)){
 if(!report.views||Object.keys(VIEW_LABELS).some(v=>!report.views[v]))throw new Error(`${symbol}: missing research view`);
 const visit=value=>{if(!value||typeof value!=='object')return;if(value.documentId&&Number.isInteger(value.page)&&!validateCitation(value,fullDocs))throw new Error(`${symbol}: invalid source citation ${value.documentId} p${value.page}`);for(const v of Object.values(value))visit(v);};visit(report);
 for(const row of report.scorecard||[]){if(['met','missed','mixed'].includes(row.status)&&!promisePredatesOutcome(row.promiseSource,row.actualSource,fullDocs))throw new Error(`${symbol}: scorecard verdict lacks earlier promise evidence`);}
}
const seed={generatedAt:new Date().toISOString(),companies,prices,announcements,documents:[...documentMap.values()],universe,sourceChecks,research:analyses,enrichments};
const client=await build({entryPoints:['frontend/app.jsx'],bundle:true,write:false,minify:true,format:'esm',target:'es2022',define:{'process.env.NODE_ENV':'"production"'}});
const css=await readFile('frontend/styles.css','utf8');
await mkdir('dist/server',{recursive:true});await mkdir('dist/.openai',{recursive:true});
await build({entryPoints:['worker/index.js'],bundle:true,outfile:'dist/server/index.js',format:'esm',platform:'browser',target:'es2022',minify:true,external:['node:*'],define:{__SEED__:JSON.stringify(seed),__CLIENT_JS__:JSON.stringify(client.outputFiles[0].text),__CSS__:JSON.stringify(css)}});
await copyFile('.openai/hosting.json','dist/.openai/hosting.json');
console.log(JSON.stringify({companies:companies.length,prices:prices.length,announcements:announcements.length,documents:seed.documents.length,preparedResearch:Object.keys(analyses).length,preparedExtractions:Object.keys(enrichments).length,clientBytes:client.outputFiles[0].text.length}));
