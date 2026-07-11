
const API = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
  ? 'http://localhost:8001/api/v1' 
  : 'https://zsm-record-backend.onrender.com/api/v1';

// ─── STATE ───────────────────────────────────────────
let currentUser = null;
let searchTimeout = null;
const apiCache = new Map();
const CACHE_TTL = 60000;
const liteDevice = window.matchMedia('(max-width: 768px)').matches ||
  (navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 4) ||
  (navigator.deviceMemory && navigator.deviceMemory <= 4);
if (liteDevice) document.documentElement.classList.add('perf-lite');

// ─── UTILS ───────────────────────────────────────────
const $ = id => document.getElementById(id);
const esc = str => { if(!str) return ''; const d=document.createElement('div'); d.textContent=str; return d.innerHTML; };

function fmtMs(ms) {
  const m=Math.floor(ms/60000), s=Math.floor((ms%60000)/1000), cs=Math.floor((ms%1000)/10);
  return `${m}:${String(s).padStart(2,'0')}:${String(cs).padStart(2,'0')}`;
}
function parseRecord(str) {
  const parts = str.split(':');
  if(parts.length === 3) {
    return parseInt(parts[0])*60000 + parseInt(parts[1])*1000 + parseInt(parts[2])*10;
  }
  return 0;
}
function dateStr(d) { return new Date(d).toLocaleDateString('vi-VN'); }
function optimizedImage(url, width=900) {
  if(!url) return '';
  if(url.includes('res.cloudinary.com') && url.includes('/upload/') && !url.includes('/upload/f_auto')) {
    return url.replace('/upload/', `/upload/f_auto,q_auto,c_limit,w_${width}/`);
  }
  if(url.startsWith('/uploads/')) {
    return API.replace('/api/v1', '') + url;
  }
  return url;
}
function proofImage(v, width=900) {
  const src = v?.thumbnail || v?.map?.image || `https://placehold.co/600x338/0d0d22/fff?text=${encodeURIComponent(v?.map?.name||'Record')}`;
  return optimizedImage(src, width);
}
function cleanUrl(url) { return (url || '').trim(); }
function getToken() { return localStorage.getItem('zsm_token'); }
function setToken(t) { localStorage.setItem('zsm_token',t); }
function clearToken() { localStorage.removeItem('zsm_token'); }

// ─── API ─────────────────────────────────────────────
async function apiFetch(path, opts={}) {
  const h={'Content-Type':'application/json',...(opts.headers||{})};
  if(getToken()) h['Authorization']=`Bearer ${getToken()}`;
  const res = await fetch(`${API}${path}`,{...opts,headers:h});
  if(!res.ok) { const e=await res.json().catch(()=>({detail:'Lỗi kết nối'})); throw new Error(e.detail||'Yêu cầu thất bại'); }
  return res.json();
}
async function cachedApiFetch(path, ttl=CACHE_TTL) {
  const now = Date.now();
  const cached = apiCache.get(path);
  if(cached && now - cached.ts < ttl) return cached.data;
  const data = await apiFetch(path);
  apiCache.set(path, {ts: now, data});
  return data;
}
function clearApiCache() { apiCache.clear(); }

async function fetchUser() {
  try { if(!getToken()){currentUser=null;return;} currentUser=await apiFetch('/auth/me'); }
  catch { currentUser=null; clearToken(); }
}

// ─── TOAST ───────────────────────────────────────────
function toast(msg, type='success') {
  const c=$('toasts'), t=document.createElement('div');
  t.className=`toast toast-${type}`; t.textContent=msg; c.appendChild(t);
  setTimeout(()=>{t.style.opacity='0';setTimeout(()=>t.remove(),300)},3000);
}

// ─── NAV ─────────────────────────────────────────────
function renderNav() {
  const el=$('nav-auth');
  // Update active link
  const hash=window.location.hash.slice(1)||'/';
  document.querySelectorAll('[data-route]').forEach(l => l.classList.toggle('active', l.dataset.route===hash));
  if(currentUser) {
    el.innerHTML=`
      <a href="#/upload" class="btn btn-purple btn-sm">+ Đăng Record</a>
      <div class="user-menu" id="user-menu">
        <button class="user-trigger" onclick="toggleUserMenu()">
          ${currentUser.avatar 
            ? `<img src="${esc(optimizedImage(currentUser.avatar, 64))}" class="avatar avatar-sm" loading="eager" decoding="async" style="object-fit:cover;"/>`
            : `<span class="avatar avatar-sm">${esc(currentUser.username[0].toUpperCase())}</span>`
          }
          <span class="uname">${esc(currentUser.username)}</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
        </button>
      </div>`;
  } else {
    el.innerHTML=`
      <a href="#/login" class="btn btn-outline btn-sm">Đăng nhập</a>
      <a href="#/register" class="btn btn-primary btn-sm">Đăng ký</a>`;
  }
}

function toggleUserMenu() {
  const menu=$('user-menu'); if(!menu) return;
  const existing=menu.querySelector('.user-dropdown');
  if(existing) { existing.remove(); return; }
  const dd=document.createElement('div');
  dd.className='user-dropdown';
  dd.innerHTML=`
    <button class="dd-item" onclick="navigate('/profile/'+currentUser.id);closeMenu()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      Hồ sơ của tôi
    </button>
    ${currentUser.role==='ADMIN'?`<button class="dd-item" onclick="navigate('/admin');closeMenu()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
      Trang Quản Trị
    </button>`:''}
    <div class="dd-sep"></div>
    <button class="dd-item danger" onclick="logout()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
      Đăng xuất
    </button>`;
  menu.appendChild(dd);
}

function closeMenu() { const d=document.querySelector('.user-dropdown'); if(d) d.remove(); }
document.addEventListener('click',e=>{ if(!e.target.closest('.user-menu')) closeMenu(); });
function logout() { clearToken(); currentUser=null; renderNav(); toast('Đã đăng xuất'); navigate('/'); }
function navigate(p) { window.location.hash=p; }

// ─── COMBOBOX ─────────────────────────────────────────
// opts = [{label, value, group?}] — group is optional, used for car class grouping
function mkCombobox(id, opts, placeholder, val='') {
  const sel=opts.find(o=>o.value===val);
  // Build items with optional group headers
  let itemsHtml = '';
  let lastGroup = null;
  for (const o of opts) {
    const g = o.group || null;
    if (g && g !== lastGroup) {
      itemsHtml += `<div class="combobox-group-header">${esc(g)}</div>`;
      lastGroup = g;
    }
    itemsHtml += `<div class="combobox-item${o.value===val?' selected':''}" data-value="${o.value}" data-label="${esc(o.label.trim())}" data-group="${esc(g||'')}" onclick="pickCB('${id}','${o.value}','${esc(o.label.trim())}')" tabindex="0">
      <svg class="combobox-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M20 6L9 17l-5-5"/></svg>
      ${esc(o.label.trim())}</div>`;
  }
  return `<div class="combobox" id="cb-${id}"${val ? ` data-value="${val}"` : ''}>
    <button type="button" class="combobox-trigger${!val?' placeholder':''}"
      onclick="openCB('${id}')" id="cbt-${id}">
      <span class="selected-text ${!val?'placeholder':''}">${sel?esc(sel.label):placeholder}</span>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 10l5 5 5-5"/></svg>
    </button>
    <div class="combobox-dropdown" style="display:none" id="cbd-${id}">
      <div class="combobox-search"><input placeholder="Tìm kiếm..." oninput="filterCB('${id}',this.value)" autocomplete="off" /></div>
      <div class="combobox-list" id="cbl-${id}">
        <button type="button" class="combobox-clear" onclick="clearCB('${id}','${placeholder}')">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg> Bỏ chọn
        </button>
        ${itemsHtml}
        ${!opts.length?'<div class="combobox-empty">Không có dữ liệu</div>':''}
      </div>
    </div>
  </div>`;
}

function openCB(id) {
  document.querySelectorAll('.combobox-dropdown').forEach(d=>{if(d.id!==`cbd-${id}`)d.style.display='none';});
  const dd=$(`cbd-${id}`); const isOpen=dd.style.display!=='none';
  dd.style.display=isOpen?'none':'block';
  $(`cbt-${id}`)?.classList.toggle('open',!isOpen);
  if(!isOpen) { const inp=dd.querySelector('input'); inp?.focus(); inp&&(inp.value=''); filterCB(id,''); }
}
function filterCB(id,q) {
  const list = document.getElementById(`cbl-${id}`);
  if (!list) return;
  const items = list.querySelectorAll('.combobox-item');
  const headers = list.querySelectorAll('.combobox-group-header');
  const lq = q.toLowerCase();
  items.forEach(i => {
    i.style.display = i.dataset.label.toLowerCase().includes(lq) ? '' : 'none';
  });
  // Hide group headers if all items in that group are hidden
  headers.forEach(h => {
    let next = h.nextElementSibling;
    let hasVisible = false;
    while (next && !next.classList.contains('combobox-group-header')) {
      if (next.classList.contains('combobox-item') && next.style.display !== 'none') hasVisible = true;
      next = next.nextElementSibling;
    }
    h.style.display = hasVisible ? '' : 'none';
  });
}
function pickCB(id,val,label) {
  const cb=$(`cb-${id}`); const t=$(`cbt-${id}`);
  const txt=t.querySelector('.selected-text'); txt.textContent=label; txt.classList.remove('placeholder');
  cb.dataset.value=val;
  document.querySelectorAll(`#cbl-${id} .combobox-item`).forEach(i=>i.classList.toggle('selected',i.dataset.value===val));
  $(`cbd-${id}`).style.display='none'; t.classList.remove('open');
}
function clearCB(id, placeholder) {
  const cb=$(`cb-${id}`); const t=$(`cbt-${id}`);
  const txt=t.querySelector('.selected-text'); txt.textContent=placeholder; txt.classList.add('placeholder');
  cb.dataset.value='';
  document.querySelectorAll(`#cbl-${id} .combobox-item`).forEach(i=>i.classList.remove('selected'));
  $(`cbd-${id}`).style.display='none'; t.classList.remove('open');
}
document.addEventListener('click',e=>{
  if(!e.target.closest('.combobox')) {
    document.querySelectorAll('.combobox-dropdown').forEach(d=>d.style.display='none');
    document.querySelectorAll('.combobox-trigger.open').forEach(t=>t.classList.remove('open'));
  }
});

// ─── SKELETON ─────────────────────────────────────────
const skCards=n=>Array(n).fill('').map(()=>`<div class="card"><div class="skeleton" style="aspect-ratio:16/9;border-radius:var(--radius) var(--radius) 0 0"></div><div class="card-body"><div class="skeleton" style="height:15px;width:55%;margin-bottom:7px"></div><div class="skeleton" style="height:12px;width:38%"></div></div></div>`).join('');
const skRows=n=>Array(n).fill('').map(()=>`<tr>${Array(6).fill('').map(()=>'<td><div class="skeleton" style="height:18px"></div></td>').join('')}</tr>`).join('');

// ─── GLOBAL SEARCH ────────────────────────────────────
async function onSearchInput(q) {
  const sr=$('search-results'), query=q.trim().toLowerCase();
  clearTimeout(searchTimeout);
  if(query.length < 2){ sr.style.display='none'; return; }
  searchTimeout=setTimeout(async()=>{
    try {
      const res=await cachedApiFetch('/videos?limit=50', 45000);
      if((document.getElementById('global-search')?.value.trim().toLowerCase() || '') !== query) return;
      const fil=res.filter(v=>
        v.map?.name?.toLowerCase().includes(query)||
        v.car?.name?.toLowerCase().includes(query)||
        v.user?.username?.toLowerCase().includes(query)
      ).slice(0, 6);
      if(!fil.length){ sr.innerHTML='<div style="padding:16px;text-align:center;color:var(--text-dim);font-size:0.83rem">Không tìm thấy kết quả</div>'; }
      else {
        sr.innerHTML=fil.map(v=>`
          <a href="#/video/${v.id}" onclick="$('search-results').style.display='none';$('global-search').value=''"
            style="display:flex;align-items:center;gap:12px;padding:10px 16px;border-bottom:1px solid var(--border);transition:background 0.15s;"
            onmouseover="this.style.background='rgba(255,255,255,0.04)'" onmouseout="this.style.background=''">
            <span class="record-time" style="font-size:0.9rem;white-space:nowrap">${fmtMs(v.record_ms)}</span>
            <div style="flex:1;overflow:hidden">
              <div style="font-size:0.85rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${esc(v.map?.name)} - ${esc(v.car?.name)}</div>
              <div style="font-size:0.75rem;color:var(--text-dim)">${esc(v.user?.username)}</div>
            </div>
          </a>`).join('');
      }
      sr.style.display='block';
    } catch {}
  }, 300);
}
document.addEventListener('click',e=>{if(!e.target.closest('#global-search')&&!e.target.closest('#search-results'))$('search-results').style.display='none';});

// ─── DELETE CONFIRM MODAL ─────────────────────────────
function confirmDelete(videoId, title) {
  const overlay=document.createElement('div');
  overlay.className='modal-overlay';
  overlay.innerHTML=`<div class="modal">
    <h3>Xóa Record</h3>
    <p>Bạn có chắc chắn muốn xóa "<strong>${esc(title)}</strong>"? Hành động này không thể hoàn tác.</p>
    <div class="modal-actions">
      <button class="btn btn-outline btn-sm" onclick="this.closest('.modal-overlay').remove()">Hủy</button>
      <button class="btn btn-danger btn-sm" onclick="doDelete('${videoId}',this.closest('.modal-overlay'))">Xóa</button>
    </div>
  </div>`;
  document.body.appendChild(overlay);
}
async function doDelete(id, overlay) {
  try {
    await apiFetch(`/videos/${id}`,{method:'DELETE'});
    clearApiCache();
    overlay.remove(); toast('Đã xóa record thành công!'); navigate('/');
  } catch(e) { toast(e.message,'error'); }
}

// ════════════════════════════════════════════════════
//                       PAGES
// ════════════════════════════════════════════════════

// ── HOME ──────────────────────────────────────────────
async function renderHome() {
  $('app').innerHTML=`<div class="animate-in" style="display:flex;flex-direction:column;gap:36px;">
    <section class="hero"><div class="hero-content">
      <h1 class="animate-up">Kho Dữ Liệu Tốc Độ<br><span class="grad" style="font-size:1.1em;">TENVYX CLAN (TNX)</span></h1>
      <p class="animate-up delay-1" style="color:var(--text-muted);font-size:1.1rem;line-height:1.6;">Lưu trữ, vinh danh kỷ lục và chia sẻ kỹ năng của các tay đua xuất sắc nhất thuộc Tenvyx Clan.</p>
      <div class="hero-actions animate-up delay-2">
        <a href="#/board" class="btn btn-purple" style="padding:12px 28px">&#127942; Bảng Xếp Hạng</a>
        <a href="#/upload" class="btn btn-outline" style="padding:12px 28px">&#9650; Đăng Record</a>
      </div>
      <div class="hero-stats animate-up delay-3" id="hero-stats">
        <div class="hero-stat"><div class="skeleton" style="height:28px;width:50px;margin-bottom:4px"></div><div class="skeleton" style="height:12px;width:50px"></div></div>
        <div class="hero-stat"><div class="skeleton" style="height:28px;width:50px;margin-bottom:4px"></div><div class="skeleton" style="height:12px;width:50px"></div></div>
        <div class="hero-stat"><div class="skeleton" style="height:28px;width:50px;margin-bottom:4px"></div><div class="skeleton" style="height:12px;width:50px"></div></div>
      </div>
    </div></section>
    <section>
      <div class="section-header">
        <h2 style="color:var(--neon-cyan); text-shadow:var(--neon-glow-cyan);">👑 Top 3 Vinh Danh 👑</h2>
      </div>
      <div class="video-grid" id="hall-of-fame" style="margin-bottom: 36px;">
        <div class="skeleton" style="height:100px;border-radius:var(--radius)"></div>
        <div class="skeleton" style="height:100px;border-radius:var(--radius)"></div>
        <div class="skeleton" style="height:100px;border-radius:var(--radius)"></div>
      </div>
    </section>
    <section>
    <section>
      <div class="section-header" style="display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; gap:16px;">
          <h2 id="tab-latest" class="tab-title active" onclick="switchHomeTab('latest')" style="cursor:pointer; color:var(--neon-cyan); transition:var(--transition); text-shadow:var(--neon-glow-cyan);">Mới Nhất</h2>
          <h2 id="tab-trending" class="tab-title" onclick="switchHomeTab('trending')" style="cursor:pointer; color:var(--text-dim); transition:var(--transition);">Xu Hướng</h2>
        </div>
        <a href="#/board" style="font-size:0.83rem;color:var(--purple-light)">Xem tất cả &rarr;</a>
      </div>
      <div class="video-grid" id="home-grid">${skCards(8)}</div>
    </section>
  </div>`;

  try {
    const [allVideos, maps, cars] = await Promise.all([
      cachedApiFetch('/videos?limit=200', 30000), cachedApiFetch('/maps', 300000), cachedApiFetch('/cars', 300000)
    ]);
    
    // Process Hall of Fame (Top 3 users by number of records)
    const userCounts = {};
    const userObjs = {};
    allVideos.filter(v => v.visibility === 'PUBLIC').forEach(v => {
      if(v.user) {
        userCounts[v.user.id] = (userCounts[v.user.id] || 0) + 1;
        userObjs[v.user.id] = v.user;
      }
    });
    const topUsers = Object.keys(userCounts)
      .map(id => ({ user: userObjs[id], count: userCounts[id] }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 3);
      
    $('hall-of-fame').innerHTML = topUsers.length 
      ? topUsers.map((u, i) => `
        <a href="#/profile/${u.user.id}" class="card card-hover" style="display:flex;align-items:center;padding:16px;gap:12px;background:linear-gradient(135deg,rgba(15,15,35,0.8),rgba(10,5,25,0.9));border:1px solid ${i===0?'var(--yellow)':(i===1?'#cbd5e1':'var(--orange)')};box-shadow:0 0 15px ${i===0?'rgba(251,191,36,0.2)':'transparent'}">
          <div style="font-size:1.8rem;font-weight:900;color:${i===0?'var(--yellow)':(i===1?'#cbd5e1':'var(--orange)')}">${i+1}</div>
          ${u.user.avatar ? `<img src="${esc(optimizedImage(u.user.avatar, 64))}" style="width:48px;height:48px;border-radius:50%;object-fit:cover;border:2px solid ${i===0?'var(--yellow)':'var(--border)'}"/>` : `<div style="width:48px;height:48px;border-radius:50%;background:var(--purple);display:flex;align-items:center;justify-content:center;font-weight:bold">${esc(u.user.username[0].toUpperCase())}</div>`}
          <div style="flex:1">
            <div style="font-weight:800;font-size:1rem;color:var(--text)">${esc(u.user.username)}</div>
            <div style="font-size:0.75rem;color:var(--text-muted)">${u.count} Kỷ lục</div>
          </div>
          ${i===0 ? '<div style="font-size:1.5rem">👑</div>' : ''}
        </a>
      `).join('')
      : '<div class="empty" style="grid-column:1/-1">Chưa có đủ dữ liệu</div>';

    $('hero-stats').innerHTML=`
      <div class="hero-stat"><div class="val">${allVideos.length}</div><div class="lbl">Số Record</div></div>
      <div class="hero-stat"><div class="val">${maps.length}</div><div class="lbl">Bản Đồ</div></div>
      <div class="hero-stat"><div class="val">${cars.length}</div><div class="lbl">Siêu Xe</div></div>`;
      
    window.homeAllVideos = allVideos;
    window.switchHomeTab('latest');
    
  } catch { $('home-grid').innerHTML='<div class="empty" style="color:var(--red)">Tải dữ liệu thất bại. Bạn đã chạy backend chưa?</div>'; }
}

window.switchHomeTab = function(tab) {
  const vids = window.homeAllVideos || [];
  if (tab === 'latest') {
    $('tab-latest').style.color = 'var(--neon-cyan)';
    $('tab-latest').style.textShadow = 'var(--neon-glow-cyan)';
    $('tab-trending').style.color = 'var(--text-dim)';
    $('tab-trending').style.textShadow = 'none';
    const sorted = [...vids].sort((a,b)=>new Date(b.created_at)-new Date(a.created_at));
    $('home-grid').innerHTML = sorted.slice(0, 8).map(videoCard).join('');
  } else {
    $('tab-trending').style.color = 'var(--neon-pink)';
    $('tab-trending').style.textShadow = 'var(--neon-glow-pink)';
    $('tab-latest').style.color = 'var(--text-dim)';
    $('tab-latest').style.textShadow = 'none';
    const sorted = [...vids].sort((a,b)=>((b.views||0)+(b.likes||0)*2) - ((a.views||0)+(a.likes||0)*2));
    $('home-grid').innerHTML = sorted.slice(0, 8).map(videoCard).join('');
  }
}

window.cachedVideos = window.cachedVideos || {};
function videoCard(v) {
  window.cachedVideos[v.id] = v;
  const img=proofImage(v, 640);
  const canEdit = currentUser && (currentUser.id === v.user?.id || currentUser.role === 'ADMIN');
  return `<div class="card card-hover video-card" style="position:relative;">
    ${canEdit ? `<div style="position:absolute;top:8px;right:8px;z-index:10;display:flex;gap:6px">
      <button class="btn-icon" style="background:rgba(0,0,0,0.7);color:#fff;padding:5px;" onclick="editRecord('${v.id}')" title="Sửa">&#9998;</button>
    </div>` : ''}
    <a href="javascript:void(0)" onclick="showQuickView('${v.id}')" class="thumb">
      <img src="${esc(img)}" alt="${esc(v.map?.name)}" width="640" height="360" loading="lazy" decoding="async"/>
      <div class="overlay"></div>
      <div class="time-badge">${fmtMs(v.record_ms)}</div>
      
    </a>
    <div class="info">
      <div class="title">${esc(v.map?.name)}</div>
      <div class="meta">
        <span>&#128663; ${esc(v.car?.name)}</span>
        <span>&#128100; ${esc(v.user?.username)}</span>
      </div>
      <div class="stats">
        <div class="stats-left"><span>&#128065; ${v.views||0}</span><span>&#128077; ${v.likes||0}</span></div>
        <span>${dateStr(v.created_at)}</span>
      </div>
    </div>
  </div>`;
}

// ── LOGIN ─────────────────────────────────────────────
function renderLogin() {
  $('app').innerHTML=`<div class="auth-wrap animate-in"><div class="auth-card card"><div class="card-body-lg">
    <h1 class="auth-title">&#128274; Đăng nhập</h1>
    <p class="auth-desc">Chào mừng trở lại căn cứ TNX!</p>
    <form id="lf" style="display:flex;flex-direction:column;gap:14px;">
      <div class="form-group"><label class="form-label">Tài khoản</label><input class="form-input" name="u" placeholder="Nhập tài khoản" required /></div>
      <div class="form-group"><label class="form-label">Mật khẩu</label><div style="position:relative;">
        <input class="form-input" type="password" name="p" placeholder="Nhập mật khẩu" required  style="padding-right:40px;"/>
        <button type="button" onclick="const i=this.previousElementSibling; if(i.type==='password'){i.type='text';this.innerHTML='&#128064;'}else{i.type='password';this.innerHTML='&#128065;'}" style="position:absolute;right:10px;top:50%;transform:translateY(-50%);background:none;border:none;color:var(--text-muted);font-size:1.1rem;cursor:pointer;transition:color 0.2s;">&#128065;</button>
      </div></div>
      <button class="btn btn-primary" type="submit" id="lb">Đăng nhập</button>
    </form>
    <div class="auth-foot">Chưa có tài khoản? <a href="#/register">Đăng ký tại đây</a></div>
  </div></div></div>`;
  $('lf').onsubmit=async e=>{
    e.preventDefault(); const b=$('lb'); b.disabled=true; b.innerHTML='<span class="spinner"></span> Đang xử lý...';
    try {
      const fd=new URLSearchParams(); fd.append('username',e.target.u.value); fd.append('password',e.target.p.value);
      const r=await fetch(`${API}/auth/login`,{method:'POST',body:fd});
      if(!r.ok) throw new Error((await r.json()).detail||'Đăng nhập thất bại');
      setToken((await r.json()).access_token); await fetchUser(); renderNav();
      toast('Xin chào, '+currentUser.username+'!'); navigate('/');
    } catch(err){ toast(err.message,'error'); b.disabled=false; b.textContent='Đăng nhập'; }
  };
}

// ── REGISTER ──────────────────────────────────────────
function renderRegister() {
  $('app').innerHTML=`<div class="auth-wrap animate-in"><div class="auth-card card"><div class="card-body-lg">
    <h1 class="auth-title">&#128293; Đăng ký</h1>
    <p class="auth-desc">Trở thành tay đua chính thức của Tenvyx Clan!</p>
    <form id="rf" style="display:flex;flex-direction:column;gap:14px;">
      <div class="form-group"><label class="form-label">Tài khoản</label><input class="form-input" name="u" placeholder="Tối thiểu 3 ký tự" required minlength="3"/></div>
      <div class="form-group"><label class="form-label">Email</label><input class="form-input" type="email" name="e" placeholder="email@cua-ban.com" required /></div>
      <div class="form-group"><label class="form-label">Mật khẩu</label><div style="position:relative;">
        <input class="form-input" type="password" name="p" placeholder="Tối thiểu 6 ký tự" required minlength="6" style="padding-right:40px;"/>
        <button type="button" onclick="const i=this.previousElementSibling; if(i.type==='password'){i.type='text';this.innerHTML='&#128064;'}else{i.type='password';this.innerHTML='&#128065;'}" style="position:absolute;right:10px;top:50%;transform:translateY(-50%);background:none;border:none;color:var(--text-muted);font-size:1.1rem;cursor:pointer;transition:color 0.2s;">&#128065;</button>
      </div></div>
      <div class="form-group"><label class="form-label">Xác nhận mật khẩu</label><div style="position:relative;">
        <input class="form-input" type="password" name="c" placeholder="Nhập lại mật khẩu" required  style="padding-right:40px;"/>
        <button type="button" onclick="const i=this.previousElementSibling; if(i.type==='password'){i.type='text';this.innerHTML='&#128064;'}else{i.type='password';this.innerHTML='&#128065;'}" style="position:absolute;right:10px;top:50%;transform:translateY(-50%);background:none;border:none;color:var(--text-muted);font-size:1.1rem;cursor:pointer;transition:color 0.2s;">&#128065;</button>
      </div></div>
      <button class="btn btn-primary" type="submit" id="rb">Tạo tài khoản</button>
    </form>
    <div class="auth-foot">Đã là thành viên? <a href="#/login">Đăng nhập tại đây</a></div>
  </div></div></div>`;
  $('rf').onsubmit=async e=>{
    e.preventDefault();
    if(e.target.p.value!==e.target.c.value){toast('Mật khẩu không khớp!','error');return;}
    const b=$('rb'); b.disabled=true; b.innerHTML='<span class="spinner"></span> Đang tạo...';
    try {
      await apiFetch('/auth/register',{method:'POST',body:JSON.stringify({username:e.target.u.value,email:e.target.e.value,password:e.target.p.value})});
      toast('Tạo tài khoản thành công! Vui lòng đăng nhập.'); navigate('/login');
    } catch(err){ toast(err.message,'error'); b.disabled=false; b.textContent='Tạo tài khoản'; }
  };
}

// ── UPLOAD ────────────────────────────────────────────
async function renderUpload() {
  if(!getToken()){ toast('Vui lòng đăng nhập trước','error'); navigate('/login'); return; }
  $('app').innerHTML=`<div class="animate-in" style="max-width:680px;margin:0 auto">${skCards(1)}</div>`;
  const [maps,cars,pets]=await Promise.all([cachedApiFetch('/maps', 300000), cachedApiFetch('/cars', 300000), cachedApiFetch('/pets', 300000)]);
  $('app').innerHTML=`<div class="animate-in" style="max-width:680px;margin:0 auto;">
    <h1 style="font-size:1.7rem;font-weight:800;margin-bottom:6px">&#9650; Đăng Record</h1>
    <p style="color:var(--text-muted);font-size:0.85rem;margin-bottom:22px">Chia sẻ kỷ lục đỉnh cao của bạn với cộng đồng.</p>
    <div class="card"><div class="card-body-lg">
    <form id="uf" style="display:flex;flex-direction:column;gap:18px;">
    <div class="form-group">
        <label class="form-label">Ảnh Kỷ Lục *</label>
        <input class="form-input" type="file" name="vfile" accept="image/*" required />
      </div>
      <div class="form-group">
        <label class="form-label">Link Video Youtube/Drive <span style="color:var(--text-dim)">(Tuỳ chọn)</span></label>
        <input class="form-input" type="url" name="vurl" placeholder="https://youtube.com/... hoặc https://drive.google.com/..." />
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
        <div class="form-group"><label class="form-label">Bản đồ *</label>${mkCombobox('map',maps.map(m=>({label:m.name,value:m.id})),'Chọn bản đồ...')}</div>
        <div class="form-group"><label class="form-label">Siêu xe *</label>${mkCombobox('car',cars.map(c=>({label:c.name,value:c.id,group:c.car_class==='T'?'⚡ Xe T (Siêu Xe)':'🏎️ Xe A (Xe Thường)'})),'Chọn siêu xe...')}</div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
        <div class="form-group">
          <label class="form-label">Thời gian * <span style="color:var(--text-dim)">(p:gg:cc)</span></label>
          <input class="form-input" name="rec" placeholder="1:23:45" style="font-family:monospace;letter-spacing:0.05em" required/>
        </div>
        <div class="form-group"><label class="form-label">Pet <span style="color:var(--text-dim)">(Tùy chọn)</span></label>${mkCombobox('pet',pets.map(p=>({label:p.name,value:p.id})),'Không có pet')}</div>
      </div>
      <div class="form-group">
        <label class="form-label">Quyền riêng tư</label>
        <select class="form-input" name="vis">
          <option value="PUBLIC">&#127758; Công khai — Mọi người đều có thể xem</option>
          <option value="PRIVATE">&#128274; Riêng tư — Chỉ tôi và Quản trị viên</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Mô tả <span style="color:var(--text-dim)">(Tùy chọn)</span></label>
        <textarea class="form-input" name="desc" placeholder="Bạn có mẹo chạy, cấu hình xe nào muốn chia sẻ không?"></textarea>
      </div>
      <button class="btn btn-primary" style="padding:12px" type="submit" id="ub">&#9650; Tải lên Record</button>
    </form>
    </div></div>
  </div>`;
  $('uf').onsubmit=async e=>{
    e.preventDefault();
    const mapId=$('cb-map')?.dataset.value, carId=$('cb-car')?.dataset.value;
    if(!mapId||!carId){toast('Vui lòng chọn Bản đồ và Xe','error');return;}
    const rec=e.target.rec.value;
    if(!/^\d+:\d{2}:\d{2}$/.test(rec)){toast('Định dạng thời gian phải là p:gg:cc (VD: 1:23:45)','error');return;}
    const imageFile = e.target.vfile.files[0];
    if(!imageFile || !imageFile.type.startsWith('image/')){toast('Vui lòng chọn ảnh kỷ lục hợp lệ','error');return;}
    const b=$('ub'); b.disabled=true; b.innerHTML='<span class="spinner"></span> Đang tải lên (1/2)...';
    try {
      // Bước 1: Upload trực tiếp lên Cloudinary
      const cfd = new FormData();
      cfd.append('file', imageFile);
      cfd.append('upload_preset', 'zsm_preset');
      
      const cres = await fetch('https://api.cloudinary.com/v1_1/ip5cfp9y/image/upload', {
        method: 'POST',
        body: cfd
      });
      if(!cres.ok) {
        const cerr = await cres.json();
        throw new Error('Lỗi từ Cloudinary: ' + (cerr.error?.message || 'Không thể tải ảnh'));
      }
      const cjson = await cres.json();
      const imageUrl = cjson.secure_url;

      // Bước 2: Bắn dữ liệu về Backend
      b.innerHTML='<span class="spinner"></span> Đang lưu kỷ lục (2/2)...';
      const payload = {
        thumbnail: imageUrl,
        video_url: cleanUrl(e.target.vurl.value),
        map_id: mapId,
        car_id: carId,
        pet_id: $('cb-pet')?.dataset.value || null,
        record_ms: parseRecord(rec),
        description: e.target.desc.value,
        visibility: e.target.vis.value
      };
      
      await apiFetch('/videos', {
        method:'POST',
        body: JSON.stringify(payload)
      });

      clearApiCache();
      toast('Đăng record thành công!'); navigate('/');
    } catch(err){ 
      console.error(err);
      toast(err.message,'error'); 
      b.disabled=false; 
      b.innerHTML='&#9650; Tải lên Record'; 
    }
  };
}

// ── BOARD ─────────────────────────────────────────────
async function renderBoard() {
  $('app').innerHTML=`<div class="animate-in" style="display:flex;flex-direction:column;gap:20px;">
    <div>
      <h1 style="font-size:1.9rem;font-weight:900">&#127942; Bảng Xếp Hạng</h1>
      <p style="color:var(--text-muted);font-size:0.85rem;margin-top:4px">Xếp hạng kỷ lục theo Bản đồ, Siêu xe và Pet.</p>
    </div>
    <div class="skeleton" style="height:130px;border-radius:var(--radius-lg)"></div>
    <div id="podium-container" class="podium-container" style="display:none"></div>
    <div class="card" style="overflow:hidden"><table class="data-table"><thead><tr>
      <th style="width:70px;text-align:center">Hạng</th><th>Tay đua</th><th>Siêu xe</th><th>Pet</th><th>Thời gian</th><th style="text-align:right">Xem</th>
    </tr></thead><tbody id="board-body">${skRows(5)}</tbody></table></div>
  </div>`;

  const [maps,cars,pets,allVideos]=await Promise.all([cachedApiFetch('/maps', 300000), cachedApiFetch('/cars', 300000), cachedApiFetch('/pets', 300000), cachedApiFetch('/videos?limit=500', 30000)]);
  
  let defaultMapId = '';
  if (allVideos && allVideos.length > 0 && maps && maps.length > 0) {
      const mapCounts = {};
      allVideos.filter(v => v.visibility === 'PUBLIC').forEach(v => {
          if(v.map_id) mapCounts[v.map_id] = (mapCounts[v.map_id] || 0) + 1;
      });
      let mostPopularMapId = null;
      let maxCount = 0;
      for (const [mid, count] of Object.entries(mapCounts)) {
          if (count > maxCount) { maxCount = count; mostPopularMapId = mid; }
      }
      if (mostPopularMapId) {
          defaultMapId = mostPopularMapId;
      }
  }

  $('app').querySelector('.skeleton').outerHTML=`<div class="filter-bar">
    <h2>Lọc Dữ Liệu</h2>
    <div class="filter-grid">
      <div class="form-group"><label class="form-label">Bản đồ</label>${mkCombobox('bmap',maps.map(m=>({label:m.name,value:m.id})),'Tất cả bản đồ',defaultMapId)}</div>
      <div class="form-group"><label class="form-label">Siêu xe</label>${mkCombobox('bcar',cars.map(c=>({label:c.name,value:c.id})),'Tất cả siêu xe')}</div>
      <div class="form-group"><label class="form-label">Pet</label>${mkCombobox('bpet',pets.map(p=>({label:p.name,value:p.id})),'Tất cả pet')}</div>
    </div>
    <button class="btn btn-purple btn-sm" style="margin-top:14px" onclick="loadBoard()">Áp dụng</button>
    <button class="btn btn-outline btn-sm" style="margin-top:14px" onclick="clearCB('bmap','Tất cả bản đồ');clearCB('bcar','Tất cả siêu xe');clearCB('bpet','Tất cả pet');loadBoard()">Khôi phục</button>
  </div>`;
  loadBoard();
}

async function loadBoard() {
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
                    <a href="#/profile/${e.player.id}" title="Xem Profile" style="text-decoration:none">${avatarHtml}</a>
                    <a href="#/profile/${e.player.id}" class="podium-name" style="text-decoration:none;color:var(--text);">${esc(e.player.username)}</a>
                    <a href="#/video/${e.video_id}" class="podium-time" style="text-decoration:none;">${fmtMs(e.record_ms)}</a>
                    <div class="podium-rank">${r}</div>
                </div>
            `);
        });
        podium.innerHTML = spots.join('');
    }
    
    const tableCard = body.closest('.card');
    if (rest.length > 0) {
        if(tableCard) tableCard.style.display = 'block';
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
        if(tableCard) tableCard.style.display = 'none';
        body.innerHTML='';
    }
  } catch (e) { 
      body.innerHTML=`<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--red)">Tải bảng xếp hạng thất bại. ${e.message}</td></tr>`; 
  }
}

// ── VIDEO DETAIL ──────────────────────────────────────
async function renderVideo(id) {
  $('app').innerHTML=`<div class="animate-in"><div class="skeleton" style="aspect-ratio:16/9;border-radius:20px;margin-bottom:24px"></div><div class="skeleton" style="height:180px;border-radius:12px"></div></div>`;
  try {
    const video=await apiFetch(`/videos/${id}`);
    const proof=proofImage(video, 1400);
    const videoLink=cleanUrl(video.video_url);
    const media=`<img src="${esc(proof)}" alt="Ảnh kỷ lục ${esc(video.map?.name||'record')}" loading="eager" decoding="async" fetchpriority="high" />`;
    const videoButton=videoLink
      ? `<a href="${esc(videoLink)}" target="_blank" rel="noopener" class="btn btn-purple btn-sm" style="flex-shrink:0">Xem Video &#8599;</a>`
      : '';

    let related='';
    try {
      const rel=await cachedApiFetch(`/videos?map_id=${video.map_id}&car_id=${video.car_id}&limit=6`, 30000);
      const fil=rel.filter(r=>r.id!==id);
      if(fil.length) related=`<div>
        <div style="font-size:0.8rem;font-weight:600;color:var(--text-dim);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:10px">Kỷ Lục Tương Tự</div>
        <div style="display:flex;flex-direction:column;gap:6px">
          ${fil.map(r=>`<a href="#/video/${r.id}" class="card card-hover" style="display:flex;align-items:center;gap:12px;padding:10px 14px" onclick="event.preventDefault(); showQuickView('${r.id}')">
            <span class="record-time">${fmtMs(r.record_ms)}</span>
            <div style="flex:1;overflow:hidden">
              <div style="font-size:0.82rem;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(r.user?.username)}</div>
            </div>
          </a>`).join('')}
        </div>
      </div>`;
    } catch {}

    const canDel=currentUser&&(currentUser.id===video.user_id||currentUser.role==='ADMIN');

    $('app').innerHTML=`<div class="animate-in" style="display:flex;flex-direction:column;gap:24px;">
      <div class="video-player" style="text-align:center;">
        <div class="bracket-frame" style="display:inline-block; border-radius:8px; overflow:hidden;">
          ${media}
        </div>
      </div>
      <div class="detail-grid">
        <div style="display:flex;flex-direction:column;gap:18px;">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-wrap:wrap;">
            <h1 class="glitch" data-text="${esc(video.map?.name)} — ${esc(video.car?.name)}" style="font-size:1.6rem;font-weight:800;letter-spacing:-0.02em;line-height:1.2;flex:1;min-width:min(260px,100%); color:transparent; background-clip:text; -webkit-background-clip:text; background-image:linear-gradient(90deg, var(--neon-cyan), var(--neon-pink));">${esc(video.map?.name)} — ${esc(video.car?.name)}</h1>
            <div style="display:flex;align-items:center;justify-content:flex-end;gap:8px;flex-wrap:wrap">
              ${videoButton}
              ${canDel?`<button class="btn btn-danger btn-sm" style="flex-shrink:0" onclick="confirmDelete('${video.id}','${esc(video.map?.name)} - ${esc(video.car?.name)}')">Xóa</button>`:''}
            </div>
          </div>
          <div class="info-bar" style="background:rgba(255,255,255,0.03); padding:10px 16px; border-radius:8px; border:1px solid rgba(255,255,255,0.08); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div style="display:flex;align-items:center;gap:10px">
              ${video.user?.avatar ? `<img src="${esc(optimizedImage(video.user.avatar, 80))}" class="avatar avatar-md" style="object-fit:cover; box-shadow:var(--neon-glow-purple); border:1px solid var(--neon-purple); cursor:pointer;" onclick="viewAvatar('${esc(optimizedImage(video.user.avatar, 600))}')" />` : `<span class="avatar avatar-md" style="box-shadow:var(--neon-glow-purple); border:1px solid var(--neon-purple);">${esc(video.user?.username[0].toUpperCase())}</span>`}
              <div><div style="font-size:0.72rem;color:var(--text-dim)">Người đăng</div><div style="font-weight:700;font-size:0.9rem; color:var(--neon-cyan);">${esc(video.user?.username)}</div></div>
            </div>
            <div style="display:flex;align-items:center;gap:16px;">
              <span class="info-stat">&#128197; ${dateStr(video.created_at)}</span>
              <span class="info-stat">&#128065; <span class="count-up" data-val="${video.views||0}">${video.views||0}</span></span>
              <div style="position:relative; display:inline-block;">
                <button onclick="toggleLike(this, '${video.id}')" class="btn btn-sm ${localStorage.getItem('liked_'+video.id) ? 'btn-purple' : 'btn-outline'}" style="border-color:var(--neon-pink); color:${localStorage.getItem('liked_'+video.id)?'white':'var(--neon-pink)'}; display:flex; align-items:center; gap:6px;">
                  ${localStorage.getItem('liked_'+video.id) ? '&#10084;' : '&#128077;'} <span id="like-count" class="count-up" data-val="${video.likes||0}">${video.likes||0}</span>
                </button>
                <div id="like-floating" style="position:absolute; top:0; left:50%; transform:translateX(-50%); pointer-events:none;"></div>
              </div>
              <button onclick="shareVideo('${video.id}')" class="btn btn-sm btn-outline" style="border-color:var(--neon-cyan); color:var(--neon-cyan);" title="Copy Link">&#128279; Share</button>
            </div>
          </div>
          <div class="card"><div class="card-body">
            <div style="font-size:0.8rem;font-weight:600;color:var(--text-dim);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:8px">Mô Tả</div>
            <p style="color:var(--text-muted);font-size:0.87rem;line-height:1.65;white-space:pre-wrap">${esc(video.description)||'Không có mô tả.'}</p>
          </div></div>
        </div>
        <div style="display:flex;flex-direction:column;gap:18px;">
          <div class="stat-card">
            <div style="text-align:center;padding-bottom:18px;border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:14px; background:rgba(0,0,0,0.2); border-radius:8px; padding-top:14px;">
              <div style="font-size:0.7rem;color:var(--neon-cyan);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;text-shadow:var(--neon-glow-cyan);">Thời gian kỷ lục</div>
              <div class="record-time record-time-xl" style="color:var(--neon-purple); text-shadow:var(--neon-glow-purple); font-size:2rem;">${fmtMs(video.record_ms)}</div>
            </div>
            <div class="stat-row"><span class="stat-label">&#128506; Bản đồ</span><span class="badge badge-blue">${esc(video.map?.name)}</span></div>
            <div class="stat-row"><span class="stat-label">&#128663; Siêu xe</span><span class="badge badge-orange">${esc(video.car?.name)}</span></div>
            <div class="stat-row"><span class="stat-label">&#128062; Pet</span>${video.pet?.name&&video.pet.name!=='None'?`<span class="badge badge-purple">${esc(video.pet.name)}</span>`:'<span style="color:var(--text-dim);font-style:italic">Không dùng</span>'}</div>
            <div class="stat-row" style="border-top:1px solid var(--border);margin-top:14px;padding-top:14px">
              <span class="stat-label">&#128274; Quyền riêng tư</span>
              <span class="badge ${video.visibility==='PUBLIC'?'badge-green':'badge-orange'}">${video.visibility==='PUBLIC'?'CÔNG KHAI':'RIÊNG TƯ'}</span>
            </div>
          </div>
          ${related}
        </div>
      </div>
    </div>
    <div class="card" style="margin-top: 24px; max-width: 1400px;">
      <div class="card-body">
        <div style="font-size:1.1rem;font-weight:700;margin-bottom:16px;color:var(--neon-cyan);text-shadow:var(--neon-glow-cyan);">Bình Luận</div>
        <div id="comments-list" style="display:flex;flex-direction:column;gap:12px;margin-bottom:20px;">
          <div class="skeleton" style="height:60px;border-radius:8px"></div>
        </div>
        ${currentUser ? `
          <form id="comment-form" onsubmit="submitComment(event, '${id}')" style="display:flex;gap:10px;">
            <input type="text" id="comment-input" class="form-input" placeholder="Viết bình luận của bạn..." required style="flex:1;" />
            <button type="submit" class="btn btn-purple">Gửi</button>
          </form>
        ` : '<div style="font-size:0.85rem;color:var(--text-muted)">Vui lòng <a href="#/login" style="color:var(--neon-cyan)">đăng nhập</a> để bình luận.</div>'}
      </div>
    </div>
  </div>`;
  
  loadComments(id);
  } catch { $('app').innerHTML='<div class="empty" style="color:var(--red)">Không tìm thấy record.</div>'; }
}

async function loadComments(videoId) {
  try {
    const comments = await apiFetch(`/videos/${videoId}/comments`);
    const list = $('comments-list');
    if (!list) return;
    
    if (comments.length === 0) {
      list.innerHTML = '<div class="empty" style="padding: 10px;">Chưa có bình luận nào.</div>';
      return;
    }
    
    list.innerHTML = comments.map(c => `
      <div id="comment-${c.id}" style="display:flex;gap:12px;padding:12px;background:var(--bg-input);border-radius:8px;position:relative;">
        ${c.user.avatar ? `<img src="${esc(optimizedImage(c.user.avatar, 64))}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;"/>` : `<div style="width:36px;height:36px;border-radius:50%;background:var(--purple);display:flex;align-items:center;justify-content:center;font-weight:bold">${esc(c.user.username[0].toUpperCase())}</div>`}
        <div style="flex:1">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px">
            <span style="font-weight:bold;font-size:0.9rem">${esc(c.user.username)}</span>
            <span style="font-size:0.75rem;color:var(--text-dim)">${dateStr(c.created_at)}</span>
          </div>
          <div style="font-size:0.85rem;color:var(--text);white-space:pre-wrap;">${esc(c.content)}</div>
        </div>
        ${(currentUser && (currentUser.id === c.user_id || currentUser.role === 'ADMIN')) ? `<button onclick="delComment('${videoId}', '${c.id}')" style="background:none;border:none;color:var(--red);cursor:pointer;position:absolute;top:10px;right:10px;font-size:1.1rem" title="Xóa">&#128465;</button>` : ''}
      </div>
    `).join('');
  } catch (e) {
    console.error(e);
    if($('comments-list')) $('comments-list').innerHTML = '<div class="empty" style="color:var(--red)">Lỗi tải bình luận.</div>';
  }
}

window.submitComment = async function(e, videoId) {
  e.preventDefault();
  const input = $('comment-input');
  const btn = e.target.querySelector('button');
  const content = input.value.trim();
  if (!content) return;
  
  btn.disabled = true;
  btn.textContent = 'Đang gửi...';
  
  try {
    await apiFetch(`/videos/${videoId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ content })
    });
    input.value = '';
    await loadComments(videoId);
  } catch(err) {
    alert('Lỗi khi gửi bình luận');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Gửi';
  }
}

// ── PROFILE ───────────────────────────────────────────
window.editProfile = async function(field) {
  if (field === 'avatar') {
    const file = document.createElement('input');
    file.type = 'file'; file.accept = 'image/*';
    file.onchange = async e => {
      const f = e.target.files[0];
      if(!f) return;
      const b = $('avatar-edit-btn');
      b.innerHTML = '<span class="spinner" style="width:12px;height:12px"></span>';
      const fd = new FormData(); fd.append('avatar_file', f);
      try {
        const r = await fetch(`${API}/users/me/avatar`, {
          method: 'POST',
          headers: {'Authorization': `Bearer ${getToken()}`},
          body: fd
        });
        if(!r.ok) throw new Error((await r.json()).detail || 'Lỗi cập nhật avatar');
        toast('Cập nhật Avatar thành công!');
        clearApiCache();
        await fetchUser(); renderProfile(currentUser.id); renderNav();
      } catch(err) { toast(err.message, 'error'); b.innerHTML = 'Đổi ảnh'; }
    };
    file.click();
  } else if (field === 'username') {
    const newName = prompt('Nhập tên người dùng mới (Tối thiểu 3 ký tự):', currentUser.username);
    if (!newName || newName === currentUser.username) return;
    try {
      const r = await fetch(`${API}/users/me/username`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${getToken()}`},
        body: JSON.stringify({username: newName})
      });
      if(!r.ok) throw new Error((await r.json()).detail || 'Lỗi cập nhật tên');
      toast('Cập nhật tên thành công!');
      clearApiCache();
      await fetchUser(); renderProfile(currentUser.id); renderNav();
    } catch(err) { toast(err.message, 'error'); }
  }
};

async function renderProfile(userId) {
  $('app').innerHTML=`<div class="animate-in"><div class="skeleton" style="height:130px;border-radius:var(--radius-lg);margin-bottom:24px"></div><div class="video-grid">${skCards(6)}</div></div>`;
  try {
    const [videos, user] = await Promise.all([
      apiFetch(`/videos?user_id=${userId}&limit=50`),
      apiFetch(`/users/${userId}`)
    ]);
    const totalMs = videos.reduce((a,v) => a+(v.record_ms||0), 0);
    const isOwner = currentUser?.id === userId;
      const publicVideos = videos.filter(v => v.visibility === 'PUBLIC');
    
    
    // Gamification Logic
    const exp = user.exp || 0;
    const level = Math.floor(Math.sqrt(exp / 100)) + 1;
    const currentLevelExp = Math.pow(level - 1, 2) * 100;
    const nextLevelExp = Math.pow(level, 2) * 100;
    const progress = ((exp - currentLevelExp) / (nextLevelExp - currentLevelExp)) * 100;

    let petName = 'Trứng Gà';
    let petEmoji = '🥚';
    let pColor = '#ccc';
    if (level >= 20) { petName = 'Rồng Thần'; petEmoji = '🐉'; pColor = 'var(--neon-pink)'; }
    else if (level >= 10) { petName = 'Tiểu Long'; petEmoji = '🦎'; pColor = 'var(--neon-blue)'; }
    else if (level >= 5) { petName = 'Gà Chọi'; petEmoji = '🐓'; pColor = '#ffeb3b'; }
    else if (level >= 2) { petName = 'Gà Con'; petEmoji = '🐥'; pColor = '#4caf50'; }

    let badgeHtml = '';
    if (user.role === 'ADMIN') badgeHtml = `<span class="badge-label badge-boss" title="Quản trị viên">Boss</span>`;
    else if (publicVideos.length >= 15) badgeHtml = `<span class="badge-label badge-monster" title="Trên 15 kỷ lục">Quái Vật Drift</span>`;
    else if (publicVideos.length >= 5) badgeHtml = `<span class="badge-label badge-pro" title="Trên 5 kỷ lục">Racer Chuyên Nghiệp</span>`;
    else badgeHtml = `<span class="badge-label badge-rookie" title="Dưới 5 kỷ lục">Tân Binh</span>`;

    // Calculate cooldowns
    let avatarWait = '', nameWait = '';
    if (isOwner) {
      const now = new Date();
      if (currentUser.last_avatar_update) {
        const d = new Date(currentUser.last_avatar_update + (currentUser.last_avatar_update.endsWith('Z') ? '' : 'Z'));
        const diff = Date.now() - d.getTime();
        if (diff < 86400000 && currentUser.avatar_update_count >= 5) {
           let h = Math.ceil((86400000 - diff) / 3600000);
           if (h > 24) h = 24;
           if (h < 1) h = 1;
           avatarWait = `(Chờ ${h}h)`;
        }
      }
      if (currentUser.last_username_update) {
        const d = new Date(currentUser.last_username_update + 'Z');
        const diff = now - d;
        if (diff < 7*86400000) nameWait = `(Chờ ${Math.ceil((7*86400000-diff)/86400000)} ngày)`;
      }
    }

    $('app').innerHTML=`<div class="animate-in" style="display:flex;flex-direction:column;gap:24px;">
      <div class="profile-header" style="display:flex; gap:24px; align-items:center; flex-wrap:wrap; background:var(--card-bg); padding:24px; border-radius:var(--radius-lg); border:1px solid rgba(255,255,255,0.05); box-shadow:var(--shadow-lg);">
        <div style="position:relative; display:flex; flex-direction:column; align-items:center; gap:8px;${user.avatar ? ' cursor:pointer;' : ''}" ${user.avatar ? `onclick="viewAvatar('${esc(optimizedImage(user.avatar, 1200))}')"` : ''}>
          ${user.avatar 
            ? `<img src="${esc(optimizedImage(user.avatar, 160))}" class="avatar avatar-lg" width="100" height="100" loading="eager" decoding="async" style="object-fit:cover; border:3px solid ${pColor}; box-shadow:0 0 15px ${pColor};" />`
            : `<div style="width:100px;height:100px;border-radius:50%;background:var(--bg-dark);display:flex;align-items:center;justify-content:center;font-size:3rem;font-weight:700;color:${pColor};border:3px solid ${pColor};box-shadow:0 0 15px ${pColor}">${esc(user.username[0].toUpperCase())}</div>`
          }
          <div style="text-align:center; font-size:1.5rem;" title="${petName}">${petEmoji} <span style="font-size:0.8rem; color:var(--text-secondary); display:block; font-weight:bold;">Lv.${level}</span></div>
          ${isOwner ? `<button id="avatar-edit-btn" onclick="event.stopPropagation(); editProfile('avatar')" class="btn btn-sm" style="position:absolute;bottom:35px;left:50%;transform:translateX(-50%);background:var(--bg-card);border:1px solid var(--border);font-size:0.7rem;padding:4px 8px;white-space:nowrap;">Đổi ảnh ${avatarWait}</button>` : ''}
        </div>
        <div class="profile-info" style="flex:1;">
          <h2 style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
            <span ${isOwner ? `style="cursor:pointer;border-bottom:1px dashed rgba(255,255,255,0.3)" onclick="triggerFieldEdit('username')" title="Nhấp để đổi tên ${nameWait}"` : ''}>${esc(user.username)}</span>
            ${badgeHtml}
          </h2>
          <div style="margin-bottom:16px;">
            <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:var(--text-secondary);margin-bottom:4px;">
              <span>EXP: ${exp}</span>
              <span>Tiếp theo: ${nextLevelExp}</span>
            </div>
            <div style="width:100%;height:8px;background:rgba(255,255,255,0.1);border-radius:4px;overflow:hidden;">
              <div style="width:${progress}%;height:100%;background:linear-gradient(90deg, var(--neon-pink), ${pColor});border-radius:4px;transition:width 1s ease-in-out;"></div>
            </div>
          </div>
          <p style="margin-bottom:12px;">${isOwner ? 'Hồ sơ của bạn' : 'Tay đua cộng đồng'}</p>
          <div class="profile-stats">
            <div class="profile-stat"><div class="val">${publicVideos.length}</div><div class="lbl">Số Record</div></div>
            <div class="profile-stat"><div class="val">${publicVideos.reduce((a,v)=>a+(v.views||0),0)}</div><div class="lbl">Tổng lượt xem</div></div>
            ${publicVideos.length?`<div class="profile-stat"><div class="val record-time" style="font-size:1.4rem">${fmtMs(Math.min(...publicVideos.map(v=>v.record_ms)))}</div><div class="lbl">Thành tích tốt nhất</div></div>`:''}
          </div>
        </div>
      </div>
      
      ${videos.length > 0 ? `
      <div class="card" style="margin-top: 24px; padding: 20px;">
        <h3 style="margin-bottom: 15px; font-size: 1rem; color: var(--neon-cyan); text-shadow: var(--neon-glow-cyan);">Biểu đồ Tiến bộ (Thời gian Kỷ lục)</h3>
        <canvas id="progressionChart" style="max-height: 250px;"></canvas>
      </div>` : ''}

      <div class="section-header" style="margin-top:20px;"><h2>Tất Cả Record</h2></div>
      <div class="video-grid">
        ${videos.length ? videos.map(videoCard).join('') : '<div class="empty">Người này chưa tải lên record nào.</div>'}
      </div>
    </div>`;

    if (videos.length > 0 && typeof Chart !== 'undefined') {
      const sortedVideos = [...videos].sort((a,b) => new Date(a.created_at) - new Date(b.created_at));
      const labels = sortedVideos.map(v => new Date(v.created_at).toLocaleDateString('vi-VN'));
      const data = sortedVideos.map(v => v.record_ms / 1000);
      
      new Chart($('progressionChart'), {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Thời gian (Giây)',
            data: data,
            borderColor: '#0ff',
            backgroundColor: 'rgba(0, 255, 255, 0.1)',
            borderWidth: 2,
            tension: 0.3,
            fill: true,
            pointBackgroundColor: '#f0f',
            pointBorderColor: '#f0f'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { title: { display: true, text: 'Thời gian (Giây)' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            x: { grid: { color: 'rgba(255,255,255,0.05)' } }
          },
          plugins: { legend: { display: false } }
        }
      });
    }

  } catch(e) { console.error(e); $('app').innerHTML='<div class="empty" style="color:var(--red)">Không tìm thấy hồ sơ người dùng.</div>'; }
}

// ── ADMIN ─────────────────────────────────────────────
async function renderAdmin() {
  if(!currentUser||currentUser.role!=='ADMIN'){ toast('Bạn không có quyền truy cập trang này!','error'); navigate('/'); return; }
  let tab='maps';

  async function renderTab() {
    const [maps,cars,pets,users]=await Promise.all([cachedApiFetch('/maps', 300000),cachedApiFetch('/cars', 300000),cachedApiFetch('/pets', 300000),apiFetch('/users')]);
    $('app').innerHTML=`<div class="animate-in" style="display:flex;flex-direction:column;gap:20px;">
      <div><h1 style="font-size:1.7rem;font-weight:800">&#128736; Bảng Quản Trị</h1><p style="color:var(--text-muted);font-size:0.85rem">Quản lý dữ liệu hệ thống.</p></div>
      <div><div class="tabs">
        <button class="tab-btn${tab==='maps'?' active':''}" onclick="adminTab('maps')">Bản đồ (${maps.length})</button>
        <button class="tab-btn${tab==='cars'?' active':''}" onclick="adminTab('cars')">Siêu xe (${cars.length})</button>
        <button class="tab-btn${tab==='pets'?' active':''}" onclick="adminTab('pets')">Pets (${pets.length})</button>
        <button class="tab-btn${tab==='users'?' active':''}" onclick="adminTab('users')">Tài khoản (${users.length})</button>
      </div></div>

      ${tab==='maps'?`
        <div class="card"><div class="card-body">
          <div style="font-size:0.85rem;font-weight:700;margin-bottom:10px">Thêm Bản đồ mới</div>
          <div class="admin-add-form">
            <div class="form-group"><label class="form-label">Tên bản đồ *</label><input class="form-input" id="mn" placeholder="Tên bản đồ"/></div>
            <div class="form-group" style="max-width:90px"><label class="form-label">Độ khó (sao)</label><input class="form-input" id="md" type="number" min="1" max="10" value="1"/></div>
            <button class="btn btn-primary btn-sm" onclick="adminAdd('map')">+ Thêm</button>
          </div>
        </div></div>
        <div class="card" style="overflow:hidden"><table class="data-table"><thead><tr><th>Tên</th><th>Độ khó</th><th>Mã ID</th></tr></thead>
        <tbody>${maps.map(m=>`<tr><td style="font-weight:600">${esc(m.name)}</td><td><span style="color:var(--yellow)">${'★'.repeat(m.difficulty||1)}</span></td><td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${m.id}</td></tr>`).join('')}</tbody>
        </table></div>`:
      tab==='cars'?`
        <div class="card"><div class="card-body">
          <div style="font-size:0.85rem;font-weight:700;margin-bottom:10px">Thêm Siêu xe mới</div>
          <div class="admin-add-form">
            <div class="form-group"><label class="form-label">Tên xe *</label><input class="form-input" id="cn" placeholder="Tên xe"/></div>
            <div class="form-group" style="max-width:90px"><label class="form-label">Phân khúc</label><input class="form-input" id="cc" placeholder="S, A..."/></div>
            <button class="btn btn-sm" style="background:var(--orange);color:#fff" onclick="adminAdd('car')">+ Thêm</button>
          </div>
        </div></div>
        <div class="card" style="overflow:hidden"><table class="data-table"><thead><tr><th>Tên</th><th>Phân khúc</th><th>Mã ID</th></tr></thead>
        <tbody>${cars.map(c=>`<tr><td style="font-weight:600">${esc(c.name)}</td><td><span class="badge badge-orange">${esc(c.car_class||'?')}</span></td><td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${c.id}</td></tr>`).join('')}</tbody>
        </table></div>`:
      tab==='pets'?`<div class="card"><div class="card-body">
          <div style="font-size:0.85rem;font-weight:700;margin-bottom:10px">Thêm Pet mới</div>
          <div class="admin-add-form">
            <div class="form-group"><label class="form-label">Tên Pet *</label><input class="form-input" id="pn" placeholder="Tên Pet"/></div>
            <button class="btn btn-sm" style="background:var(--purple);color:#fff" onclick="adminAdd('pet')">+ Thêm</button>
          </div>
        </div></div>
        <div class="card" style="overflow:hidden"><table class="data-table"><thead><tr><th>Tên</th><th>Mã ID</th></tr></thead>
        <tbody>${pets.map(p=>`<tr><td style="font-weight:600">${esc(p.name)}</td><td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${p.id}</td></tr>`).join('')}</tbody>
        </table></div>`:
      tab==='users'?`
        <div class="card" style="overflow:hidden"><table class="data-table"><thead><tr><th>Avatar</th><th>Tài khoản</th><th>Email</th><th>Quyền</th><th>Mã ID</th><th>Hành động</th></tr></thead>
        <tbody>${users.map(u=>`<tr>
          <td>${u.avatar?`<img src="${esc(optimizedImage(u.avatar, 48))}" width="28" height="28" loading="lazy" decoding="async" style="width:28px;height:28px;border-radius:50%;object-fit:cover"/>`:`<div class="avatar avatar-sm">${esc(u.username[0].toUpperCase())}</div>`}</td>
          <td style="font-weight:600">${esc(u.username)}</td>
          <td style="color:var(--text-dim)">${esc(u.email)}</td>
          <td><span class="badge ${u.role==='ADMIN'?'badge-red':'badge-blue'}">${esc(u.role)}</span></td>
          <td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${u.id}</td>
          <td><button class="btn btn-sm btn-outline" onclick="adminEditUser('${u.id}', '${esc(u.username)}', '${esc(u.email)}')">&#9998; Sửa</button></td>
        </tr>`).join('')}</tbody>
        </table></div>`:''}
    </div>`;
  }

  window.adminTab=(t)=>{ tab=t; renderTab(); };
  window.adminAdd=async(type)=>{
    try {
      if(type==='map'){
        const n=$('mn').value; if(!n){toast('Vui lòng nhập tên','error');return;}
        await apiFetch('/admin/maps',{method:'POST',body:JSON.stringify({name:n, difficulty: parseInt($('md').value||1)})});
      } else if(type==='car'){
        const n=$('cn').value; if(!n){toast('Vui lòng nhập tên','error');return;}
        await apiFetch('/admin/cars',{method:'POST',body:JSON.stringify({name:n,car_class:$('cc').value||'A'})});
      } else {
        const n=$('pn').value; if(!n){toast('Vui lòng nhập tên','error');return;}
        await apiFetch('/admin/pets',{method:'POST',body:JSON.stringify({name:n})});
      }
      clearApiCache();
      toast('Đã thêm thành công!'); renderTab();
    } catch(e){ toast(e.message,'error'); }
  };

  renderTab();
}

// ─── ROUTER ──────────────────────────────────────────
async function router() {
  const hash=window.location.hash.slice(1)||'/';
  const parts=hash.split('/').filter(Boolean);
  // Update active nav links
  document.querySelectorAll('[data-route]').forEach(l=>l.classList.toggle('active',l.dataset.route===hash||(l.dataset.route==='/'&&hash==='/')));

  if(hash==='/'||hash==='') return renderHome();
  if(hash==='/login') return renderLogin();
  if(hash==='/register') return renderRegister();
  if(hash==='/upload') return renderUpload();
  if(hash==='/board') return renderBoard();
  if(hash==='/admin') return renderAdmin();
  if(parts[0]==='video'&&parts[1]) return renderVideo(parts[1]);
  if(parts[0]==='profile'&&parts[1]) return renderProfile(parts[1]);
  if(parts[0]==='insights') return renderInsights();
  if(parts[0]==='tournaments') return renderTournaments();
  $('app').innerHTML='<div class="empty"><div class="empty-icon">&#128270;</div><p>Không tìm thấy trang.</p><a href="#/" style="color:var(--purple-light);margin-top:8px;display:inline-block">Về trang chủ &rarr;</a></div>';
}

window.addEventListener('hashchange', router);
window.doDelete=doDelete;
window.loadBoard=loadBoard;
window.confirmDelete=confirmDelete;

window.adminEditUser = function(id, curName, curEmail) {
  const overlay=document.createElement('div');
  overlay.className='modal-overlay';
  overlay.innerHTML=`<div class="modal">
    <h3>Sửa Người Dùng</h3>
    <form id="euf" style="display:flex;flex-direction:column;gap:14px;">
      <div class="form-group"><label class="form-label">Tên</label><input class="form-input" name="un" value="${curName}" required/></div>
      <div class="form-group"><label class="form-label">Email</label><input class="form-input" name="em" value="${curEmail}" required/></div>
      <div class="modal-actions" style="margin-top:10px">
        <button type="button" class="btn btn-outline btn-sm" onclick="this.closest('.modal-overlay').remove()">Hủy</button>
        <button type="submit" class="btn btn-primary btn-sm">Lưu</button>
      </div>
    </form>
  </div>`;
  document.body.appendChild(overlay);
  $('euf').onsubmit=async e=>{
    e.preventDefault();
    try {
      await apiFetch(`/users/${id}/admin`, {method:'PUT', body:JSON.stringify({username: e.target.un.value, email: e.target.em.value})});
      overlay.remove(); toast('Đã cập nhật!'); window.adminTab('users');
    } catch(err){ toast(err.message, 'error'); }
  };
};

window.editRecord = async function(id) {
  try {
    const v = await apiFetch(`/videos/${id}`);
    const [maps, cars, pets] = await Promise.all([cachedApiFetch('/maps', 300000), cachedApiFetch('/cars', 300000), cachedApiFetch('/pets', 300000)]);
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `<div class="modal" style="max-width:500px">
      <h3>Sửa Record</h3>
      <form id="erf" style="display:flex;flex-direction:column;gap:14px;">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
          <div class="form-group"><label class="form-label">Bản đồ</label>${mkCombobox('emap',maps.map(m=>({label:m.name,value:m.id})),'Chọn bản đồ...', v.map_id)}</div>
          <div class="form-group"><label class="form-label">Siêu xe</label>${mkCombobox('ecar',cars.map(c=>({label:c.name,value:c.id})),'Chọn siêu xe...', v.car_id)}</div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
          <div class="form-group">
            <label class="form-label">Thời gian <span style="color:var(--text-dim)">(p:gg:cc)</span></label>
            <input class="form-input" name="rec" value="${fmtMs(v.record_ms)}" style="font-family:monospace;letter-spacing:0.05em" required/>
          </div>
          <div class="form-group"><label class="form-label">Pet</label>${mkCombobox('epet',pets.map(p=>({label:p.name,value:p.id})),'Không có pet', v.pet_id||'')}</div>
        </div>
        <div class="form-group">
          <label class="form-label">Link Video Youtube/Drive <span style="color:var(--text-dim)">(Tùy chọn)</span></label>
          <input class="form-input" type="url" name="vurl" value="${esc(v.video_url||'')}" placeholder="https://youtube.com/... hoặc https://drive.google.com/..." />
        </div>
        <div class="form-group">
          <label class="form-label">Quyền riêng tư</label>
          <select class="form-input" name="vis">
            <option value="PUBLIC" ${v.visibility==='PUBLIC'?'selected':''}>Công khai</option>
            <option value="PRIVATE" ${v.visibility==='PRIVATE'?'selected':''}>Riêng tư</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Mô tả</label>
          <textarea class="form-input" name="desc">${esc(v.description||'')}</textarea>
        </div>
        <div class="modal-actions" style="margin-top:10px">
          <button type="button" class="btn btn-outline btn-sm" onclick="this.closest('.modal-overlay').remove()">Hủy</button>
          <button type="submit" class="btn btn-primary btn-sm">Lưu Thay Đổi</button>
        </div>
      </form>
    </div>`;
    document.body.appendChild(overlay);
    $('erf').onsubmit = async e => {
      e.preventDefault();
      const mapId=$('cb-emap')?.dataset.value, carId=$('cb-ecar')?.dataset.value, petId=$('cb-epet')?.dataset.value;
      const rec = e.target.rec.value;
      if(!/^\d+:\d{2}:\d{2}$/.test(rec)){toast('Định dạng thời gian phải là p:gg:cc (VD: 1:23:45)','error');return;}
      const payload = {
        map_id: mapId, car_id: carId, pet_id: petId||null,
        record_ms: parseRecord(rec),
        video_url: cleanUrl(e.target.vurl.value),
        description: e.target.desc.value, visibility: e.target.vis.value
      };
      try {
        await apiFetch(`/videos/${id}`, {method:'PUT', body:JSON.stringify(payload)});
        clearApiCache();
        overlay.remove(); toast('Đã cập nhật record!');
        if(window.location.hash.includes('board')) loadBoard(); else if(window.location.hash.includes('profile')) renderProfile(window.location.hash.split('/')[2]); else { renderHome(); }
      } catch(err){ toast(err.message, 'error'); }
    };
  } catch(e) { toast('Lỗi tải dữ liệu', 'error'); }
};


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

// ─── INIT ─────────────────────────────────────────────
(async()=>{ await fetchUser(); renderNav(); router(); })();

window.viewAvatar = function(url) {
  if(!url) return;
  const overlay = document.createElement('div');
  overlay.className = 'quick-view-overlay active';
  overlay.style.zIndex = '10000';
  overlay.innerHTML = `
    <span class="btn-close-modal" style="position:fixed; top:20px; right:20px; font-size:2.5rem; color:#fff; cursor:pointer;" onclick="this.parentElement.remove()">&times;</span>
    <img src="${url}" style="max-width:90vw; max-height:90vh; object-fit:cover;width:100%;height:100%; border-radius:8px; box-shadow:0 0 40px rgba(0,0,0,0.8);" />
  `;
  overlay.onclick = (e) => {
    if(e.target === overlay) overlay.remove();
  };
  document.body.appendChild(overlay);
}


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


window.toggleLike = async function(btn, videoId) {
    const isLiked = localStorage.getItem('liked_' + videoId);
    try {
        const countSpan = document.getElementById('like-count');
        let currentLikes = countSpan ? parseInt(countSpan.innerText) : 0;
        if (isLiked) {
            await apiFetch(`/videos/${videoId}/unlike`, {method: 'POST'});
            localStorage.removeItem('liked_' + videoId);
            currentLikes = Math.max(0, currentLikes - 1);
            btn.innerHTML = `&#128077; <span id="like-count" class="count-up" data-val="${currentLikes}">${currentLikes}</span>`;
            btn.classList.remove('btn-purple');
            btn.classList.add('btn-outline');
            btn.style.color = 'var(--neon-pink)';
        } else {
            await apiFetch(`/videos/${videoId}/like`, {method: 'POST'});
            localStorage.setItem('liked_' + videoId, 'true');
            currentLikes += 1;
            btn.innerHTML = `&#10084; <span id="like-count" class="count-up" data-val="${currentLikes}">${currentLikes}</span>`;
            btn.classList.remove('btn-outline');
            btn.classList.add('btn-purple');
            btn.style.color = 'white';
            
            const floating = document.getElementById('like-floating');
            if(floating) {
                floating.innerHTML = '<span style="font-size:1.5rem;color:var(--neon-pink);display:inline-block;animation:floatUp 0.8s ease-out forwards">&#10084;</span>';
                setTimeout(() => floating.innerHTML='', 800);
            }
        }
    } catch(e) {
        toast('Lỗi: ' + e.message, 'error');
    }
}

window.shareVideo = function(videoId) {
    const url = window.location.origin + window.location.pathname + '#/video/' + videoId;
    navigator.clipboard.writeText(url).then(() => {
        toast('Đã sao chép liên kết video!');
    }).catch(err => {
        toast('Không thể sao chép liên kết!', 'error');
    });
}

window.delComment = function(videoId, commentId) {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `<div class="modal">
      <h3>Xóa bình luận</h3>
      <p>Bạn có chắc chắn muốn xóa bình luận này?</p>
      <div class="modal-actions">
        <button class="btn btn-outline btn-sm" onclick="this.closest('.modal-overlay').remove()">Hủy</button>
        <button class="btn btn-danger btn-sm" onclick="doDelComment('${videoId}', '${commentId}', this.closest('.modal-overlay'))">Xóa</button>
      </div>
    </div>`;
    document.body.appendChild(overlay);
}

window.doDelComment = async function(videoId, commentId, overlay) {
    try {
        await apiFetch(`/videos/${videoId}/comments/${commentId}`, {method: 'DELETE'});
        if (overlay) overlay.remove();
        toast('Đã xóa bình luận!');
        const el = document.getElementById('comment-' + commentId);
        if(el) el.remove();
    } catch(e) {
        toast('Lỗi xóa bình luận: ' + e.message, 'error');
    }
}

// Notifications logic
let notifsData = [];
let notifPollInterval = null;

async function fetchNotifications() {
  if (!currentUser) return;
  try {
    const res = await fetch(`${API}/users/me/notifications`, {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    if (res.ok) {
      notifsData = await res.json();
      updateNotifBadge();
    }
  } catch(e) { console.error(e); }
}

function updateNotifBadge() {
  const badge = $('notif-badge');
  if (!badge) return;
  const unreadCount = notifsData.filter(n => !n.is_read).length;
  if (unreadCount > 0) {
    badge.textContent = unreadCount;
    badge.style.display = 'block';
  } else {
    badge.style.display = 'none';
  }
}

window.toggleNotifications = async function() {
  const dropdown = $('notif-dropdown');
  if (dropdown.style.display === 'none') {
    dropdown.style.display = 'block';
    if (notifsData.length === 0) {
      dropdown.innerHTML = '<div style="text-align:center;padding:10px;color:var(--text-secondary);">Không có thông báo nào.</div>';
    } else {
      dropdown.innerHTML = notifsData.map(n => `
        <div style="padding:10px;border-bottom:1px solid rgba(255,255,255,0.05);background:${n.is_read?'transparent':'rgba(255,107,158,0.1)'};border-radius:4px;margin-bottom:4px;">
          ${esc(n.message)}
          <div style="font-size:0.7rem;color:var(--text-secondary);margin-top:4px;">${dateStr(n.created_at)}</div>
        </div>
      `).join('');
    }
    
    // Mark as read
    const unread = notifsData.some(n => !n.is_read);
    if (unread) {
      try {
        await fetch(`${API}/users/me/notifications/read`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        notifsData.forEach(n => n.is_read = true);
        updateNotifBadge();
      } catch(e) {}
    }
  } else {
    dropdown.style.display = 'none';
  }
};

document.addEventListener('click', (e) => {
  const dropdown = $('notif-dropdown');
  if (dropdown && dropdown.style.display === 'block' && !e.target.closest('.nav-icon')) {
    dropdown.style.display = 'none';
  }
});

// Start polling
setInterval(() => {
  if (currentUser) fetchNotifications();
}, 30000);
