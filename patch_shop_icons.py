import re

with open('temp.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the item iteration block
old_block = """        items.forEach(item => {
          let style = '';
          if(item.item_type === 'name_color') {
            style = `color: ${item.metadata_value}; font-weight:bold;`;
          } else if(item.item_type === 'avatar_frame') {
            style = `border: ${item.metadata_value}; border-radius:50%; width: 48px; height: 48px; display:inline-block; margin-bottom:10px;`;
          }
          
          html += `
          <div class="video-card">
            <div class="card-body" style="text-align:center; padding: 20px;">
              <div style="${style}">${item.item_type === 'avatar_frame' ? '' : 'A'}</div>
              <h3 style="margin-top:10px; ${item.item_type === 'name_color' ? style : ''}">${esc(item.name)}</h3>"""

new_block = """        items.forEach(item => {
          let style = '';
          let metaVal = item.metadata_value;
          let iconUrl = '';
          try {
            const m = JSON.parse(item.metadata_value);
            metaVal = m.value;
            iconUrl = m.icon;
          } catch(e) {}

          if(item.item_type === 'name_color') {
            style = `color: ${metaVal}; font-weight:bold;`;
          } else if(item.item_type === 'avatar_frame') {
            style = `box-shadow: ${metaVal}; border-radius:50%; width: 48px; height: 48px; display:inline-flex; align-items:center; justify-content:center; margin-bottom:10px;`;
          }
          
          html += `
          <div class="video-card" data-type="${item.item_type}">
            <div class="card-body" style="text-align:center; padding: 20px;">
              <div style="${style}">${iconUrl ? `<img src="${iconUrl}" style="width:100%;height:100%;object-fit:contain;border-radius:50%"/>` : (item.item_type === 'avatar_frame' ? '' : 'A')}</div>
              <h3 style="margin-top:10px; ${item.item_type === 'name_color' ? style : ''}">${esc(item.name)}</h3>"""

if old_block in content:
    content = content.replace(old_block, new_block)
else:
    print("Old block not found!")

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(content)
