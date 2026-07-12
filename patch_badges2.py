import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add badge logic
badge_code = '''
    let badgeHtml = '';
    if (user.role === 'ADMIN') badgeHtml = `<span class="badge-label badge-boss" title="Quản trị viên">Boss</span>`;
    else if (publicVideos.length >= 15) badgeHtml = `<span class="badge-label badge-monster" title="Trên 15 kỷ lục">Quái Vật Drift</span>`;
    else if (publicVideos.length >= 5) badgeHtml = `<span class="badge-label badge-pro" title="Trên 5 kỷ lục">Racer Chuyên Nghiệp</span>`;
    else badgeHtml = `<span class="badge-label badge-rookie" title="Dưới 5 kỷ lục">Tân Binh</span>`;
'''

if 'badge-rookie' not in js:
    js = js.replace(
        '// Calculate cooldowns',
        badge_code + '\n    // Calculate cooldowns'
    )

# Render badge
render_header_old = '''          <h2 style="display:flex;align-items:center;gap:10px;">
            ${esc(user.username)}
            ${isOwner ? `<button onclick="editProfile('username')"`'''
render_header_new = '''          <h2 style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
            ${esc(user.username)} ${badgeHtml}
            ${isOwner ? `<button onclick="editProfile('username')"`'''

if 'badgeHtml' in js and '${badgeHtml}' not in js:
    js = js.replace(render_header_old, render_header_new)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
