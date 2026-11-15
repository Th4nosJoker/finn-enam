// Exercise the built app against a disposable database; never change a real portfolio.
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFile,writeFile} from 'node:fs/promises';
import {gunzipSync} from 'node:zlib';
import {pathToFileURL} from 'node:url';
import {validateCitation,promisePredatesOutcome,change} from '../worker/core.js';

const sqlite=new DatabaseSync(':memory:');
sqlite.exec('CREATE TABLE records(id TEXT PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL, updated_at TEXT NOT NULL)');
const DB={prepare(sql){let values=[];return {bind(...args){values=args;return this;},async first(){return sqlite.prepare(sql).get(...values)||null;},async all(){return {results:sqlite.prepare(sql).all(...values)};},async run(){return sqlite.prepare(sql).run(...values);}};}};
const worker=(await import(pathToFileURL(process.cwd()+'/dist/server/index.js'))).default;
const env={DB},checks=[];
async function api(path,body,method=body===undefined?'GET':'POST',expected=200,origin='https://finn.test'){
 const response=await worker.fetch(new Request('https://finn.test/api/'+path,{method,headers:{Origin:origin,...(body===undefined?{}:{'Content-Type':'application/json'})},...(body===undefined?{}:{body:JSON.stringify(body)})}),env,{waitUntil(){throw new Error('Unexpected background task in offline audit');}});
 const value=await response.json();assert.equal(response.status,expected,JSON.stringify(value));return value;
}
function pass(name,details){checks.push({name,status:'passed',...details});}
const health=await api('health');assert.equal(health.modelConnected,false);assert.equal(health.persistentStorage,true);pass('Built service and persistent database',{documents:health.documents});
const initial=await api('bootstrap');assert.ok(initial.companies.length>=15&&initial.companies.length<=20);assert.equal(initial.categories.length,17);assert.ok(initial.companies.every(c=>c.market?.baselineSessions===20));pass('Portfolio, EOD history and classification',{companies:initial.companies.length,categories:initial.categories.length});
const events=initial.events.flatMap(e=>[e,...e.related]);assert.equal(new Set(events.map(e=>e.id)).size,events.length);assert.ok(initial.events.some(e=>e.routine));assert.ok(initial.events.some(e=>!e.routine));pass('Prioritised digest retains routine and grouped original filings',{filings:events.length,groups:initial.events.length});
assert.equal((await api('search?q=ASIANPAINT'))[0].symbol,'ASIANPAINT');await api('company?symbol=INVALID_TICKER_X',undefined,'GET',400);pass('Directory search and invalid-symbol rejection');
async function sourceJSON(file){try{return JSON.parse(await readFile(`data/processed/${file}.json`,'utf8'));}catch{if(file==='documents'){try{return JSON.parse(await readFile('data/processed/documents-compact.json','utf8'));}catch{return JSON.parse(gunzipSync(await readFile('data/processed/documents-compact.json.gz')).toString('utf8'));}}throw Error(`Missing source dataset: ${file}`);}}
const allDocuments=[];for(const file of ['documents','management-documents','supplemental-documents'])allDocuments.push(...await sourceJSON(file));
let citations=0;
function auditCitations(value){if(!value||typeof value!=='object')return;if(value.documentId&&Number.isInteger(value.page)){assert.ok(validateCitation(value,allDocuments),`Invalid citation ${value.documentId} page ${value.page}`);citations++;}for(const child of Object.values(value))auditCitations(child);}
for(const symbol of ['INFY','TCS','TITAN','POLYCAB']){
 const c=await api('company?symbol='+symbol);assert.equal(Object.keys(c.research.views).length,8);assert.equal(c.research.scorecard.length,4);assert.ok(Object.values(c.research.views).every(v=>v.points.length>0));auditCitations(c.research);
 for(const row of c.research.scorecard)if(['met','missed','mixed'].includes(row.status))assert.ok(promisePredatesOutcome(row.promiseSource,row.actualSource,allDocuments));
 const citation=c.research.views.business.points[0].citations[0],source=await api(`document?symbol=${symbol}&id=${encodeURIComponent(citation.documentId)}&page=${citation.page}`);assert.equal(source.pages.length,1);assert.equal(source.pages[0].page,citation.page);
 pass(symbol+' eight-view research, scorecard and source viewer',{documents:c.documents.length,facts:c.research.facts.length});
}
for(const id of ['106818441','106858944']){const {jobId}=await api('enrich',{id}),job=await api('job/step',{id:jobId});assert.equal(job.status,'complete');auditCitations(job.result);if(id==='106818441'){assert.equal(job.result.results.length,4);for(const row of job.result.results){assert.ok(row.current&&row.previous&&row.yearAgo);assert.equal(row.current.unit,row.previous.unit);assert.equal(row.current.basis,row.yearAgo.basis);assert.ok(Number.isFinite(change(row.current.value,row.previous.value).percent));assert.ok(Number.isFinite(change(row.current.value,row.yearAgo.value).percent));}pass('Actual results filing: four metrics with comparable QoQ and YoY');}else{assert.ok(job.result.management.person&&job.result.management.background&&job.result.management.source);pass('Management filing with sourced professional background');}}
const symbols=initial.companies.map(c=>c.symbol);await api('portfolio',{symbols:[...symbols,'ASIANPAINT']},'PUT');assert.equal((await api('bootstrap')).companies.length,symbols.length+1);await api('portfolio',{symbols},'PUT');assert.equal((await api('bootstrap')).companies.length,symbols.length);pass('Portfolio additions, removal and database readback');
const updated={...initial.rules,pricePercent:0.1,volumeMultiple:1,minPriority:0,categories:initial.categories};await api('rules',updated,'PUT');let b=await api('bootstrap');assert.deepEqual(b.rules,updated);assert.ok(b.alerts.some(a=>a.type==='price'));assert.ok(b.alerts.some(a=>a.type==='volume'));assert.ok(b.alerts.some(a=>a.type==='announcement'));const ids=b.alerts.map(a=>a.id).sort();await api('rules',updated,'PUT');assert.deepEqual((await api('bootstrap')).alerts.map(a=>a.id).sort(),ids);await api('alerts/read',{});assert.ok((await api('bootstrap')).alerts.every(a=>a.read));await api('rules',{...updated,pricePercent:-1},'PUT',400);pass('Configurable alerts, deduplication, read state and invalid-rule rejection',{alerts:ids.length});
await api('portfolio',{symbols},'PUT',403,'https://another-origin.test');await api('backfill',{from:'2026-11-15',to:'2026-10-01'},'POST',400);pass('Cross-origin write and invalid date-window rejection');
const {jobId}=await api('ask',{symbol:'INFY',question:'Does profit turn into cash?'}),job=await api('job/step',{id:jobId});assert.equal(job.status,'failed');assert.match(job.error,/not connected/);pass('Disconnected model has an explicit recoverable error');
const report={at:new Date().toISOString(),status:'passed',checks,citationsVerified:citations,liveModelTested:false,scope:'Offline integrated workflows and source integrity. Does not establish live model quality or live exchange availability.'};
await writeFile('docs/feature-audit.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));sqlite.close();
