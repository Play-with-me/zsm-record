import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_profile = '''      // Calculate cooldowns
      let avatarWait = '', nameWait = '';
      if (isOwner) {
        const now = new Date();'''

new_profile = '''      let badgeHtml = '';
      if (user.role === 'ADMIN') badgeHtml = `<span class="badge-label badge-boss" title="Quản trị viên">Boss</span>`;
      else if (videos.length >= 15) badgeHtml = `<span class="badge-label badge-monster" title="Trên 15 kỷ lục">Quái Vật Drift</span>`;
      else if (videos.length >= 5) badgeHtml = `<span class="badge-label badge-pro" title="Trên 5 kỷ lục">Racer Chuyên Nghiệp</span>`;
      else badgeHtml = `<span class="badge-label badge-rookie" title="Dưới 5 kỷ lục">Tân Binh</span>`;

      // Calculate cooldowns
      let avatarWait = '', nameWait = '';
      if (isOwner) {
        const now = new Date();'''

js = js.replace(old_profile, new_profile)

old_profile_render = '''          <div class="profile-info">
            <h2 style="display:flex;align-items:center;gap:10px;">
              ${esc(user.username)}
              ${isOwner ? `<button onclick="editProfile('username')" class="btn" style="background:none;border:none;color:var(--text-muted);cursor:pointer;" title="Đổi tên ${nameWait}">&#9998;</button>` : ''}
            </h2>'''

new_profile_render = '''          <div class="profile-info">
            <h2 style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
              ${esc(user.username)} ${badgeHtml}
              ${isOwner ? `<button onclick="editProfile('username')" class="btn" style="background:none;border:none;color:var(--text-muted);cursor:pointer;" title="Đổi tên ${nameWait}">&#9998;</button>` : ''}
            </h2>'''

js = js.replace(old_profile_render, new_profile_render)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
