"""Add voiceover, music and sound effects to the silent cuts from build.py.

usage: python3 mix.py <work_dir> <dist_dir> [reel ...]
Music ducks under the voice and under each effect; output is normalised to about -14 LUFS.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK, DIST = sys.argv[1], sys.argv[2]
ONLY = sys.argv[3:]
VO = os.path.join(HERE, "audio/vo")
MUS = os.path.join(HERE, "audio")
SFX = os.path.join(HERE, "../reel-detaileros/assets/audio")

# reel: (output name, music, [(vo line, time)], [(effect, time, gain)])
REELS = {
    "qw-99-whats-included": ("quickwash-99-whats-included.mp4", "m_qw99", [("a1", 0.2), ("a2", 3.2), ("a3", 5.9), ("a4", 8.2), ("a5", 10.3), ("a6", 12.6), ("a7", 14.2), ("a8", 16.5)],
        [("tick", t, 0.5) for t in (5.8, 7.0, 8.1, 9.1, 10.2, 11.3, 12.5, 14.1)] + [("whoosh", 18.45, 0.6), ("pop", 18.65, 0.4)]),
    "qw-dirty": ("quickwash-dirty.mp4", "m_dirty", [("b1", 0.2), ("b2", 2.15), ("b3", 3.0), ("b4", 4.45), ("b5", 7.2), ("b6", 9.1)],
        [("whoosh", 2.8, 0.5), ("whoosh", 11.15, 0.6), ("pop", 11.35, 0.4)]),
    "dos-storefront-vs-dms": ("detaileros-storefront-vs-dms.mp4", "m_store", [("c1", 0.2), ("c2", 4.8), ("c3", 7.4), ("c4", 10.6), ("c5", 12.8), ("c6", 15.0)],
        [("pop", 0.35, 0.5), ("pop", 1.5, 0.5), ("pop", 2.45, 0.5), ("pop", 3.3, 0.5), ("whoosh", 4.45, 0.6), ("impact", 14.82, 0.8)]),
    "dos-book-your-regulars": ("detaileros-book-your-regulars.mp4", "m_reg", [("d1", 0.2), ("d2", 3.6), ("d3", 5.6), ("d4", 8.75), ("d5", 10.8)],
        [("ding", 0.25, 0.6), ("whoosh", 3.35, 0.5), ("tick", 5.2, 0.5), ("tick", 6.4, 0.5), ("tick", 7.6, 0.5), ("kaching", 9.55, 0.35), ("impact", 10.62, 0.8)]),
}

for name, (outname, music, vo, sfx) in REELS.items():
    if ONLY and name not in ONLY:
        continue
    video = os.path.join(WORK, name, "video.mp4")
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                               capture_output=True, text=True).stdout)
    args = ["-i", video, "-i", os.path.join(MUS, music + ".mp3")]
    fc = f"[1:a]atrim=0:{dur},asetpts=PTS-STARTPTS,volume=0.7,afade=t=in:d=0.1,afade=t=out:st={dur-0.9}:d=0.9[bed];"
    i, labels = 2, ""
    for eff, t, g in sfx:
        args += ["-i", os.path.join(SFX, eff + ".wav")]; ms = int(t * 1000)
        fc += f"[{i}:a]aformat=channel_layouts=stereo,volume={g},adelay={ms}|{ms}[s{i}];"; labels += f"[s{i}]"; i += 1
    fc += f"{labels}amix=inputs={len(sfx)}:normalize=0:duration=longest,apad=whole_dur={dur},volume=1.3,asplit[sfx][sc];"
    vl = ""
    for line, t in vo:
        args += ["-i", os.path.join(VO, line + ".wav")]; ms = int(t * 1000)
        fc += f"[{i}:a]aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{i}];"; vl += f"[v{i}]"; i += 1
    fc += (f"{vl}amix=inputs={len(vo)}:normalize=0:duration=longest,apad=whole_dur={dur},highpass=f=80,"
           "acompressor=threshold=0.1:ratio=3:attack=5:release=120,volume=2.2,asplit[vo][vsc];"
           "[bed][sc]sidechaincompress=threshold=0.03:ratio=5:attack=4:release=220[b1];"
           "[b1][vsc]sidechaincompress=threshold=0.02:ratio=8:attack=10:release=300[b2];"
           "[b2][sfx][vo]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.7,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[a]")
    out = os.path.join(DIST, outname)
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-t", str(dur), "-movflags", "+faststart", out], check=True)
    print("mixed", outname, f"{dur:.2f}s")
