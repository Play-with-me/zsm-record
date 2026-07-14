import re

with open('temp.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update renderProfile logic
profile_target = """    let badgeHtml = '';
    if (user.role === 'ADMIN') badgeHtml = `<span class="badge-label badge-boss" title="Quản trị viên">Boss</span>`;
    else if (publicVideos.length >= 15) badgeHtml = `<span class="badge-label badge-monster" title="Trên 15 kỷ lục">Quái Vật Drift</span>`;
    else if (publicVideos.length >= 5) badgeHtml = `<span class="badge-label badge-pro" title="Trên 5 kỷ lục">Racer Chuyên Nghiệp</span>`;
    else badgeHtml = `<span class="badge-label badge-rookie" title="Dưới 5 kỷ lục">Tân Binh</span>`;"""

profile_replacement = """    let badgeHtml = '';
    let frameOverlayHtml = '';
    let nameColorStyle = '';
    
    // Process equipped items
    if (user.items && user.items.length > 0) {
        const equipped = user.items.filter(i => i.is_equipped);
        equipped.forEach(eq => {
            let meta = eq.item.metadata_value;
            let iconUrl = '';
            try {
                const p = JSON.parse(meta);
                meta = p.value || p.css || '';
                iconUrl = p.icon || '';
            } catch(e) {}
            
            if (eq.item.item_type === 'name_color') {
                nameColorStyle = `color:${meta}; text-shadow: 0 0 10px ${meta};`;
            } else if (eq.item.item_type === 'avatar_frame') {
                if(iconUrl) {
                    frameOverlayHtml = `<img src="${iconUrl}" style="position:absolute; top:-20px; left:-20px; width:140px; height:140px; pointer-events:none; object-fit:contain; image-rendering:pixelated;" />`;
                }
            } else if (eq.item.item_type === 'badge') {
                if(iconUrl) {
                    badgeHtml += `<span class="badge-label" style="background:none; box-shadow:none; padding:0; display:inline-flex; align-items:center; justify-content:center; margin-left: 5px;" title="${esc(eq.item.name)}"><img src="${iconUrl}" style="height:35px; width:auto; image-rendering:pixelated; object-fit:contain;" onerror="this.style.display='none'"/></span>`;
                }
            }
        });
    }

    if (!badgeHtml) {
        if (user.role === 'ADMIN') badgeHtml = `<span class="badge-label badge-boss" title="Quản trị viên">Boss</span>`;
        else if (publicVideos.length >= 15) badgeHtml = `<span class="badge-label badge-monster" title="Trên 15 kỷ lục">Quái Vật Drift</span>`;
        else if (publicVideos.length >= 5) badgeHtml = `<span class="badge-label badge-pro" title="Trên 5 kỷ lục">Racer Chuyên Nghiệp</span>`;
        else badgeHtml = `<span class="badge-label badge-rookie" title="Dưới 5 kỷ lục">Tân Binh</span>`;
    }
"""

content = content.replace(profile_target, profile_replacement)

# Update avatar in renderProfile
avatar_target = """        <div style="position:relative; display:flex; flex-direction:column; align-items:center; gap:8px;${user.avatar ? ' cursor:pointer;' : ''}" ${user.avatar ? `onclick="viewAvatar('${esc(optimizedImage(user.avatar, 1200))}')"` : ''}>
          ${user.avatar 
            ? `<img src="${esc(optimizedImage(user.avatar, 160))}" class="avatar avatar-lg" width="100" height="100" loading="eager" decoding="async" style="object-fit:cover; border:3px solid ${pColor}; box-shadow:0 0 15px ${pColor};" />`
            : `<div style="width:100px;height:100px;border-radius:50%;background:var(--bg-dark);display:flex;align-items:center;justify-content:center;font-size:3rem;font-weight:700;color:${pColor};border:3px solid ${pColor};box-shadow:0 0 15px ${pColor}">${esc(user.username[0].toUpperCase())}</div>`
          }"""

avatar_replacement = """        <div style="position:relative; display:flex; flex-direction:column; align-items:center; gap:8px;${user.avatar ? ' cursor:pointer;' : ''}" ${user.avatar ? `onclick="viewAvatar('${esc(optimizedImage(user.avatar, 1200))}')"` : ''}>
          <div style="position:relative; width:100px; height:100px;">
            ${user.avatar 
              ? `<img src="${esc(optimizedImage(user.avatar, 160))}" class="avatar avatar-lg" width="100" height="100" loading="eager" decoding="async" style="object-fit:cover; border:3px solid ${pColor}; box-shadow:0 0 15px ${pColor}; margin:0; position:absolute; top:0; left:0;" />`
              : `<div style="width:100px;height:100px;border-radius:50%;background:var(--bg-dark);display:flex;align-items:center;justify-content:center;font-size:3rem;font-weight:700;color:${pColor};border:3px solid ${pColor};box-shadow:0 0 15px ${pColor}; margin:0; position:absolute; top:0; left:0;">${esc(user.username[0].toUpperCase())}</div>`
            }
            ${frameOverlayHtml}
          </div>"""

content = content.replace(avatar_target, avatar_replacement)

# Update username color in renderProfile
username_target = """<span ${isOwner ? `style="cursor:pointer;border-bottom:1px dashed rgba(255,255,255,0.3)" onclick="triggerFieldEdit('username')"` : ''} title="Nhấp để đổi tên ${nameWait}">${esc(user.username)}</span>"""
username_replacement = """<span ${isOwner ? `style="cursor:pointer;border-bottom:1px dashed rgba(255,255,255,0.3); ${nameColorStyle}" onclick="triggerFieldEdit('username')"` : `style="${nameColorStyle}"`} title="Nhấp để đổi tên ${nameWait}">${esc(user.username)}</span>"""

# If the exact match doesn't work, we'll try a regex replacement
import re
content = re.sub(r'<span \$\{isOwner \? `style="cursor:pointer;border-bottom:1px dashed rgba\(255,255,255,0\.3\)" onclick="triggerFieldEdit\(\'username\'\)"` : \'\'\} title="Nhấp để đổi tên \$\{nameWait\}">\$\{esc\(user\.username\)\}</span>', 
                 r'<span ${isOwner ? `style="cursor:pointer;border-bottom:1px dashed rgba(255,255,255,0.3); ${nameColorStyle}" onclick="triggerFieldEdit(\'username\')"` : `style="${nameColorStyle}"`} title="Nhấp để đổi tên ${nameWait}">${esc(user.username)}</span>', 
                 content)

# Update renderNav logic
nav_target_regex = r'\$\{currentUser\.avatar\s*\?\s*`<img src="\$\{esc\(optimizedImage\(currentUser\.avatar, 64\)\)\}" class="avatar avatar-sm" loading="eager" decoding="async" style="object-fit:cover;"/>`\s*:\s*`<span class="avatar avatar-sm">\$\{esc\(currentUser\.username\[0\]\.toUpperCase\(\)\)\}</span>`\s*\}\s*<span class="uname">\$\{esc\(currentUser\.username\)\}</span>'

nav_replacement = """${(() => {
            let frameUrl = '';
            let nameColor = '';
            if(currentUser.items) {
                const eqFrames = currentUser.items.filter(i => i.is_equipped && i.item.item_type === 'avatar_frame');
                if(eqFrames.length > 0) {
                    try { const p = JSON.parse(eqFrames[0].item.metadata_value); frameUrl = p.icon || ''; } catch(e){}
                }
                const eqColors = currentUser.items.filter(i => i.is_equipped && i.item.item_type === 'name_color');
                if(eqColors.length > 0) {
                    try { const p = JSON.parse(eqColors[0].item.metadata_value); nameColor = p.value || p.css || ''; } catch(e){}
                }
            }
            let avHtml = `<div style="position:relative; display:inline-block; width:32px; height:32px; margin-right:8px;">`;
            avHtml += currentUser.avatar 
              ? `<img src="${esc(optimizedImage(currentUser.avatar, 64))}" class="avatar avatar-sm" loading="eager" decoding="async" style="object-fit:cover; width:100%; height:100%; margin:0; position:absolute; top:0; left:0;"/>`
              : `<span class="avatar avatar-sm" style="width:100%; height:100%; margin:0; position:absolute; top:0; left:0; display:flex; align-items:center; justify-content:center;">${esc(currentUser.username[0].toUpperCase())}</span>`;
            
            if (frameUrl) avHtml += `<img src="${frameUrl}" style="position:absolute; top:-6px; left:-6px; width:44px; height:44px; pointer-events:none; object-fit:contain; image-rendering:pixelated;" />`;
            avHtml += `</div><span class="uname" style="${nameColor ? 'color:'+nameColor+'; text-shadow:0 0 8px '+nameColor+';' : ''}">${esc(currentUser.username)}</span>`;
            return avHtml;
          })()}"""

content = re.sub(nav_target_regex, nav_replacement, content)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("temp.js patched with gamification visual items!")
