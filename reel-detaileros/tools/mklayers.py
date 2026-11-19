import json, sys
import numpy as np
from PIL import Image, ImageFilter
D=sys.argv[1]
L={
 1:{"notif":(26,700,916,932)},
 2:{"logo":(266,90,672,194),"h1":(75,226,522,352),"h2":(522,226,882,362),"phone":(82,372,826,1512)},
 3:{"logo":(290,94,648,186),"head":(108,220,832,388),"sub":(148,403,792,502),"card":(242,546,706,1012)},
 4:{"logo":(243,205,698,322),"h1":(62,374,888,464),"h2":(234,466,708,616),"phones":(34,628,912,1238),"row":(110,1274,830,1328),"cta":(62,1376,878,1524)},
 5:{"logo":(98,213,842,352),"t1":(84,444,886,552),"t2":(88,552,882,670),"t3":(88,670,882,806),"btn":(66,852,874,1098),"search":(98,1098,847,1154),"walk":(108,1253,832,1392)},
}
# sub-layers that sit on top of another layer (not removed from plate separately)
SUB={3:{"paid":(356,894,590,978),"check":(404,648,540,744)}}
meta={}
for s,els in L.items():
    im=Image.open(f"{D}/src/s{s}.png").convert("RGB"); a=np.asarray(im).astype(np.float32)
    H,W=a.shape[:2]; mask=np.ones((H,W),np.float32)
    for (x0,y0,x1,y1) in els.values(): mask[y0:y1,x0:x1]=0
    def box(x,r):
        # separable box blur with edge padding, x: HxW or HxWxC float
        for ax in (0,1):
            pad=[(0,0)]*x.ndim; pad[ax]=(r+1,r)
            xp=np.pad(x,pad,mode='edge'); c=np.cumsum(xp,axis=ax)
            hi=np.take(c,range(2*r+1,c.shape[ax]),axis=ax); lo=np.take(c,range(0,c.shape[ax]-2*r-1),axis=ax)
            x=(hi-lo)/(2*r+1)
        return x
    def gblur(x,r):
        for _ in range(3): x=box(x,max(1,r//2))
        return x
    num_src=a*mask[...,None]; plate=a.copy(); done=mask.copy()
    for r in (8,16,32,64,128,256,512):
        mb=gblur(mask,r); est=gblur(num_src,r)/np.maximum(mb,1e-6)[...,None]
        sel=(done<0.5)&((mb>0.18)|(r==512))
        plate[sel]=est[sel]; done[sel]=1
    plate=plate.clip(0,255)
    # soften the filled area
    sm=gblur(plate,10); hole=mask<0.5; plate[hole]=sm[hole]
    plate=plate.astype(np.uint8)
    Image.fromarray(plate).save(f"{D}/layers/s{s}_plate.jpg",quality=95)
    meta[s]={}
    allels=dict(els); allels.update(SUB.get(s,{}))
    for name,(x0,y0,x1,y1) in allels.items():
        crop=im.crop((x0,y0,x1,y1)).convert("RGBA")
        w,h=crop.size; f=6
        al=np.ones((h,w),np.float32)
        for i in range(f):
            v=(i+1)/(f+1)
            al[i,:]=np.minimum(al[i,:],v); al[h-1-i,:]=np.minimum(al[h-1-i,:],v)
            al[:,i]=np.minimum(al[:,i],v); al[:,w-1-i]=np.minimum(al[:,w-1-i],v)
        arr=np.asarray(crop).copy(); arr[...,3]=(al*255).astype(np.uint8)
        Image.fromarray(arr).save(f"{D}/layers/s{s}_{name}.png")
        meta[s][name]=[x0,y0,x1-x0,y1-y0]
json.dump(meta,open(f"{D}/layers/meta.json","w"))
print(json.dumps(meta))
# blank the check + PAID pill on the card layer so they can animate in
card=Image.open(f"{D}/layers/s3_card.png"); arr=np.asarray(card).copy()
cx,cy=242,546
bg=arr[200:230,20:60,:3].reshape(-1,3).mean(axis=0)
for (x0,y0,x1,y1) in [(356,894,590,978),(404,648,540,744)]:
    arr[y0-cy:y1-cy, x0-cx:x1-cx, :3]=bg.astype(np.uint8)
Image.fromarray(arr).save(f"{D}/layers/s3_card.png")
from PIL import ImageDraw
def round_mask(path, inset, radius):
    im=Image.open(path).convert("RGBA"); w,h=im.size
    big=Image.new("L",(w*4,h*4),0); d=ImageDraw.Draw(big)
    d.rounded_rectangle((inset[0]*4,inset[1]*4,(w-inset[2])*4,(h-inset[3])*4),radius*4,fill=255)
    m=big.resize((w,h),Image.LANCZOS); im.putalpha(m); im.save(path)
round_mask(f"{D}/layers/s3_card.png",(9,8,13,12),30)
round_mask(f"{D}/layers/s1_notif.png",(5,8,5,7),44)
