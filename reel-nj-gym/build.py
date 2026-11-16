import subprocess, sys
S=sys.argv[1]; A=S+"/all/"; O=S+"/v3/seg/"; T=S+"/v3/txt/"; G=S+"/v3/gfx/"
F=G+"LG.woff"; OR="0xF8630A"
V="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p"
n=[0]
def cap(lines,t0=0,t1=99,y=1150,size=130):
    out=[]
    for i,(txt,slab) in enumerate(lines):
        n[0]+=1; p=T+f"c{n[0]}.txt"; open(p,"w").write(txt)
        st=(f"box=1:boxcolor={OR}:boxborderw=18" if slab else "borderw=4:bordercolor=black@0.55:shadowx=0:shadowy=6:shadowcolor=black@0.45")
        out.append(f"drawtext=fontfile={F}:textfile={p}:fontsize={size}:fontcolor=white:{st}:x=(w-tw)/2:y={y}+{i*int(size*1.12)}:enable='between(t,{t0},{t1})'")
    return ",".join(out)
segs=[
 ("IMG_4666.mov",0.3,1.5,False,cap([("YOUR CAR GETS DETAILED",False),("WHILE YOU WORK OUT",True)],y=330,size=140)),
 ("DJI_0049.mp4",2.2,1.2,False,cap([("WE COME",False),("TO YOU",True)],y=330,size=140)),
 "BOOK",
 ("IMG_4664.mov",1.0,1.3,False,cap([("HAND OFF",False),("YOUR KEYS",True)])),
 ("IMG_4673.mov",1.0,1.0,False,cap([("GO TRAIN",False)])),
 ("DJI_0062.mp4",3.0,1.2,False,cap([("YOU LIFT...",False)])),
 ("DJI_0057.mp4",0.5,0.9,False,cap([("WE DETAIL",True)])),
 ("DJI_0064.mp4",10.0,1.1,False,""),
 ("DJI_0059.mp4",5.0,0.8,False,""),
 ("DJI_0065.mp4",8.0,1.0,False,""),
 ("IMG_4680.mov",4.0,0.8,False,""),
 ("DJI_0067.mp4",2.0,0.9,False,""),
 ("DJI_0058.mp4",3.0,0.7,False,""),
 ("IMG_4695.mov",5.3,2.4,True,cap([("CHEST DAY?",False),("SAME DEAL.",True)])),
 ("DJI_0075.mp4",3.0,0.9,False,""),
 ("DJI_0056.mp4",8.0,0.8,False,""),
 ("DJI_0070.mp4",1.5,1.4,False,cap([("WALK OUT TO A",False)])),
 ("IMG_4693.mov",4.6,3.2,True,cap([("SPOTLESS RIDE",True)],0,1.0)+","+cap([("“WOW. IT’S SO GOOD.”",False)],1.0,3.2)),
 "END",
]
def run(cmd): subprocess.run(cmd,check=True)
enc=["-c:v","libx264","-preset","fast","-crf","18","-r","30","-c:a","aac","-b:a","192k","-ar","44100"]
for i,s in enumerate(segs):
    out=O+f"{i:02d}.mp4"
    if s=="BOOK":
        d=1.6
        fc=(f"[0:v]{V},gblur=sigma=28,eq=brightness=-0.12[bg];"
            f"[2:v]format=rgba,scale=eval=frame:w='1080*(1+0.12*max(0\\,1-t/0.18))':h='1920*(1+0.12*max(0\\,1-t/0.18))'[ov];"
            f"[bg][ov]overlay=x=(W-w)/2:y=(H-h)/2:eval=frame,format=yuv420p[v]")
        run(["ffmpeg","-v","error","-y","-ss","0","-t",str(d),"-i",A+"IMG_4665.mov","-f","lavfi","-t",str(d),"-i","anullsrc=r=44100:cl=stereo",
             "-loop","1","-t",str(d),"-i",G+"book.png","-filter_complex",fc,"-map","[v]","-map","1:a"]+enc+["-t",str(d),out])
    elif s=="END":
        d=4.8
        fc=(f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,zoompan=z='1+0.0007*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30[bg];"
            f"[2:v]format=rgba,fade=in:st=0:d=0.3:alpha=1[ov];[bg][ov]overlay=0:0,format=yuv420p[v]")
        run(["ffmpeg","-v","error","-y","-ss","5.0","-t",str(d),"-i",A+"DJI_0050.mp4","-f","lavfi","-t",str(d),"-i","anullsrc=r=44100:cl=stereo",
             "-loop","1","-t",str(d),"-i",G+"end.png","-filter_complex",fc,"-map","[v]","-map","1:a"]+enc+["-t",str(d),out])
    else:
        src,ss,d,nat,c=s; vf=V+(","+c if c else "")
        cmd=["ffmpeg","-v","error","-y","-ss",str(ss),"-t",str(d),"-i",A+src]
        if nat: cmd+=["-vf",vf,"-af","aresample=44100,aformat=channel_layouts=stereo","-map","0:v:0","-map","0:a:0"]
        else: cmd+=["-f","lavfi","-t",str(d),"-i","anullsrc=r=44100:cl=stereo","-vf",vf,"-map","0:v:0","-map","1:a"]
        run(cmd+enc+["-t",str(d),out])
    print("ok",i)
