"""Animate the causal order inside Figure 2, including stopping and revision."""
from pathlib import Path
import json
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "03-method-animation-poster.png"
WORK = ROOT.parent.parent / "schema-twitter/.build/method-v2"
WORK.mkdir(parents=True, exist_ok=True)
im = Image.open(SOURCE).convert("RGB")
W, H = im.size
pixels = np.asarray(im).astype(np.float32)
reveal = np.full((H, W), 8.1, dtype=np.float32)
stages = []

def rect(coords):
    x0, y0, x1, y1 = coords
    return tuple(round(v*s) for v,s in zip(coords,[W/2048,H/1195,W/2048,H/1195]))

def region(name, coords, start, wipe=None, duration=.16):
    x0,y0,x1,y1=rect(coords)
    if wipe == "right":
        reveal[y0:y1,x0:x1]=start+np.linspace(0,duration,x1-x0)[None,:]
    elif wipe == "left":
        reveal[y0:y1,x0:x1]=start+np.linspace(duration,0,x1-x0)[None,:]
    elif wipe == "down":
        reveal[y0:y1,x0:x1]=start+np.linspace(0,duration,y1-y0)[:,None]
    else:
        reveal[y0:y1,x0:x1]=start
    stages.append(dict(element=name,start=start,region=coords,transition=wipe or "fade"))

# Outer panels establish the layout; their contents are revealed independently.
region("agent and persistent program/history",(899,284,1167,688),0)
region("workspace legend",(650,1106,1420,1195),0)
region("hypothesize program",(0,0,883,508),.10)
region("proposed program label",(899,74,1157,125),.66)
region("proposed program arrow",(884,125,1167,179),.68,"right")

region("certification panel and heading",(1167,0,2048,508),.92)
region("defer certification evidence",(1190,146,2030,489),2.36)
region("history H",(1193,222,1250,293),1.04)
region("history state t=126",(1254,150,1471,401),1.05)
region("first history transition",(1472,233,1517,281),1.36,"right",.10)
region("history state t=127",(1518,150,1739,401),1.51)
region("further history transitions",(1740,233,1808,281),1.82,"right",.10)
region("history state t=130",(1809,150,2012,401),1.96)
region("history bracket",(1248,402,2018,441),2.24)
region("130/130 transitions certified",(1282,442,2001,488),2.36)
region("certification counterexample return",(884,185,1167,280),2.56,"left",.10)
region("certified program arrow",(1590,509,1640,579),2.75,"down",.10)
region("certified program label",(1637,512,1835,573),2.83)

region("planning panel",(1167,580,2048,1102),3.02)
region("defer plan contents",(1185,719,2020,1080),3.59)
region("planning tools",(1603,724,2008,918),3.16)
region("planned route",(1190,724,1572,1075),3.40)
region("search produces plan arrow",(1768,919,1840,1009),3.61,"down",.10)
region("resulting plan",(1720,1015,1915,1080),3.73)
region("commit label",(898,882,1156,939),3.93)
region("commit arrow",(884,936,1166,986),3.95,"left",.12)

region("execution panel and title",(0,580,883,1102),4.18)
region("defer execution sequence",(36,652,815,1070),6.56)
region("plan pi",(185,727,241,793),4.25)
region("first checked action",(241,730,309,797),4.48)
region("continue after a match",(112,656,399,703),4.61)
region("second checked action",(321,730,386,797),4.88)
region("matched actions bracket",(240,702,387,730),4.61)
region("next predicted observation",(44,805,385,1062),5.22)
region("next action",(398,706,464,797),5.53)
region("actual observed outcome",(441,805,783,1062),5.88)
region("prediction differs from observation",(381,872,441,963),6.12)
region("mismatch stops execution",(403,656,802,703),6.16)
region("stopped actions bracket",(397,702,618,730),6.16)
region("discard first remaining action",(473,706,536,797),6.34)
region("discard second remaining action",(548,706,615,797),6.43)
region("discarded label",(622,716,809,799),6.49)

# Reveal the original feedback arrow from the observed counterexample upward.
# Restrict the mask to its magenta pixels so neighboring borders never pop in.
xx,yy=np.meshgrid(np.arange(W)*2048/W,np.arange(H)*1195/H)
r,g,b=pixels[:,:,0],pixels[:,:,1],pixels[:,:,2]
magenta=(r>g+8)&(b>g+8)&(r>b+12)
path_area=(xx>=774)&(xx<847)&(yy>=506)&(yy<977)
path=path_area&magenta
distance=.18*np.clip((xx-774)/48,0,1)+.49*np.clip((950-yy)/415,0,1)
reveal[path]=(6.82+distance)[path]
label=(xx>=635)&(xx<802)&(yy>=512)&(yy<577)&magenta
reveal[label]=7.42
stages.append(dict(element="counterexample returns along revise-P arrow",start=6.82,end=7.70,transition="follow path from observation to program"))

# The green patch appears as the consequence of feedback, not before it.
patch=rect((382,275,855,434))
x0,y0,x1,y1=patch
program_bg=np.broadcast_to(pixels[round(274*H/1195),x0:x1],(y1-y0,x1-x0,3))
reveal[y0:y1,x0:x1]=7.75
stages.append(dict(element="revise program: green code patch",start=7.75,end=8.04))

def ease(t, start, duration=.22):
    value=np.clip((t-start)/duration,0,1)
    return value*value*(3-2*value)

font_path=ROOT.parent/"static/fonts/castoro.ttf"
font=ImageFont.truetype(str(font_path),round(25*W/2048))
fps=30
duration=10.5
cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-an","-c:v","libx264","-preset","fast","-crf","15","-pix_fmt","yuv420p","-threads","2","-movflags","+faststart",str(ASSETS/"03-method-animation.mp4")]
snapshots={round(t*fps):t for t in [1.25,1.75,2.2,2.65,4.65,5.05,5.4,5.72,6.03,6.65,7.15,7.65,8.15,9.5]}
with subprocess.Popen(cmd,stdin=subprocess.PIPE) as proc:
    delta=255-pixels
    for i in range(round(duration*fps)):
        t=i/fps
        alpha=ease(t,reveal)
        frame=255-delta*alpha[:,:,None]
        # Keep the unrevised code block dark rather than opening a white hole.
        frame[y0:y1,x0:x1]=255+(program_bg-255)*ease(t,.10)+(pixels[y0:y1,x0:x1]-program_bg)*ease(t,7.75,.29)
        canvas=Image.fromarray(np.clip(np.rint(frame),0,255).astype(np.uint8))
        if 6.26<=t<9.1:
            a=float(ease(t,6.26,.18))*(1-float(ease(t,8.65,.4)))
            overlay=Image.new("RGBA",canvas.size,(0,0,0,0))
            draw=ImageDraw.Draw(overlay)
            color=(177,47,130,round(255*a))
            draw.rectangle(rect((442,846,780,1056)),outline=color,width=3)
            x,y=round(611*W/2048),round(1066*H/1195)
            draw.text((x,y),"counterexample",font=font,fill=color,anchor="mt")
            canvas=Image.alpha_composite(canvas.convert("RGBA"),overlay).convert("RGB")
        proc.stdin.write(canvas.tobytes())
        if i in snapshots:
            canvas.save(WORK/f"at-{snapshots[i]:04.2f}.png")
    proc.stdin.close()
    proc.wait()
    assert proc.returncode==0

timeline={"version":2,"source":"paper_arxiv/figures/schema_method.pdf","duration_seconds":duration,"default_fade_seconds":.22,"stages":stages,"final_hold_seconds":2.3,"notes":"History states and execution actions appear sequentially. Prediction precedes observation; mismatch stops and discards remaining actions. The counterexample follows the revision arrow, then reveals the program patch. Temporary counterexample annotation fades before the final unchanged figure."}
(ASSETS/"03-method-animation-timeline.json").write_text(json.dumps(timeline,ensure_ascii=False,indent=2)+"\n")
print(f"Exported ordered Figure 2 animation: {duration}s; {len(stages)} timed elements.")
