with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add router logic if not already added
old_router = '''if(parts[0]==='profile'&&parts[1]) return renderProfile(parts[1]);'''
new_router = '''if(parts[0]==='profile'&&parts[1]) return renderProfile(parts[1]);
  if(parts[0]==='insights') return renderInsights();
  if(parts[0]==='tournaments') return renderTournaments();'''

if 'renderInsights();' not in js:
    js = js.replace(old_router, new_router)

# Add renderInsights and renderTournaments implementations
features_js = '''
// --- Insights (Meta Siêu Xe) ---
async function renderInsights() {
  $('app').innerHTML = `<div class="animate-in"><div class="skeleton" style="height:400px;border-radius:12px"></div></div>`;
  try {
    const data = await apiFetch('/record-board/analytics/meta');
    
    // Sort by count
    data.sort((a,b) => b.count - a.count);
    const maxCount = data.length > 0 ? data[0].count : 1;

    $('app').innerHTML = `
      <div class="animate-in fade-in slide-in">
        <div class="section-header">
          <h2>📊 Meta Siêu Xe Thịnh Hành</h2>
          <p style="color:var(--text-secondary);margin-top:8px;">Top các loại siêu xe được dùng nhiều nhất để lập kỷ lục</p>
        </div>
        
        <div style="background:var(--card-bg); border-radius:var(--radius-lg); padding:32px; margin-bottom:32px; border:1px solid rgba(255,255,255,0.05); box-shadow:var(--shadow-lg);">
          ${data.length > 0 ? `
            <div style="display:flex; flex-direction:column; gap:16px;">
              ${data.map((item, i) => `
                <div style="display:flex; align-items:center; gap:16px;">
                  <div style="width:30px; font-weight:bold; color:var(--text-secondary); text-align:right;">#${i+1}</div>
                  <div style="width:120px; font-weight:bold; color:var(--neon-cyan); text-shadow:0 0 5px rgba(0,255,255,0.3); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${esc(item.car)}">${esc(item.car)}</div>
                  <div style="flex:1; height:24px; background:rgba(255,255,255,0.05); border-radius:12px; overflow:hidden; display:flex; align-items:center;">
                    <div style="height:100%; width:${(item.count / maxCount) * 100}%; background:linear-gradient(90deg, var(--neon-blue), var(--neon-cyan)); border-radius:12px; transition:width 1s ease-in-out;"></div>
                  </div>
                  <div style="width:80px; text-align:right; font-size:0.9rem; color:var(--text-secondary);">${item.count} Lượt</div>
                </div>
              `).join('')}
            </div>
          ` : '<div class="empty">Chưa có dữ liệu.</div>'}
        </div>
      </div>
    `;
  } catch(e) {
    $('app').innerHTML = `<div class="empty">Lỗi tải dữ liệu meta: ${e.message}</div>`;
  }
}

// --- Tournaments (Giải Đấu) ---
async function renderTournaments() {
  $('app').innerHTML = `<div class="animate-in"><div class="skeleton" style="height:200px;border-radius:12px"></div></div>`;
  try {
    const t = await apiFetch('/record-board/tournaments/active');
    
    if (t) {
      $('app').innerHTML = `
        <div class="animate-in fade-in slide-in">
          <div class="section-header" style="text-align:center;">
            <h2 style="font-size:2.5rem; color:var(--neon-pink); text-shadow:var(--neon-glow-pink); margin-bottom:16px;">🏆 GIẢI ĐẤU ĐANG DIỄN RA 🏆</h2>
          </div>
          
          <div style="background:linear-gradient(135deg, rgba(255,107,158,0.1), rgba(162,107,255,0.1)); border-radius:var(--radius-lg); padding:40px; margin-bottom:32px; border:1px solid var(--neon-pink); box-shadow:0 0 30px rgba(255,107,158,0.2); text-align:center; position:relative; overflow:hidden;">
            <div style="position:absolute; top:-50px; left:-50px; width:150px; height:150px; background:var(--neon-pink); filter:blur(100px); opacity:0.5;"></div>
            <div style="position:absolute; bottom:-50px; right:-50px; width:150px; height:150px; background:var(--neon-blue); filter:blur(100px); opacity:0.5;"></div>
            
            <h3 style="font-size:2rem; margin-bottom:16px; position:relative; z-index:1;">${esc(t.name)}</h3>
            <p style="font-size:1.2rem; color:var(--text-secondary); margin-bottom:24px; position:relative; z-index:1;">${esc(t.description)}</p>
            
            <div style="display:inline-block; background:rgba(0,0,0,0.5); padding:16px 32px; border-radius:30px; font-weight:bold; font-size:1.1rem; border:1px solid rgba(255,255,255,0.1); position:relative; z-index:1; margin-bottom:32px;">
              ⏳ Kết thúc vào: <span style="color:var(--neon-cyan);">${dateStr(t.end_time)}</span>
            </div>
            
            <div>
              <button class="btn btn-primary btn-lg" onclick="window.location.hash='#/board?map=${t.map_id}'" style="box-shadow:var(--neon-glow-pink); font-size:1.2rem; padding:12px 32px; position:relative; z-index:1;">
                Xem Bảng Xếp Hạng Giải
              </button>
            </div>
          </div>
        </div>
      `;
    } else {
      $('app').innerHTML = `
        <div class="animate-in fade-in slide-in">
          <div class="section-header">
            <h2>🏆 Giải Đấu</h2>
          </div>
          <div class="empty">
            <div style="font-size:4rem; margin-bottom:16px;">😴</div>
            Hiện tại không có giải đấu nào đang diễn ra. <br>Hãy quay lại sau nhé!
          </div>
        </div>
      `;
    }
  } catch(e) {
    $('app').innerHTML = `<div class="empty">Hiện tại không có giải đấu nào đang diễn ra.</div>`;
  }
}
'''

if 'async function renderInsights' not in js:
    js = js.replace('// ─── INIT ─────────────────────────────────────────────', features_js + '\n// ─── INIT ─────────────────────────────────────────────')

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
