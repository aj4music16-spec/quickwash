const {chromium}=require('playwright');(async()=>{const dir=process.argv[2];const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+dir+'/captions.html');await p.evaluate(()=>document.fonts.ready);
const ids=await p.$$eval('.f',e=>e.map(x=>x.id));
for(const id of ids){await p.evaluate(id=>document.querySelectorAll('.f').forEach(e=>e.classList.toggle('on',e.id===id)),id);await p.screenshot({path:dir+'/cap/'+id+'.png',omitBackground:true});}
await b.close();console.log(ids.join(' '))})();
