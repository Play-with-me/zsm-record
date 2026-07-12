import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Add "Vật phẩm" tab button
tab_btn = '''<button class="tab-btn${tab==='tournaments'?' active':''}" onclick="adminTab('tournaments')">Giải đấu</button>
          <button class="tab-btn${tab==='shop'?' active':''}" onclick="adminTab('shop')">Vật phẩm (${shopItems.length})</button>'''
js = js.replace('''<button class="tab-btn${tab==='tournaments'?' active':''}" onclick="adminTab('tournaments')">Giải đấu</button>''', tab_btn)

# 2. Add "shop" tab content
shop_content = '''tab==='shop'?`
          <div class="card"><div class="card-body">
            <div style="font-size:0.85rem;font-weight:700;margin-bottom:10px">Thêm Vật phẩm mới</div>
            <div class="admin-add-form" style="display:flex;flex-direction:column;gap:12px;">
              <div class="form-group"><label class="form-label">Tên *</label><input class="form-input" id="s_name" placeholder="VD: Khung rồng"/></div>
              <div class="form-group"><label class="form-label">Mô tả</label><input class="form-input" id="s_desc" placeholder="Hiệu ứng rồng bao quanh"/></div>
              <div style="display:flex;gap:12px;">
                <div class="form-group" style="flex:1"><label class="form-label">Giá (Z-Coins) *</label><input class="form-input" type="number" id="s_price" value="100"/></div>
                <div class="form-group" style="flex:1"><label class="form-label">Loại (type) *</label><select class="form-select" id="s_type">
                  <option value="name_color">name_color</option>
                  <option value="avatar_frame">avatar_frame</option>
                  <option value="badge">badge</option>
                </select></div>
              </div>
              <div class="form-group"><label class="form-label">Giá trị (Metadata)</label><input class="form-input" id="s_meta" placeholder="#ff0000 hoặc URL khung"/></div>
              <button class="btn btn-primary btn-sm" onclick="adminAdd('shopItem')">+ Thêm Vật Phẩm</button>
            </div>
          </div></div>
          <div class="card" style="overflow:hidden"><table class="data-table"><thead><tr><th>Tên</th><th>Loại</th><th>Giá</th><th>Mã ID</th><th>Hành động</th></tr></thead>
          <tbody>${shopItems.map(s=>`<tr><td style="font-weight:600">${esc(s.name)}</td><td><span class="badge badge-purple">${esc(s.item_type)}</span></td><td>🪙 ${s.price}</td><td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${s.id}</td><td><button class="btn btn-danger btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminDelete('shopItem','${s.id}','${esc(s.name).replace(/'/g, "\\'")}')">🗑️</button></td></tr>`).join('')}</tbody>
          </table></div>
        `:'''

js = js.replace("tab==='tournaments'?`", shop_content + "\n        tab==='tournaments'?`")

# 3. Add to adminAdd
add_logic = '''else if(type==='shopItem'){
        const n=$('s_name').value;
        const p=$('s_price').value;
        const t=$('s_type').value;
        if(!n || !p || !t){toast('Vui lòng nhập đủ Tên, Giá, Loại','error');return;}
        await apiFetch('/shop/admin/items',{method:'POST',body:JSON.stringify({name:n, description:$('s_desc').value, price:parseInt(p), item_type:t, metadata_value:$('s_meta').value})});
      } else'''

js = js.replace("} else {", add_logic + " {", 1) # Only replace the first occurrence (which should be the pet one)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
