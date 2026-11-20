import {chromium} from 'playwright-core';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import fs from 'node:fs/promises';

const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const external=process.env.FORESTPROOF_PUBLIC_ORIGIN;
const base=external||'http://127.0.0.1:18463';
const output=process.env.FORESTPROOF_SCREENSHOT_DIR||path.join(repo,'.tmp/public-atlas-smoke');
await fs.mkdir(output,{recursive:true});
const server=external?null:spawn(process.env.PYTHON||'python',['-u','-m','tools.sentinel_visibility.preview_fixture','--port','18463'],{cwd:repo,stdio:['ignore','pipe','pipe']});
server?.stderr.on('data',b=>process.stderr.write(b));
let browser;
async function fit(page){assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Horizontal overflow');}
async function ready(page){await page.waitForFunction(()=>document.querySelector('[data-atlas-map]')?.dataset.ready==='true',{},{timeout:40000});}
try{
 for(let n=0;n<60;n++){try{const r=await fetch(base+'/atlas/geta');if(r.ok)break;}catch{}if(n===59)throw new Error('Public fixture did not start');await new Promise(r=>setTimeout(r,500));}
 browser=await chromium.launch({executablePath:process.env.FORESTPROOF_CHROME_EXECUTABLE||undefined,headless:true,timeout:60000,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 for(const [name,width] of [['desktop',1440],['mobile',390],['narrow',320]]){
  const context=await browser.newContext({viewport:{width,height:1000},hasTouch:width<600,isMobile:width<600,reducedMotion:'reduce'}),page=await context.newPage(),errors=[],outside=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>{if(m.type()==='warning'||m.type()==='error')console.log(name,m.text())});
  page.on('request',r=>{if(new URL(r.url()).origin!==base)outside.push(r.url())});
  try{
   assert.equal((await page.goto(base+'/welcome',{waitUntil:'networkidle'})).status(),200);
   await fit(page);await page.screenshot({path:path.join(output,name+'-welcome.png'),fullPage:true});
   const transfer=await page.evaluate(()=>performance.getEntriesByType('resource').reduce((n,e)=>n+e.encodedBodySize,0));
   assert.ok(transfer<1_500_000,'Landing resource budget exceeded: '+transfer);
   await page.locator('.hero-actions a[href="/atlas/geta"]').click();await page.waitForURL('**/atlas/geta');
   await ready(page);await fit(page);
   assert.equal(await page.locator('[data-atlas-visible]').innerText(),'6,424');
   assert.equal(await page.locator('[data-atlas-vegetation]').innerText(),'6,346');
   await page.screenshot({path:path.join(output,name+'-atlas-2d.png'),fullPage:true});
   await page.locator('[data-map-terrain]').click();assert.equal(await page.locator('[data-map-terrain]').getAttribute('aria-pressed'),'true');
   await page.waitForTimeout(800);await ready(page);await page.screenshot({path:path.join(output,name+'-atlas-3d.png'),fullPage:true});
   await page.locator('[data-map-terrain]').click();assert.equal(await page.locator('[data-map-terrain]').getAttribute('aria-pressed'),'false');
   const input=width<600?'[data-atlas-date-compact]':'[data-atlas-date]';
   await page.locator(input).selectOption('2026-11-13');assert.equal(await page.locator('[data-atlas-visible]').innerText(),'3');
   if(width<600)await page.locator('.atlas-mobile-sheet > summary').click();
   await page.locator('[data-atlas-grid-choice="T37MBV"]').click();assert.match(await page.locator('[data-atlas-image-state]').innerText(),/No published image/);
   await page.reload({waitUntil:'networkidle'});await ready(page);assert.equal(await page.locator('[data-atlas-grid-choice="T37MBV"]').getAttribute('aria-pressed'),'true');
   const atlasTransfer=await page.evaluate(()=>performance.getEntriesByType('resource').reduce((n,e)=>n+e.encodedBodySize,0));assert.ok(atlasTransfer<5_000_000,'Atlas resource budget exceeded: '+atlasTransfer);
   await page.locator('[data-atlas-laboratory]').first().click();await page.waitForURL('**/visibility?*');
   await page.waitForLoadState('networkidle');assert.equal(await page.locator('[data-visible-count]').innerText(),'3');await fit(page);
   assert.deepEqual(errors,[]);assert.deepEqual(outside,[]);
   console.log(JSON.stringify({name,landingBytes:transfer,atlasBytes:atlasTransfer,geography:'ready',terrain:'toggled',selection:'passed'}));
  }catch(error){await page.screenshot({path:path.join(output,name+'-failure.png'),fullPage:true}).catch(()=>{});console.error(await page.locator('[data-map-message]').textContent().catch(()=>''));throw error;}finally{await context.close();}
 }
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}}),np=await nojs.newPage();
 await np.goto(base+'/welcome');assert.equal(await np.locator('a[href="/atlas/geta"]').count()>0,true);
 await np.goto(base+'/atlas/geta');assert.equal(await np.locator('[data-atlas-archive]').getAttribute('open'),'');await fit(np);await nojs.close();
 const blocked=await browser.newContext({viewport:{width:390,height:844}}),bp=await blocked.newPage();
 await bp.addInitScript(()=>{const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return type.includes('webgl')?null:original.call(this,type,...args)};});
 await bp.goto(base+'/atlas/geta',{waitUntil:'networkidle'});await bp.waitForFunction(()=>document.querySelector('[data-map-message]').textContent.includes('unavailable'));
 assert.equal(await bp.locator('[data-atlas-visible]').innerText(),'6,424');
 const reference=bp.locator('.atlas-reference');
 assert.equal(await bp.locator('.atlas-reference image[href="/assets/geta-relief.png"]').count(),1);
 const box=()=>reference.getAttribute('viewBox').then(v=>v.split(/\s+/).map(Number));
 const originalBox=await box();await bp.locator('[data-map-zoom="in"]').click();assert.ok((await box())[2]<originalBox[2]);
 await bp.locator('[data-map-reset]').click();assert.deepEqual(await box(),originalBox);
 await reference.focus();await bp.keyboard.press('ArrowRight');assert.ok((await box())[0]>originalBox[0]);
 await bp.locator('[data-map-reset]').click();
 await fit(bp);await bp.screenshot({path:path.join(output,'mobile-no-webgl.png'),fullPage:true});await blocked.close();
 console.log('Public geographic smoke passed; no-script and WebGL-failure reading retained.');
}finally{await browser?.close();if(server)server.kill('SIGTERM');}
