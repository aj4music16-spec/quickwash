const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.argv[2]+'/overlays.html');await p.evaluate(()=>document.fonts.ready);
for(const id of ['book','end']){await p.evaluate(id=>{document.querySelectorAll('.f').forEach(e=>e.classList.toggle('on',e.id===id))},id);await p.waitForTimeout(200);
await p.screenshot({path:process.argv[2]+'/'+id+'.png',omitBackground:true});}
await b.close()})();
