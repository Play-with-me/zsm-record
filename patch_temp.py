import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Add Level calculation logic and pet info before `let badgeHtml`
pet_logic = '''      // EXP and Level logic
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

      let badgeHtml = '';'''

js = js.replace("      let badgeHtml = '';", pet_logic)


# 2. Modify Avatar border color and add EXP Progress bar in the profile header
old_profile_header = '''      $('app').innerHTML = `
        <div class="animate-in fade-in slide-in">
          <div style="background:var(--card-bg); border-radius:var(--radius-lg); padding:32px; margin-bottom:32px; display:flex; gap:32px; align-items:center; border:1px solid rgba(255,255,255,0.05); box-shadow:var(--shadow-lg); flex-wrap:wrap">
            <div style="position:relative; cursor:${isOwner?'pointer':'default'}" ${isOwner?'onclick="triggerAvatarUpload()"':''}>
              ${user.avatar 
                ? `<img src="${esc(optimizedImage(user.avatar, 256))}" style="width:120px;height:120px;border-radius:50%;object-fit:cover;border:3px solid var(--neon-pink);cursor:zoom-in" onclick="event.stopPropagation();viewAvatar('${esc(user.avatar)}')"/>`
                : `<div style="width:120px;height:120px;border-radius:50%;background:var(--purple-dark);display:flex;align-items:center;justify-content:center;font-size:3rem;font-weight:700;color:var(--neon-pink);border:3px solid var(--neon-pink)">${esc(user.username[0].toUpperCase())}</div>`
              }
              ${isOwner?`<div class="edit-badge">✎</div>`:''}
            </div>
            <div style="flex:1">
              <h2 style="font-size:2rem;margin-bottom:12px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
                <span ${isOwner?'style="cursor:pointer;border-bottom:1px dashed rgba(255,255,255,0.3)" onclick="triggerFieldEdit(\\\'username\\\')" title="Nhấp để sửa tên"':''}>${esc(user.username)}</span>
                ${badgeHtml}
              </h2>'''

new_profile_header = '''      $('app').innerHTML = `
        <div class="animate-in fade-in slide-in">
          <div style="background:var(--card-bg); border-radius:var(--radius-lg); padding:32px; margin-bottom:32px; display:flex; gap:32px; align-items:center; border:1px solid rgba(255,255,255,0.05); box-shadow:var(--shadow-lg); flex-wrap:wrap">
            <div style="position:relative; cursor:${isOwner?'pointer':'default'}; display:flex; flex-direction:column; align-items:center; gap:8px;" ${isOwner?'onclick="triggerAvatarUpload()"':''}>
              ${user.avatar 
                ? `<img src="${esc(optimizedImage(user.avatar, 256))}" style="width:120px;height:120px;border-radius:50%;object-fit:cover;border:3px solid ${pColor};cursor:zoom-in;box-shadow:0 0 15px ${pColor}" onclick="event.stopPropagation();viewAvatar('${esc(user.avatar)}')"/>`
                : `<div style="width:120px;height:120px;border-radius:50%;background:var(--bg-dark);display:flex;align-items:center;justify-content:center;font-size:3rem;font-weight:700;color:${pColor};border:3px solid ${pColor};box-shadow:0 0 15px ${pColor}">${esc(user.username[0].toUpperCase())}</div>`
              }
              ${isOwner?`<div class="edit-badge">✎</div>`:''}
              <div style="text-align:center; font-size:1.5rem;" title="${petName}">${petEmoji} <span style="font-size:0.8rem; color:var(--text-secondary); display:block;">Lv.${level}</span></div>
            </div>
            <div style="flex:1">
              <h2 style="font-size:2rem;margin-bottom:12px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
                <span ${isOwner?'style="cursor:pointer;border-bottom:1px dashed rgba(255,255,255,0.3)" onclick="triggerFieldEdit(\\\'username\\\')" title="Nhấp để sửa tên"':''}>${esc(user.username)}</span>
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
              </div>'''

js = js.replace(old_profile_header, new_profile_header)


# 3. Add Notifications to renderNav
old_nav = '''    if(currentUser) {
      el.innerHTML=`
        <a href="#/upload" class="btn btn-purple btn-sm">+ Đăng Record</a>
        <div class="user-menu" id="user-menu">'''

new_nav = '''    if(currentUser) {
      el.innerHTML=`
        <a href="#/upload" class="btn btn-purple btn-sm" style="display:none;" id="btn-upload">+ Đăng Record</a>
        <div class="nav-icon" style="position:relative;cursor:pointer;margin-right:16px;font-size:1.2rem;" onclick="toggleNotifications()">
          🔔
          <span id="notif-badge" style="display:none;position:absolute;top:-5px;right:-10px;background:var(--neon-pink);color:white;font-size:0.6rem;padding:2px 5px;border-radius:10px;font-weight:bold;">0</span>
          <div id="notif-dropdown" style="display:none;position:absolute;top:30px;right:-60px;width:300px;background:var(--card-bg);border:1px solid rgba(255,255,255,0.1);border-radius:8px;box-shadow:var(--shadow-lg);z-index:1000;max-height:400px;overflow-y:auto;padding:12px;font-size:0.9rem;">
            <div style="text-align:center;padding:10px;">Đang tải...</div>
          </div>
        </div>
        <div class="user-menu" id="user-menu">'''

js = js.replace(old_nav, new_nav)
js = js.replace('id="btn-upload"', '') # Fix my own mistake in new_nav

# 4. Add global variables for Notifications and the toggle function at the top (after INIT block)
notif_code = '''
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
'''

js = js + notif_code

# Also fix the `fetchUser` logic to load notifications initially
fetch_user_old = '''      if(r.ok) { currentUser = await r.json(); }'''
fetch_user_new = '''      if(r.ok) { currentUser = await r.json(); fetchNotifications(); }'''
js = js.replace(fetch_user_old, fetch_user_new)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
