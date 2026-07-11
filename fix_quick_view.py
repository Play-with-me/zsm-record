import re

with open('temp.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Modify line 641 to add onclick
content = content.replace(
    'class="card card-hover" style="display:flex;align-items:center;gap:12px;padding:10px 14px">',
    'class="card card-hover" style="display:flex;align-items:center;gap:12px;padding:10px 14px" onclick="event.preventDefault(); showQuickView(\'${r.id}\')">'
)

# Append showQuickView to the end
quick_view_js = """

window.showQuickView = async function(id) {
    try {
      const v = await apiFetch(`/videos/${id}`);
      $('quick-view-body').innerHTML = `
        <div style="display:flex; flex-direction:column; gap:16px;">
          <h2 style="color:var(--neon-cyan); margin:0;">${esc(v.map?v.map.name:'Unknown')}</h2>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; background:var(--bg); padding:16px; border-radius:8px;">
            <div>
              <div style="font-size:0.8rem; color:var(--text-dim)">Người chơi</div>
              <div style="font-weight:bold">${esc(v.user?v.user.username:'Unknown')}</div>
            </div>
            <div>
              <div style="font-size:0.8rem; color:var(--text-dim)">Thời gian</div>
              <div style="font-weight:bold; color:var(--neon-pink); font-size:1.2rem">${fmtMs(v.record_ms)}</div>
            </div>
            <div>
              <div style="font-size:0.8rem; color:var(--text-dim)">Xe</div>
              <div>${esc(v.car?v.car.name:'-')}</div>
            </div>
            <div>
              <div style="font-size:0.8rem; color:var(--text-dim)">Pet</div>
              <div>${esc(v.pet?v.pet.name:'-')}</div>
            </div>
          </div>
          <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:8px;">
            <a href="#/video/${v.id}" class="btn btn-outline btn-sm" onclick="closeQuickView()">Chi tiết</a>
          </div>
        </div>
      `;
      $('quick-view-modal').classList.add('active');
    } catch(e) {
      toast('Lỗi tải thông tin: ' + e.message, 'error');
    }
}

window.closeQuickView = function() {
    $('quick-view-modal').classList.remove('active');
}
"""

if 'showQuickView =' not in content:
    content += quick_view_js

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated temp.js")
