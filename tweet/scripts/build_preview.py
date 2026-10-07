"""Render only tweet text, quoted tweet text, and attached media."""
from pathlib import Path
from html import escape
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
posts=json.loads((ROOT/"thread.json").read_text())

def linked(text):
    out=[]
    last=0
    for match in re.finditer(r"https?://[^\s]+|@[A-Za-z0-9_]+",text):
        out.append(escape(text[last:match.start()]))
        label=match.group()
        url=label if label.startswith("http") else "https://x.com/"+label[1:]
        out.append(f'<a href="{escape(url,quote=True)}" target="_blank" rel="noopener noreferrer">{escape(label)}</a>')
        last=match.end()
    out.append(escape(text[last:]))
    return "".join(out)

def asset(path):
    digest=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()[:12]
    return escape(f"{path}?v={digest}",quote=True)

articles=[]
for post in posts:
    media=post.get("media") or []
    if isinstance(media,str):media=[media]
    attachments=[]
    for path in media:
        alt=escape(post.get("alt",""),quote=True)
        if path.endswith(".mp4"):
            poster=f' poster="{asset(post["poster"])}"' if post.get("poster") else ""
            motion=' muted loop data-animation="true"' if post.get("animation") else ""
            attachments.append(f'<video controls playsinline preload="metadata"{motion}{poster} aria-label="{alt}"><source src="{asset(path)}" type="video/mp4"></video>')
        else:
            attachments.append(f'<a class="image" href="{asset(path)}" target="_blank" rel="noopener noreferrer"><img src="{asset(path)}" alt="{alt}" loading="lazy"></a>')
    quote=""
    if post.get("quote_url"):
        quote_text="Today, we’re introducing [schema]: a harness reaching 99% RHAE with Opus 4.8 + Fable 5 and 95.35% with GPT-5.6 Sol on ARC-AGI-3 Public set.\n\n[schema] makes an LLM think like a physicist. 🧵"
        quote=f'<blockquote><a href="{escape(post["quote_url"],quote=True)}" target="_blank" rel="noopener noreferrer">{escape(quote_text)}</a></blockquote>'
    articles.append(f'<article id="post-{post["number"]}"><p class="tweet">{linked(post["text"])}</p>{quote}<div class="media">{"".join(attachments)}</div></article>')

html='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Schema</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#fff;color:#18212a;font-family:Arial,Helvetica,sans-serif}main{max-width:840px;margin:0 auto;padding:8px 24px 48px}article{padding:40px 0;border-bottom:1px solid #e8ecef;scroll-margin-top:24px}article:last-child{border:0}.tweet{margin:0;font-size:20px;line-height:1.6;white-space:pre-wrap;overflow-wrap:anywhere}a{color:#176fbc;text-decoration:none}a:hover{text-decoration:underline}a:focus-visible{outline:2px solid #176fbc;outline-offset:4px}blockquote{margin:24px 0 0;padding:18px 22px;border:1px solid #dfe5ea;border-radius:12px;font-size:16px;line-height:1.6;white-space:pre-wrap}blockquote a{color:inherit}.media:empty{display:none}.media{display:grid;gap:18px;margin-top:24px}.media img,.media video{display:block;width:100%;height:auto;border-radius:8px}.media video{background:#fff}.image{display:block}@media(max-width:540px){main{padding:0 18px 30px}article{padding:30px 0}.tweet{font-size:18px;line-height:1.55}blockquote{padding:14px 16px;font-size:15px}.media{margin-top:20px}}
#post-8 .media{width:30%;margin-inline:auto}
</style></head><body><main>'''+"\n".join(articles)+'''</main><script>
if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
  const observer=new IntersectionObserver(entries=>{
    for(const entry of entries){
      const video=entry.target;
      if(entry.isIntersecting){video.currentTime=0;video.play().catch(()=>{})}
      else video.pause();
    }
  },{threshold:.4});
  document.querySelectorAll('video[data-animation]').forEach(video=>observer.observe(video));
}
</script></body></html>'''
(ROOT/"index.html").write_text(html)
print(f"Rendered {len(posts)} tweets with no visible editorial or preview UI.")
