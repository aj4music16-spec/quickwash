// usage: node tools/render.js <out_dir> [t1 t2 ...]   (no times = every frame)
const {chromium}=require('playwright'),path=require('path'),fs=require('fs');
(async()=>{const root=path.resolve(__dirname,'..'),out=process.argv[2];fs.mkdirSync(out,{recursive:true});const times=process.argv.slice(3).map(Number);
 const cfg=JSON.parse(fs.readFileSync(path.join(root,'config.json'))),meta=JSON.parse(fs.readFileSync(path.join(root,'assets/layers/meta.json')));
 const b=await chromium.launch(),p=await b.newPage({viewport:{width:1080,height:1920}});await p.goto('file://'+path.join(root,'index.html'));
 await p.evaluate(([c,m])=>window.init(c,m),[cfg,meta]);await p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
 const D=await p.evaluate(()=>window.DURATION),F=cfg.fps;const list=times.length?times:Array.from({length:Math.round(D*F)},(_,i)=>i/F);
 for(let i=0;i<list.length;i++){await p.evaluate(t=>window.seek(t),list[i]);
  await p.locator('#stage').screenshot({path:path.join(out,times.length?`t${list[i].toFixed(2).padStart(5,'0')}.jpg`:`f${String(i).padStart(5,'0')}.jpg`),type:'jpeg',quality:93});}
 await b.close();console.log('frames',list.length,'dur',D);})();
