import re

with open('temp.js', 'r', encoding='utf-8') as f:
    content = f.read()

# exact old block to replace
old_block = """        <div style="position:relative; display:inline-block;">
          ${user.avatar 
            ? `<img src="${esc(optimizedImage(user.avatar, 160))}" class="avatar avatar-lg" width="80" height="80" loading="eager" decoding="async" style="object-fit:cover; border:2px solid var(--border);" />`
            : `<span class="avatar avatar-lg">${esc(user.username[0].toUpperCase())}</span>`
          }
          ${isOwner ? `<button id="avatar-edit-btn" onclick="editProfile('avatar')" class="btn btn-sm" style="position:absolute;bottom:-10px;left:50%;transform:translateX(-50%);background:var(--bg-card);border:1px solid var(--border);font-size:0.7rem;padding:4px 8px;white-space:nowrap;">Đổi ảnh ${avatarWait}</button>` : ''}
        </div>"""

new_block = """        <div style="position:relative; display:inline-block;" ${user.avatar ? `cursor:pointer;" onclick="viewAvatar('${esc(optimizedImage(user.avatar, 1200))}')` : '"'}>
          ${user.avatar 
            ? `<img src="${esc(optimizedImage(user.avatar, 160))}" class="avatar avatar-lg" width="80" height="80" loading="eager" decoding="async" style="object-fit:cover; border:2px solid var(--border);" />`
            : `<span class="avatar avatar-lg">${esc(user.username[0].toUpperCase())}</span>`
          }
          ${isOwner ? `<button id="avatar-edit-btn" onclick="event.stopPropagation(); editProfile('avatar')" class="btn btn-sm" style="position:absolute;bottom:-10px;left:50%;transform:translateX(-50%);background:var(--bg-card);border:1px solid var(--border);font-size:0.7rem;padding:4px 8px;white-space:nowrap;">Đổi ảnh ${avatarWait}</button>` : ''}
        </div>"""

if old_block in content:
    content = content.replace(old_block, new_block)
else:
    print('Failed to find old block in temp.js')

view_avatar_fn = """
window.viewAvatar = function(url) {
  if(!url) return;
  const overlay = document.createElement('div');
  overlay.className = 'quick-view-overlay active';
  overlay.style.zIndex = '10000';
  overlay.innerHTML = `
    <span class="btn-close-modal" style="position:fixed; top:20px; right:20px; font-size:2.5rem; color:#fff; cursor:pointer;" onclick="this.parentElement.remove()">&times;</span>
    <img src="${url}" style="max-width:90vw; max-height:90vh; object-fit:contain; border-radius:8px; box-shadow:0 0 40px rgba(0,0,0,0.8);" />
  `;
  overlay.onclick = (e) => {
    if(e.target === overlay) overlay.remove();
  };
  document.body.appendChild(overlay);
}
"""
if 'window.viewAvatar =' not in content:
    content += view_avatar_fn

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated temp.js')
