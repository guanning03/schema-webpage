"""Create a portable, dependency-free HTML thread preview from posts.json."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "thread.json"
if not source.exists():
    source = ROOT / "posts.json"
posts = json.loads(source.read_text())
for p in posts:
    if not isinstance(p.get("media"), list):
        p["media"] = [p["media"]] if p.get("media") else []
    p.setdefault("media_descriptions", {m: p.get("alt", "") for m in p["media"]})
    p.setdefault("note", p["title"])

def linked(text):
    pattern = r"https?://[^\s]+|@[A-Za-z0-9_]+"
    out, last = [], 0
    for m in re.finditer(pattern, text):
        out.append(escape(text[last:m.start()]))
        label=m.group()
        url=label if label.startswith("http") else "https://x.com/"+label[1:]
        out.append(f'<a href="{escape(url,quote=True)}" target="_blank" rel="noopener noreferrer">{escape(label)}</a>')
        last=m.end()
    out.append(escape(text[last:]))
    return "".join(out)

articles=[]
for p in posts:
    n=p["number"]
    media=[]
    for file in p["media"]:
        description=escape(p["media_descriptions"][file],quote=True)
        name=Path(file).name
        if file.endswith(".mp4"):
            poster=escape(p.get("poster", "assets/04-theory-revision-poster.png"),quote=True)
            caption=escape(p.get("media_caption",p["title"]))
            animate=' muted loop data-animate="true"' if p.get("animation") else ''
            replay='<button class="replay-animation" type="button">重播动画</button> · ' if p.get("animation") else ''
            media.append(f'''<figure class="video"><video controls playsinline preload="metadata"{animate} poster="{poster}" aria-label="{description}"><source src="{file}" type="video/mp4"></video><figcaption>{replay}<a href="{file}" download>下载视频</a> · {caption}</figcaption></figure>''')
        else:
            media.append(f'''<figure><button class="image-zoom" type="button" data-src="{file}" data-alt="{description}" aria-label="放大图片"><img src="{file}" alt="{description}" loading="lazy"></button><figcaption><a href="{file}" download>下载图片</a> · 点击图片放大</figcaption></figure>''')
    quoted=""
    if n==1:
        quoted='''<a class="quote" href="https://x.com/HavenFeng/status/2077770348876247502" target="_blank" rel="noopener noreferrer"><strong>Haven Feng <span>@HavenFeng · Jul 16, 2026</span></strong><p>Today, we’re introducing [schema]: a harness reaching 99% RHAE with Opus 4.8 + Fable 5 and 95.35% with GPT-5.6 Sol on ARC-AGI-3 Public set.</p><p>[schema] makes an LLM think like a physicist. 🧵</p><span class="quote-link">引用首次发布的 tweet · 原帖含 demo ↗</span></a>'''
    articles.append(f'''<article class="post" id="post-{n}" aria-labelledby="label-{n}"><div class="rail"><span class="avatar" aria-hidden="true">[s]</span></div><div class="post-main"><header class="post-header"><div><strong id="label-{n}">Schema</strong><span class="post-position">{n} / {len(posts)}</span></div><button class="copy" data-post="{n}" type="button">复制正文</button></header><p class="tweet" id="text-{n}">{linked(p['text'])}</p>{quoted}<div class="media">{''.join(media)}</div><footer class="post-footer"><span>{p['weighted_characters']} / 280 字符</span><details><summary>制作备注</summary><p>{escape(p['note'])}</p></details></footer></div></article>''')

html='''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Schema · Twitter Thread Preview</title>
<style>
:root{font-family:Arial,"PingFang SC",sans-serif;color:#17202a;background:#fff;font-synthesis:none;line-height:1.5}*{box-sizing:border-box}body{margin:0}a{color:#176fbc;text-decoration:none}a:hover{text-decoration:underline}button{font:inherit;cursor:pointer}button:focus-visible,a:focus-visible,summary:focus-visible{outline:3px solid #297ac0;outline-offset:4px}main{max-width:780px;margin:auto;border-left:1px solid #e9edf0;border-right:1px solid #e9edf0}.intro{padding:36px 30px 24px;border-bottom:1px solid #e9edf0}.intro h1{font-size:28px;letter-spacing:-.7px;margin:0 0 6px}.intro p{margin:4px 0;color:#607080;font-size:14px}.toolbar{display:flex;align-items:center;gap:18px;flex-wrap:wrap;margin-top:20px;font-size:14px}.toolbar button{border:1px solid #cbd3da;background:white;border-radius:20px;padding:7px 14px;color:#233545}.jump{display:flex;gap:8px;margin-top:22px}.jump a{display:grid;place-items:center;width:32px;height:32px;border:1px solid #e2e8ee;border-radius:50%;color:#526575;font-size:13px}.jump a:hover{background:#f1f5f8;text-decoration:none}.post{display:grid;grid-template-columns:44px minmax(0,1fr);gap:12px;padding:24px 24px 0;scroll-margin-top:16px}.rail{position:relative;display:flex;justify-content:center}.rail:after{content:"";position:absolute;top:51px;bottom:-17px;width:2px;background:#e1e7ec}.post:last-child .rail:after{display:none}.avatar{height:42px;width:42px;display:grid;place-items:center;background:#f3f0ed;border-radius:50%;font-family:Georgia,serif;font-size:23px;z-index:1;letter-spacing:-2px}.post-main{min-width:0;padding-bottom:27px}.post-header{display:flex;justify-content:space-between;align-items:center;gap:12px;height:36px;margin-bottom:8px}.post-header strong{font-size:16px}.post-position{color:#6e7c89;font-size:14px;margin-left:10px}.copy{padding:4px 10px;border:1px solid #dce3e9;background:white;color:#556879;border-radius:16px;font-size:12px;white-space:nowrap}.copy:hover{background:#f4f7f9}.tweet{white-space:pre-wrap;overflow-wrap:anywhere;font-size:19px;line-height:1.52;margin:0 0 17px}.quote{display:block;color:inherit;border:1px solid #dfe5ea;border-radius:14px;padding:16px;margin:0 0 16px;font-size:14px}.quote:hover{text-decoration:none;background:#fafbfc}.quote strong span{font-weight:400;color:#6e7c89;font-size:12px;display:inline-block}.quote p{margin:9px 0;line-height:1.5}.quote-link{font-size:12px;color:#176fbc}.media{display:grid;gap:14px}.media figure{margin:0;min-width:0}.image-zoom{display:block;border:1px solid #e4e8ec;border-radius:12px;background:white;overflow:hidden;padding:0;width:100%;line-height:0}.image-zoom img{width:100%;height:auto;display:block}.media video{display:block;width:100%;background:#202225;border-radius:12px;border:1px solid #e4e8ec}.media figcaption{font-size:11px;color:#85909a;margin:5px 2px 0}.media figcaption a{color:#687d8f}.replay-animation{background:none;border:none;color:#176fbc;font-size:11px;padding:0}.post-footer{display:flex;justify-content:space-between;align-items:start;gap:15px;font-size:11px;color:#89959f;margin-top:16px}.post-footer details{text-align:right;max-width:75%}.post-footer summary{cursor:pointer;color:#6e7c89}.post-footer details p{text-align:left;color:#5a6977;line-height:1.7;margin-top:10px;font-size:12px}.end{padding:20px 30px 34px;color:#80909d;font-size:12px;border-top:1px solid #eef1f4}.end a{color:#60788c}body.mobile main{max-width:430px}body.mobile .post{padding-left:12px;padding-right:12px;gap:8px;grid-template-columns:32px minmax(0,1fr)}body.mobile .avatar{width:31px;height:31px;font-size:18px}body.mobile .tweet{font-size:16px}body.mobile .intro{padding:24px 20px}body.mobile .rail:after{top:40px}dialog{border:none;padding:0;max-width:95vw;max-height:95vh;overflow:visible;background:transparent}dialog::backdrop{background:rgba(15,20,25,.88)}dialog img{display:block;max-width:95vw;max-height:90vh;object-fit:contain;background:white;border-radius:5px}dialog button{position:absolute;right:8px;top:8px;width:38px;height:38px;border:1px solid #ccd3da;border-radius:50%;background:white;font-size:25px;color:#182431}#toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#17202a;color:white;padding:9px 18px;border-radius:22px;font-size:13px;opacity:0;pointer-events:none;transition:opacity .15s}#toast.visible{opacity:1}@media(max-width:540px){.intro{padding:24px 18px}.intro h1{font-size:25px}.post{padding-left:12px;padding-right:12px;gap:8px;grid-template-columns:32px minmax(0,1fr)}.avatar{height:31px;width:31px;font-size:18px}.rail:after{top:40px}.tweet{font-size:16px}.quote{padding:12px;font-size:13px}.post-header strong{font-size:15px}.post-footer{gap:10px}.copy{font-size:11px}.toolbar{gap:14px}}
</style></head><body><main><section class="intro"><h1>Schema · Release thread</h1><p>TOTAL_POSTS 条帖文 · 预览稿 · 尚未发布</p><p>首帖引用 July 的首次发布；图片可放大，视频可直接播放。</p><div class="toolbar"><button type="button" id="copy-all">复制全部正文</button><button type="button" id="mobile-toggle" aria-pressed="false">手机宽度</button><a href="thread.md">Markdown</a><a href="thread.json" download>帖文与素材清单</a></div><nav class="jump" aria-label="跳转到帖文">'''+''.join(f'<a href="#post-{i}" aria-label="第 {i} 条">{i}</a>' for i in range(1,len(posts)+1))+'''</nav></section><section class="thread" aria-label="Thread">'''+''.join(articles)+r'''</section><footer class="end">首帖文案的 July 15 为博客 release 日期；引用 tweet 发表于 July 16。<br><a href="thread.md">完整制作说明与数据来源</a> · <a href="alt-text.md">媒体描述 / Alt text</a></footer></main><dialog id="lightbox" aria-label="图片预览"><button type="button" aria-label="关闭图片">×</button><img alt=""></dialog><div id="toast" role="status" aria-live="polite"></div><script>
const posts=POST_DATA;
const toast=document.querySelector('#toast');let timer;
function showToast(s){toast.textContent=s;toast.classList.add('visible');clearTimeout(timer);timer=setTimeout(()=>toast.classList.remove('visible'),2200)}
async function copyText(s){try{await navigator.clipboard.writeText(s);showToast('已复制')}catch(e){const box=document.createElement('textarea');box.value=s;box.style.cssText='position:fixed;left:-9999px';document.body.appendChild(box);box.select();const ok=document.execCommand('copy');box.remove();showToast(ok?'已复制':'请选中文本后复制')}}
document.querySelectorAll('.copy').forEach(b=>b.addEventListener('click',()=>copyText(posts[Number(b.dataset.post)-1].text)));
document.querySelector('#copy-all').addEventListener('click',()=>copyText(posts.map((p,i)=>`${i+1}/TOTAL_POSTS\n\n${p.text}`).join('\n\n———\n\n')));
document.querySelector('#mobile-toggle').addEventListener('click',function(){const on=document.body.classList.toggle('mobile');this.setAttribute('aria-pressed',on);this.textContent=on?'桌面宽度':'手机宽度'});
document.querySelectorAll('.replay-animation').forEach(b=>b.addEventListener('click',()=>{const v=b.closest('figure').querySelector('video');v.currentTime=0;v.play()}));
if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches){const watcher=new IntersectionObserver(entries=>{for(const entry of entries){const v=entry.target;if(entry.isIntersecting){v.currentTime=0;v.play().catch(()=>{})}else{v.pause()}}},{threshold:.45});document.querySelectorAll('video[data-animate]').forEach(v=>watcher.observe(v))}
const dialog=document.querySelector('#lightbox');document.querySelectorAll('.image-zoom').forEach(b=>b.addEventListener('click',()=>{const im=dialog.querySelector('img');im.src=b.dataset.src;im.alt=b.dataset.alt;dialog.showModal()}));dialog.querySelector('button').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});
</script></body></html>'''
html=html.replace('POST_DATA',json.dumps(posts,ensure_ascii=False).replace('</','<\\/'))
html=html.replace('TOTAL_POSTS',str(len(posts)))
(ROOT/'index.html').write_text(html)
print(f'Built {ROOT / "index.html"}: {len(posts)} posts.')
