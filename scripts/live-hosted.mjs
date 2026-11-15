// The private dispatch token is supplied through hidden stdin, never command arguments.
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
if(process.stdin.isTTY)process.stdin.setRawMode(true);console.log('Ready for private live-check JSON (input hidden).');
let input='';const config=await new Promise((resolve,reject)=>process.stdin.on('data',chunk=>{input+=chunk.toString();if(input.includes('\n')){try{resolve(JSON.parse(input.trim()));}catch(e){reject(e);}}}));
if(process.stdin.isTTY)process.stdin.setRawMode(false);process.stdin.pause();
const origin=new URL(config.url);if(origin.protocol!=='https:'||origin.hostname!=='finn-enam-rohit-2026.wildcarol8.chatgpt.site')throw Error('Use the existing FINN private origin.');
async function api(path,body){const response=await fetch(new URL('/api/'+path,origin),{method:body===undefined?'GET':'POST',headers:{'OAI-Sites-Authorization':`Bearer ${config.token}`,...(body===undefined?{}:{'Content-Type':'application/json'})},...(body===undefined?{}:{body:JSON.stringify(body)}),signal:AbortSignal.timeout(180000)});const value=await response.json();if(!response.ok)throw Error(`${path}: ${value.error||response.status}`);return value;}
const health=await api('health');assert.equal(health.modelConnected,true);console.log(JSON.stringify({check:'hosted-model-connected',ok:true}));
const mode=config.mode||'question',symbol=config.symbol||'INFY';let jobId=config.jobId;
if(!jobId){const request=mode==='question'?['ask',{symbol,question:config.question||'Does the company convert its profits into cash? Cite dated reported figures and limitations.'}]:mode==='enrichment'?['enrich',{id:config.eventId}]:['research',{symbol}];jobId=(await api(...request)).jobId;}
console.log(JSON.stringify({check:'live-job',mode,symbol,jobId}));
let job;for(let i=0;i<40;i++){job=await api('job/step',{id:jobId});console.log(JSON.stringify({status:job.status,stage:job.stage,progress:job.progress,error:job.error}));if(job.status!=='running')break;}
await mkdir('.local/live-audit',{recursive:true});await writeFile(`.local/live-audit/hosted-${mode}-${mode==='enrichment'?config.eventId:symbol}.json`,JSON.stringify(job,null,2)+'\n');
assert.equal(job.status,'complete',job.error||'Job did not complete');
const result=job.result;console.log(JSON.stringify({check:'live-result',mode,symbol,views:result.views?Object.keys(result.views).length:undefined,points:result.points?.length,viewPoints:result.views?Object.fromEntries(Object.entries(result.views).map(([k,v])=>[k,v.points.length])):undefined,facts:result.facts?.length,quarters:result.scorecard?.length,metrics:result.results?.filter(r=>r.current).length,management:!!result.management,usage:result.usage}));
if(mode==='question')assert.ok(result.points.length>0,'No source-backed answer points');
if(mode==='research'){assert.equal(Object.keys(result.views).length,8);assert.ok(Object.values(result.views).every(v=>v.points.length>0),'A research view has no validated points');assert.equal(result.scorecard.length,4);assert.ok(result.facts.length>0);}
