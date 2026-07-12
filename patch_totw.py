import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Inject HTML into renderHome
old_renderHome_html = '''        </div>
      </div></section>
      <section>
        <div class="section-header">'''

new_renderHome_html = '''        </div>
      </div></section>
      <section id="totw-section" style="display:none; margin-bottom: 36px;">
        <div class="section-header">
          <h2 style="color:var(--neon-purple); text-shadow:var(--neon-glow-purple);">🏆 Bản Đồ Của Tuần</h2>
        </div>
        <div class="totw-banner" style="background:var(--bg-card); border:1px solid var(--neon-purple); border-radius:var(--radius-lg); padding:20px; display:flex; align-items:center; gap:20px; box-shadow:0 0 20px rgba(188, 19, 254, 0.2);">
            <div id="totw-image" style="width:120px; height:80px; border-radius:12px; background:#111; overflow:hidden; flex-shrink:0;"></div>
            <div style="flex:1">
                <h3 id="totw-map-name" style="font-size:1.4rem; font-weight:800; margin-bottom:4px; color:var(--text);">...</h3>
                <p style="color:var(--text-muted); font-size:0.85rem; margin-bottom:10px;">Thách thức mọi tay đua phá vỡ kỷ lục bản đồ này!</p>
                <div id="totw-record" style="font-size:0.9rem;"></div>
            </div>
            <div>
                <a href="#/board" class="btn btn-purple btn-sm">Xem ngay</a>
            </div>
        </div>
      </section>
      <section>
        <div class="section-header">'''

js = js.replace(old_renderHome_html, new_renderHome_html)

# 2. Inject JS logic into renderHome
# find where maps are loaded
old_logic = '''      $('hero-stats').innerHTML=`
        <div class="hero-stat"><div class="num">${maps.length}</div><div class="label">Bản đồ</div></div>'''

new_logic = '''      // Track of the Week
      if (maps && maps.length > 0) {
          const weekNumber = Math.ceil(Math.floor((new Date() - new Date(new Date().getFullYear(), 0, 1)) / (24 * 60 * 60 * 1000)) / 7);
          const totwMap = maps[weekNumber % maps.length];
          const totwSection = $('totw-section');
          if (totwMap && totwSection) {
              totwSection.style.display = 'block';
              $('totw-map-name').innerText = totwMap.name;
              if (totwMap.image) $('totw-image').innerHTML = `<img src="${esc(optimizedImage(totwMap.image, 300))}" style="width:100%;height:100%;object-fit:cover;" />`;
              
              const bestRecord = allVideos.filter(v => v.map_id === totwMap.id).sort((a,b) => a.record_ms - b.record_ms)[0];
              if (bestRecord) {
                  $('totw-record').innerHTML = `Đang giữ Top 1: <strong style="color:var(--neon-cyan)">${fmtMs(bestRecord.record_ms)}</strong> - <strong>${esc(bestRecord.user?.username || 'Unknown')}</strong>`;
              } else {
                  $('totw-record').innerHTML = `<span style="color:var(--text-muted)">Chưa có kỷ lục nào. Hãy là người đầu tiên!</span>`;
              }
          }
      }

      $('hero-stats').innerHTML=`
        <div class="hero-stat"><div class="num">${maps.length}</div><div class="label">Bản đồ</div></div>'''

js = js.replace(old_logic, new_logic)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
