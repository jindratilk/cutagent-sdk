import assert from 'node:assert/strict';
import {mkdtemp,writeFile,readFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import test from 'node:test';
import {ensureFreeBroker} from '../runtime/local/free-broker.mjs';

async function fixture(t, mode='normal') {
 const directory=await mkdtemp(join(tmpdir(),'free-broker-life-'));
 t.after(()=>rm(directory,{recursive:true,force:true}));
 const script=join(directory,'broker.mjs'), state=join(directory,'state');
 await writeFile(script,`import fs from 'node:fs';const p=process.env.BROKER_TEST_STATE;if(process.argv[2]==='status'){console.log(JSON.stringify(fs.existsSync(p)?{running:true}:(process.env.BROKER_TEST_MODE==='auth'?{running:false,error_code:'EMBEDDED_BRIDGE_AUTH_FAILED'}:{running:false})));}else if(process.env.BROKER_TEST_MODE==='fail'){process.exit(7);}else{fs.writeFileSync(p,String(process.pid));process.on('SIGTERM',()=>{fs.unlinkSync(p);process.exit(0)});setInterval(()=>{},1000);}`);
 return {python:process.execPath,script,env:{...process.env,BROKER_TEST_STATE:state,BROKER_TEST_MODE:mode},state};
}
test('runtime owns only a broker it starts and shuts it down',async t=>{
 const f=await fixture(t);const broker=await ensureFreeBroker(f);t.after(()=>broker.close());
 assert.equal(broker.owned,true);assert.ok(Number(await readFile(f.state,'utf8'))>0);
 const reused=await ensureFreeBroker(f);assert.equal(reused.owned,false);await reused.close();
 assert.ok(await readFile(f.state,'utf8'));await broker.close();await assert.rejects(readFile(f.state));await broker.close();
});
test('broker startup failure fails closed with no successful runtime claim',async t=>{
 const f=await fixture(t,'fail');await assert.rejects(ensureFreeBroker(f),/stopped during startup/);await assert.rejects(readFile(f.state));
});

test('authentication failure never starts a competing broker',async t=>{
 const f=await fixture(t,'auth');await assert.rejects(ensureFreeBroker(f),/rejected authentication/);await assert.rejects(readFile(f.state));
});
