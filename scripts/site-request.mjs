// Private-site smoke test: receives the dispatch credential through hidden stdin.
if(process.stdin.isTTY)process.stdin.setRawMode(true);
process.stdout.write('Ready for private-site check JSON (input hidden).\n');
let input='';const config=await new Promise((resolve,reject)=>{process.stdin.on('data',chunk=>{input+=chunk.toString();if(input.includes('\n')){try{resolve(JSON.parse(input.trim()));}catch(e){reject(e);}}});});
if(process.stdin.isTTY)process.stdin.setRawMode(false);process.stdin.pause();
const response=await fetch(config.url,{method:config.method||'GET',headers:{...(config.token?{'OAI-Sites-Authorization':`Bearer ${config.token}`} : {}),...(config.body?{'Content-Type':'application/json'}:{})},...(config.body?{body:JSON.stringify(config.body)}:{}),signal:AbortSignal.timeout(45000)});
const text=await response.text();let result;try{result=JSON.parse(text);}catch{result=text.slice(0,400);}
if(config.fields&&result&&typeof result==='object')result=Object.fromEntries(config.fields.map(k=>[k,Array.isArray(result[k])?result[k].length:result[k]]));
console.log(JSON.stringify({status:response.status,result}));
