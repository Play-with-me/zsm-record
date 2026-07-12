import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. We need to add publicVideos
if 'const publicVideos = videos.filter(v => v.visibility === \'PUBLIC\');' not in js:
    js = js.replace(
        'const isOwner = currentUser?.id === userId;',
        'const isOwner = currentUser?.id === userId;\n      const publicVideos = videos.filter(v => v.visibility === \'PUBLIC\');'
    )

# 2. Update badge logic to use publicVideos.length
js = js.replace(
    'else if (videos.length >= 15) badgeHtml =',
    'else if (publicVideos.length >= 15) badgeHtml ='
)
js = js.replace(
    'else if (videos.length >= 5) badgeHtml =',
    'else if (publicVideos.length >= 5) badgeHtml ='
)

# 3. Update stats logic to use publicVideos
old_stats = '''          <div class="profile-stats">
            <div class="profile-stat"><div class="val">${videos.length}</div><div class="lbl">Số Record</div></div>
            <div class="profile-stat"><div class="val">${videos.reduce((a,v)=>a+(v.views||0),0)}</div><div class="lbl">Tổng lượt xem</div></div>
            ${videos.length?`<div class="profile-stat"><div class="val record-time" style="font-size:1.4rem">${fmtMs(Math.min(...videos.map(v=>v.record_ms)))}</div><div class="lbl">Thành tích tốt nhất</div></div>`:''}
          </div>'''

new_stats = '''          <div class="profile-stats">
            <div class="profile-stat"><div class="val">${publicVideos.length}</div><div class="lbl">Số Record</div></div>
            <div class="profile-stat"><div class="val">${publicVideos.reduce((a,v)=>a+(v.views||0),0)}</div><div class="lbl">Tổng lượt xem</div></div>
            ${publicVideos.length?`<div class="profile-stat"><div class="val record-time" style="font-size:1.4rem">${fmtMs(Math.min(...publicVideos.map(v=>v.record_ms)))}</div><div class="lbl">Thành tích tốt nhất</div></div>`:''}
          </div>'''

js = js.replace(old_stats, new_stats)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
