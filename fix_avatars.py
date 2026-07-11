import re

with open('temp.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix board avatar
old_board = '<td><div style="display:flex;align-items:center;gap:10px"><span class="avatar avatar-sm">${esc(e.player.username[0].toUpperCase())}</span><span style="font-weight:600">${esc(e.player.username)}</span></div></td>'
new_board = '<td><div style="display:flex;align-items:center;gap:10px;${e.player.avatar ? \'cursor:pointer;\' : \'\'}" ${e.player.avatar ? `onclick="viewAvatar(\'${esc(optimizedImage(e.player.avatar, 600))}\')"` : \'\'}>${e.player.avatar ? `<img src="${esc(optimizedImage(e.player.avatar, 40))}" class="avatar avatar-sm" style="object-fit:cover" />` : `<span class="avatar avatar-sm">${esc(e.player.username[0].toUpperCase())}</span>`}<span style="font-weight:600">${esc(e.player.username)}</span></div></td>'

if old_board in content:
    content = content.replace(old_board, new_board)
else:
    print("Warning: old_board not found")

# Fix video detail avatar
old_video = '<span class="avatar avatar-md" style="box-shadow:var(--neon-glow-purple); border:1px solid var(--neon-purple);">${esc(video.user?.username[0].toUpperCase())}</span>'
new_video = '${video.user?.avatar ? `<img src="${esc(optimizedImage(video.user.avatar, 80))}" class="avatar avatar-md" style="object-fit:cover; box-shadow:var(--neon-glow-purple); border:1px solid var(--neon-purple); cursor:pointer;" onclick="viewAvatar(\'${esc(optimizedImage(video.user.avatar, 600))}\')" />` : `<span class="avatar avatar-md" style="box-shadow:var(--neon-glow-purple); border:1px solid var(--neon-purple);">${esc(video.user?.username[0].toUpperCase())}</span>`}'

if old_video in content:
    content = content.replace(old_video, new_video)
else:
    print("Warning: old_video not found")

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Finished replacing avatars")
