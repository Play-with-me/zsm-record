import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update renderBoard
old_render_board = '''    $('app').innerHTML=`<div class="animate-in" style="display:flex;flex-direction:column;gap:20px;">
      <div>
        <h1 style="font-size:1.9rem;font-weight:900">&#127942; Bảng Xếp Hạng</h1>
        <p style="color:var(--text-muted);font-size:0.85rem;margin-top:4px">Xếp hạng kỷ lục theo Bản đồ, Siêu xe và Pet.</p>
      </div>
      <div class="skeleton" style="height:130px;border-radius:var(--radius-lg)"></div>
      <div class="card" style="overflow:hidden"><table class="data-table"><thead><tr>'''

new_render_board = '''    $('app').innerHTML=`<div class="animate-in" style="display:flex;flex-direction:column;gap:20px;">
      <div>
        <h1 style="font-size:1.9rem;font-weight:900">&#127942; Bảng Xếp Hạng</h1>
        <p style="color:var(--text-muted);font-size:0.85rem;margin-top:4px">Xếp hạng kỷ lục theo Bản đồ, Siêu xe và Pet.</p>
      </div>
      <div class="skeleton" style="height:130px;border-radius:var(--radius-lg)"></div>
      <div id="podium-container" class="podium-container" style="display:none"></div>
      <div class="card" style="overflow:hidden"><table class="data-table"><thead><tr>'''

js = js.replace(old_render_board, new_render_board)

# 2. Update loadBoard
loadBoard_pattern = r'async function loadBoard\(\) \{.*?\}\n  \}\n  \n  // ── VIDEO DETAIL ──'
# wait, loadBoard definition might be different. Let's just find the start and end of loadBoard.
def load_board_replacer(match):
    return '''async function loadBoard() {
    const body=$('board-body'); if(!body) return;
    const podium = $('podium-container');
    body.innerHTML=skRows(5);
    if(podium) podium.style.display='none';
    const params=new URLSearchParams();
    const m=$('cb-bmap')?.dataset.value, c=$('cb-bcar')?.dataset.value, p=$('cb-bpet')?.dataset.value;
    if(m) params.append('map_id',m); if(c) params.append('car_id',c); if(p) params.append('pet_id',p);
    try {
      const board=await cachedApiFetch(`/record-board?${params}`, 15000);
      if(!board.length){ body.innerHTML='<tr><td colspan="6"><div class="empty">Chưa có dữ liệu cho bộ lọc này.</div></td></tr>'; return; }
      
      let top1Ms = board[0].record_ms;
      let top3 = board.slice(0, 3);
      let rest = board.slice(3);
      
      if (podium && top3.length > 0) {
          podium.style.display = 'flex';
          let spots = [];
          const ordered = [top3[1], top3[0], top3[2]];
          ordered.forEach((e) => {
              if(!e) return;
              let r = e.rank;
              let avatarHtml = e.player.avatar 
                  ? `<img src="${esc(optimizedImage(e.player.avatar, 120))}" class="podium-avatar" />`
                  : `<div class="podium-avatar">${esc(e.player.username[0].toUpperCase())}</div>`;
                  
              spots.push(`
                  <div class="podium-spot rank-${r}" style="${r===1?'order:2':(r===2?'order:1':'order:3')}">
                      ${e.player.avatar ? `<a href="#/profile/${e.player.id}" title="Xem Profile">${avatarHtml}</a>` : avatarHtml}
                      <a href="#/profile/${e.player.id}" class="podium-name" style="text-decoration:none;color:var(--text);">${esc(e.player.username)}</a>
                      <a href="#/video/${e.video_id}" class="podium-time" style="text-decoration:none;">${fmtMs(e.record_ms)}</a>
                      <div class="podium-rank">${r}</div>
                  </div>
              `);
          });
          podium.innerHTML = spots.join('');
      }
      
      if (rest.length > 0) {
          body.innerHTML=rest.map(e=>{
            const canEdit = currentUser && (currentUser.id === e.player.id || currentUser.role === 'ADMIN');
            let delta = e.record_ms - top1Ms;
            let deltaStr = delta > 0 ? `<span class="time-delta">+${(delta/1000).toFixed(2)}s</span>` : '';
            return `<tr>
            <td style="text-align:center"><span style="color:var(--text-dim);font-family:monospace;font-size:0.85rem">${e.rank}</span></td>
            <td><a href="#/profile/${e.player.id}" style="display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--text);">${e.player.avatar ? 
            `<img src="${esc(optimizedImage(e.player.avatar, 40))}" class="avatar avatar-sm" style="object-fit:cover" />` : `<span 
            class="avatar avatar-sm">${esc(e.player.username[0].toUpperCase())}</span>`}<span 
            style="font-weight:600">${esc(e.player.username)}</span></a></td>
            <td><span class="badge badge-blue">${esc(e.car.name)}</span></td>
            <td>${e.pet?.name&&e.pet.name!=='None'?`<span class="badge badge-purple">${esc(e.pet.name)}</span>`:'<span style="color:var(--text-dim)">—</span>'}</td>
            <td><span class="record-time" style="font-size:1.05rem">${fmtMs(e.record_ms)}</span>${deltaStr}</td>
            <td style="text-align:right; white-space:nowrap;">
              ${canEdit ? `<button class="btn-icon" style="color:var(--orange)" onclick="editRecord('${e.video_id}')" title="Sửa">&#9998;</button>` : ''}
              <a href="#/video/${e.video_id}" class="btn-icon" title="Xem chi tiết">&#128065;</a>
            </td>
          </tr>`}).join('');
      } else {
          body.innerHTML='<tr><td colspan="6"><div class="empty">Chỉ có thành tích Top 3.</div></td></tr>';
      }
    } catch (e) { 
        body.innerHTML=`<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--red)">Tải bảng xếp hạng thất bại. ${e.message}</td></tr>`; 
    }
}

// ── VIDEO DETAIL ──'''

js = re.sub(r'async function loadBoard\(\) \{.*?\}\n  \}\n  \n  // ── VIDEO DETAIL ──', load_board_replacer, js, flags=re.DOTALL)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
