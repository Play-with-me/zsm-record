import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Find the injected bad text from line 1076 to 1104
bad_text = r"""      // Thêm phần Túi đồ vào Profile
      let inventoryHtml = '';
      if(user.id === (currentUser && currentUser.id)) {
        try {
          const inv = await apiFetch('/shop/my-items');
          if(inv && inv.length > 0) {
            inventoryHtml = `<div class="card" style="margin-top: 20px;">
              <h3 style="margin-bottom: 10px;">Túi Đồ Của Tôi 🎒</h3>
              <div class="video-grid" style="--cols:4">`;
              
            inv.forEach(ui => {
              const item = ui.item;
              let style = '';
              if(item.item_type === 'name_color') {
                style = `color: ${item.metadata_value}; font-weight:bold;`;
              } else if(item.item_type === 'avatar_frame') {
                style = `border: ${item.metadata_value}; border-radius:50%; width: 48px; height: 48px; display:inline-block; margin-bottom:10px;`;
              }
              
              inventoryHtml += `
                <div class="video-card" style="padding: 15px; text-align: center; ${ui.is_equipped ? 'border: 2px solid var(--primary);' : ''}">
                  <div style="${style}">${item.item_type === 'avatar_frame' ? '' : 'A'}</div>
                  <div style="font-weight:bold; margin-top:5px; font-size:0.9rem; ${item.item_type === 'name_color' ? style : ''}">${esc(item.name)}</div>
                  <button class="btn btn-sm ${ui.is_equipped ? 'btn-outline' : 'btn-primary'}" style="margin-top:10px;" onclick="equipShopItem('${ui.id}')">
                    ${ui.is_equipped ? 'Tháo ra' : 'Trang bị'}
                  </button>
                </div>
              `;
            });
            
            inventoryHtml += `</div></div>`;
          }
        } catch(e) { console.error(e); }
      }
      ${inventoryHtml}"""

if bad_text in js:
    js = js.replace(bad_text, "")
else:
    print("Could not find exact bad text, attempting fallback")
    # Let's use regex to remove it
    js = re.sub(r'      // Thêm phần Túi đồ vào Profile.*?      \$\{inventoryHtml\}', '', js, flags=re.DOTALL)

# Now, we need to inject the logic BEFORE `$('app').innerHTML = `
# and then inject `${inventoryHtml}` inside the template right before `<div class="video-grid">`
# Let's find the correct spot for logic.
logic = r"""
      let inventoryHtml = '';
      if(user.id === (currentUser && currentUser.id)) {
        try {
          const inv = await apiFetch('/shop/my-items');
          if(inv && inv.length > 0) {
            inventoryHtml = `<div class="card" style="margin-top: 20px; padding: 20px;">
              <h3 style="margin-bottom: 15px; font-size: 1rem; color: var(--neon-cyan); text-shadow: var(--neon-glow-cyan);">Túi Đồ Của Tôi 🎒</h3>
              <div class="video-grid" style="--cols:4">`;
              
            inv.forEach(ui => {
              const item = ui.item;
              let style = '';
              if(item.item_type === 'name_color') {
                style = `color: ${item.metadata_value}; font-weight:bold;`;
              } else if(item.item_type === 'avatar_frame') {
                style = `border: ${item.metadata_value}; border-radius:50%; width: 48px; height: 48px; display:inline-block; margin-bottom:10px;`;
              }
              
              inventoryHtml += `
                <div class="video-card" style="padding: 15px; text-align: center; ${ui.is_equipped ? 'border: 2px solid var(--primary);' : ''}">
                  <div style="${style}">${item.item_type === 'avatar_frame' ? '' : 'A'}</div>
                  <div style="font-weight:bold; margin-top:5px; font-size:0.9rem; ${item.item_type === 'name_color' ? style : ''}">${esc(item.name)}</div>
                  <button class="btn btn-sm ${ui.is_equipped ? 'btn-outline' : 'btn-primary'}" style="margin-top:10px;" onclick="equipShopItem('${ui.id}')">
                    ${ui.is_equipped ? 'Tháo ra' : 'Trang bị'}
                  </button>
                </div>
              `;
            });
            
            inventoryHtml += `</div></div>`;
          }
        } catch(e) { console.error(e); }
      }
"""

inner_html_target = r"      const uStyles = getUserStyles(user);"
if inner_html_target in js:
    js = js.replace(inner_html_target, logic + "\n" + inner_html_target)
    
    # inject `${inventoryHtml}` before `Tất Cả Record`
    target2 = r"""<div class="section-header" style="margin-top:20px;"><h2>Tất Cả Record</h2></div>"""
    if target2 in js:
        js = js.replace(target2, "${inventoryHtml}\n\n      " + target2)
    else:
        print("Could not find target2")

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("done")
