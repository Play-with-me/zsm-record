import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update Promise.all in renderTab to fetch shop items
promise_target = r"const [maps,cars,pets,users]=await Promise.all([cachedApiFetch('/maps', 300000),cachedApiFetch('/cars', 300000),cachedApiFetch('/pets', 300000),apiFetch('/users')]);"
promise_replacement = r"const [maps,cars,pets,users,shopItems]=await Promise.all([cachedApiFetch('/maps', 300000),cachedApiFetch('/cars', 300000),cachedApiFetch('/pets', 300000),apiFetch('/users'),apiFetch('/shop/items')]);"
js = js.replace(promise_target, promise_replacement)

# 2. Add Tab button
tab_target = r"""<button class="tab-btn${tab==='tournaments'?' active':''}" onclick="adminTab('tournaments')">Giải Đấu</button>"""
tab_replacement = tab_target + r"""
          <button class="tab-btn${tab==='shop'?' active':''}" onclick="adminTab('shop')">Shop (${shopItems.length})</button>"""
js = js.replace(tab_target, tab_replacement)

# 3. Add tab==='shop' logic
# We need to find the end of tournaments block.
# Usually it ends with a template literal interpolation.
shop_html = r"""
        tab==='shop'?`
          <div class="card"><div class="card-body">
            <div style="font-size:0.85rem;font-weight:700;margin-bottom:10px">Thêm Vật Phẩm Cửa Hàng</div>
            <div class="admin-add-form" style="grid-template-columns: 1fr 1fr 1fr 1fr 1fr auto;">
              <div class="form-group"><input class="form-input" id="s_name" placeholder="Tên (VD: Màu Đỏ)"/></div>
              <div class="form-group"><input class="form-input" id="s_desc" placeholder="Mô tả"/></div>
              <div class="form-group"><input class="form-input" id="s_price" type="number" placeholder="Giá (Z-Coins)"/></div>
              <div class="form-group">
                <select class="form-input" id="s_type">
                  <option value="name_color">Màu Tên (name_color)</option>
                  <option value="avatar_frame">Viền Avatar (avatar_frame)</option>
                </select>
              </div>
              <div class="form-group"><input class="form-input" id="s_meta" placeholder="Giá trị (Mã màu/CSS)"/></div>
              <button class="btn btn-primary" onclick="adminAddShopItem()">Thêm</button>
            </div>
          </div></div>
          <div class="card"><div class="card-body" style="overflow-x:auto"><table class="admin-table">
          <thead><tr><th>ID</th><th>Tên</th><th>Loại</th><th>Giá</th><th>Giá trị</th><th>Thao tác</th></tr></thead>
          <tbody>${shopItems.map(i=>`<tr>
            <td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${i.id.substring(0,8)}...</td>
            <td>${esc(i.name)}</td>
            <td>${esc(i.item_type)}</td>
            <td>${i.price} 🪙</td>
            <td><code>${esc(i.metadata_value)}</code></td>
            <td style="display:flex;gap:4px;"><button class="btn btn-sm btn-outline" onclick="adminEditShopItem('${i.id}', '${esc(i.name)}', '${esc(i.description)}', ${i.price}, '${esc(i.item_type)}', '${esc(i.metadata_value).replace(/'/g, "\\'")}')">Sửa</button> <button class="btn btn-danger btn-sm" onclick="adminDelete('shopItem','${i.id}','${esc(i.name).replace(/'/g, "\\'")}')">Xóa</button></td>
          </tr>`).join('')}</tbody>
          </table></div></div>`:
"""

# Let's insert before `          tab==='users'?`
users_target = r"          tab==='users'?`"
js = js.replace(users_target, shop_html + users_target)

# 4. Add window.adminAddShopItem, window.adminEditShopItem, and update doAdminDelete
script_additions = r"""
  window.adminAddShopItem = async function() {
    const name = $('s_name').value.trim(), desc = $('s_desc').value.trim(), price = parseInt($('s_price').value), type = $('s_type').value, meta = $('s_meta').value.trim();
    if(!name || isNaN(price) || !meta) return toast('Vui lòng điền đủ Tên, Giá, Giá trị', 'error');
    try {
      await apiFetch('/shop/admin/items', {method:'POST', body:JSON.stringify({name, description: desc, price, item_type: type, metadata_value: meta})});
      toast('Thêm vật phẩm thành công!'); clearApiCache(); renderTab();
    } catch(e) { toast(e.message, 'error'); }
  };

  window.adminEditShopItem = function(id, name, desc, price, type, meta) {
    const overlay = document.createElement('div');
    overlay.className='modal-overlay';
    overlay.innerHTML=`<div class="modal">
      <h3>Sửa Vật Phẩm</h3>
      <form id="esf" style="display:flex;flex-direction:column;gap:14px;">
        <div class="form-group"><label class="form-label">Tên</label><input class="form-input" name="name" value="${name}" required/></div>
        <div class="form-group"><label class="form-label">Mô tả</label><input class="form-input" name="desc" value="${desc}"/></div>
        <div class="form-group"><label class="form-label">Giá</label><input class="form-input" type="number" name="price" value="${price}" required/></div>
        <div class="form-group"><label class="form-label">Loại</label>
          <select class="form-input" name="type">
            <option value="name_color" ${type==='name_color'?'selected':''}>Màu Tên</option>
            <option value="avatar_frame" ${type==='avatar_frame'?'selected':''}>Viền Avatar</option>
          </select>
        </div>
        <div class="form-group"><label class="form-label">Giá trị</label><input class="form-input" name="meta" value="${meta}" required/></div>
        <div class="modal-actions" style="margin-top:10px">
          <button type="button" class="btn btn-outline btn-sm" onclick="this.closest('.modal-overlay').remove()">Hủy</button>
          <button type="submit" class="btn btn-primary btn-sm">Lưu</button>
        </div>
      </form>
    </div>`;
    document.body.appendChild(overlay);
    $('esf').onsubmit=async e=>{
      e.preventDefault();
      try {
        await apiFetch(`/shop/admin/items/${id}`, {method:'PUT', body:JSON.stringify({
          name: e.target.name.value, description: e.target.desc.value, price: parseInt(e.target.price.value), item_type: e.target.type.value, metadata_value: e.target.meta.value
        })});
        overlay.remove(); toast('Đã cập nhật!'); clearApiCache(); window.adminTab('shop');
      } catch(err){ toast(err.message, 'error'); }
    };
  };
"""

# Let's insert before `  window.editRecord = async function(id) {`
edit_target = r"  window.editRecord = async function(id) {"
js = js.replace(edit_target, script_additions + "\n" + edit_target)

# We need to update doAdminDelete to handle 'shopItem'
delete_target = r"if(type==='user') await apiFetch(`/users/${id}/admin`,{method:'DELETE'});"
delete_replacement = delete_target + r"\n      else if(type==='shopItem') await apiFetch(`/shop/admin/items/${id}`,{method:'DELETE'});"
js = js.replace(delete_target, delete_replacement)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("done")
