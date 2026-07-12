import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

helper = r"""
function getUserStyles(u) {
  let nameStyle = '';
  let avatarStyle = '';
  if(u.items && u.items.length > 0) {
    u.items.forEach(ui => {
      if(ui.is_equipped && ui.item) {
        if(ui.item.item_type === 'name_color') nameStyle = `color: ${ui.item.metadata_value}; font-weight:bold; text-shadow: 0 0 5px ${ui.item.metadata_value}40;`;
        if(ui.item.item_type === 'avatar_frame') avatarStyle = `border: ${ui.item.metadata_value};`;
      }
    });
  }
  return { nameStyle, avatarStyle };
}
"""

if "function getUserStyles" not in js:
    js = js.replace("function parseRecord(str) {", helper + "\nfunction parseRecord(str) {")

if "const uStyles = getUserStyles(user);" not in js:
    p_header_idx = js.find('const pColor =')
    if p_header_idx != -1:
        insert = "\n      const uStyles = getUserStyles(user);\n"
        js = js[:p_header_idx] + insert + js[p_header_idx:]
        
        js = js.replace(
            'style="object-fit:cover; border:3px solid ${pColor}; box-shadow:0 0 15px ${pColor};"',
            'style="object-fit:cover; border:3px solid ${pColor}; box-shadow:0 0 15px ${pColor}; ${uStyles.avatarStyle}"'
        )
        js = js.replace(
            '<h2 style="margin:0">${esc(user.username)}',
            '<h2 style="margin:0; ${uStyles.nameStyle}">${esc(user.username)}'
        )

if "const uStyles = getUserStyles(r.player);" not in js:
    target = 'return `<div class="board-row"'
    replacement = 'const uStyles = getUserStyles(r.player);\n      return `<div class="board-row"'
    js = js.replace(target, replacement)
    
    js = js.replace(
        '<span class="uname" style="font-weight:bold">${esc(r.player.username)}</span>',
        '<span class="uname" style="font-weight:bold; ${uStyles.nameStyle}">${esc(r.player.username)}</span>'
    )
    js = js.replace(
        '<img src="${esc(optimizedImage(r.player.avatar, 64))}" class="avatar avatar-sm" loading="lazy" decoding="async" />',
        '<img src="${esc(optimizedImage(r.player.avatar, 64))}" class="avatar avatar-sm" loading="lazy" decoding="async" style="${uStyles.avatarStyle}" />'
    )

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("done")
