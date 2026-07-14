import re
with open('temp.js', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Update Admin UI Add form
admin_form_old = """<div class="form-group"><label class="form-label">Giá trị (Metadata)</label><input class="form-input" id="s_meta" placeholder="#ff0000 hoặc URL khung"/></div>"""
admin_form_new = """<div class="form-group"><label class="form-label">Giá trị (Metadata)</label><input class="form-input" id="s_meta" placeholder="#ff0000 hoặc CSS box-shadow..."/></div>
                <div class="form-group"><label class="form-label">URL Icon (Tùy chọn)</label><input class="form-input" id="s_icon" placeholder="https://api.iconify..."/></div>"""
c = c.replace(admin_form_old, admin_form_new)

# 2. Update AdminAdd logic
admin_add_old = """          if(!n || !p || !t){toast('Vui lòng nhập đủ Tên, Giá, Loại','error');return;}
          await apiFetch('/shop/admin/items',{method:'POST',body:JSON.stringify({name:n, description:$('s_desc').value, price:parseInt(p), item_type:t, metadata_value:$('s_meta').value})});"""
admin_add_new = """          if(!n || !p || !t){toast('Vui lòng nhập đủ Tên, Giá, Loại','error');return;}
          let meta = $('s_meta').value;
          let icon = $('s_icon') ? $('s_icon').value : '';
          let finalMeta = JSON.stringify({value: meta, icon: icon});
          await apiFetch('/shop/admin/items',{method:'POST',body:JSON.stringify({name:n, description:$('s_desc').value, price:parseInt(p), item_type:t, metadata_value:finalMeta})});"""
c = c.replace(admin_add_old, admin_add_new)

# 3. Enhance shop item UI
shop_card_old = """          <div class="video-card shop-item" data-type="${item.item_type}">
            <div class="card-body" style="text-align:center; padding: 20px;">"""
shop_card_new = """          <div class="video-card shop-item" data-type="${item.item_type}" style="transition: transform 0.3s, box-shadow 0.3s; position:relative; overflow:hidden;">
            <div class="card-body" style="text-align:center; padding: 20px; position:relative; z-index:1;" onmouseenter="this.parentElement.style.transform='scale(1.05)'; this.parentElement.style.boxShadow='0 10px 20px rgba(0,0,0,0.5)'" onmouseleave="this.parentElement.style.transform='scale(1)'; this.parentElement.style.boxShadow='none'">
              <div style="position:absolute; top:-50%; left:-50%; width:200%; height:200%; background: radial-gradient(circle, ${item.item_type==='avatar_frame'?'rgba(138,43,226,0.1)':'rgba(255,255,255,0.05)'} 0%, transparent 70%); z-index:-1; pointer-events:none;"></div>"""
c = c.replace(shop_card_old, shop_card_new)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(c)
print("Patched temp.js for admin form and UI")
