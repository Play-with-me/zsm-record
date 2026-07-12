import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

inventory_logic = r"""
      // Thêm phần Túi đồ vào Profile
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
"""

if "Túi Đồ Của Tôi" not in js:
    # insert before <div class="video-grid">
    target_split = r'      <div class="video-grid">'
    if target_split in js:
        parts = js.split(target_split)
        js = parts[0] + inventory_logic + "\n      " + "${inventoryHtml}\n" + target_split + parts[1]
        
        with open('temp.js', 'w', encoding='utf-8') as f:
            f.write(js)
        print("Patched inventory UI")
    else:
        print("Target split not found")
else:
    print("Already patched")
