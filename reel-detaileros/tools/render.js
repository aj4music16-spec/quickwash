// usage: node tools/render.js <out_dir> [t1 t2 ...]   (no times = every frame -> out_dir/f00000.jpg)
const {chromium}=require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{
  const out=process.argv[2]; fs.mkdirSync(out,{recursive:true});
  const times=process.argv.slice(3).map(Number);
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+path.resolve(__dirname,'..','index.html'));
  await p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  const D=await p.evaluate(()=>window.DURATION), F=await p.evaluate(()=>window.FPS);
  const list=times.length?times:Array.from({length:Math.round(D*F)},(_,i)=>i/F);
  for (let i=0;i<list.length;i++){
    await p.evaluate(t=>window.seek(t),list[i]);
    const name=times.length?`t${list[i].toFixed(2)}.jpg`:`f${String(i).padStart(5,'0')}.jpg`;
    await p.locator('#stage').screenshot({path:path.join(out,name),type:'jpeg',quality:93});
  }
  await b.close(); console.log('frames',list.length);
})();
