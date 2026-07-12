import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update renderNav to show coins and add Shop tab
# Find the nav links to add Shop
nav_links_target = r'<a href="#/tournaments" class="nav-link" data-route="/tournaments">Giải Đấu 🏆</a>'
if nav_links_target in js:
    js = js.replace(nav_links_target, nav_links_target + '\n          <a href="#/shop" class="nav-link" data-route="/shop">Cửa Hàng 🛒</a>')

# Update user menu to show coins
user_trigger_target = r'<span class="uname">${esc(currentUser.username)}</span>'
if user_trigger_target in js:
    js = js.replace(user_trigger_target, r'<span class="uname">${esc(currentUser.username)}</span> <span class="badge badge-orange" style="margin-left:8px;">🪙 ${currentUser.coins || 0}</span>')

# 2. Add /shop route to the router
router_target = r"'/admin': renderAdmin"
if router_target in js:
    js = js.replace(router_target, r"'/admin': renderAdmin," + "\n    " + r"'/shop': renderShop")

# 3. Add renderShop function
shop_function = r"""
async function renderShop() {
  $('app').innerHTML = `<div class="animate-in"><div class="skeleton" style="height:100px;border-radius:var(--radius-lg);margin-bottom:24px"></div><div class="video-grid">${skCards(4)}</div></div>`;
  try {
    const items = await apiFetch('/shop/items');
    
    let html = `<div class="page-header animate-in">
      <h1>Cửa Hàng 🛒</h1>
      <p>Dùng Z-Coins 🪙 của bạn để mua vật phẩm trang trí hồ sơ.</p>
    </div>`;
    
    if(!items || items.length === 0) {
      html += `<div class="empty animate-in">Chưa có vật phẩm nào được bày bán.</div>`;
    } else {
      html += `<div class="video-grid animate-in" style="--cols:4">`;
      items.forEach(item => {
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
            <h3 style="margin-top:10px; ${item.item_type === 'name_color' ? style : ''}">${esc(item.name)}</h3>
            <p style="color:var(--text-dim); font-size:0.85rem; margin-top:5px; height: 40px;">${esc(item.description)}</p>
            <div style="margin-top:15px; font-weight:bold; color:var(--orange);">🪙 ${item.price}</div>
            <button class="btn btn-primary" style="margin-top:10px; width: 100%;" onclick="buyShopItem('${item.id}', ${item.price})">Mua Ngay</button>
          </div>
        </div>`;
      });
      html += `</div>`;
    }
    
    $('app').innerHTML = html;
  } catch(err) {
    $('app').innerHTML = `<div class="empty">Lỗi tải cửa hàng: ${err.message}</div>`;
  }
}

window.buyShopItem = async function(itemId, price) {
  if(!currentUser) { toast('Vui lòng đăng nhập để mua đồ', 'error'); return; }
  if(currentUser.coins < price) { toast('Bạn không đủ Z-Coins! Hãy kiếm thêm bằng cách up kỷ lục.', 'error'); return; }
  if(!confirm(`Xác nhận mua vật phẩm này với giá ${price} 🪙?`)) return;
  
  try {
    const r = await fetch(`${API}/shop/buy/${itemId}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    if(!r.ok) throw new Error((await r.json()).detail || 'Lỗi mua đồ');
    toast('Mua thành công! Vào Hồ Sơ để trang bị nhé.');
    clearApiCache();
    await fetchUser();
    renderNav();
  } catch(e) {
    toast(e.message, 'error');
  }
};

window.equipShopItem = async function(userItemId) {
  if(!currentUser) return;
  try {
    const r = await fetch(`${API}/shop/equip/${userItemId}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    if(!r.ok) throw new Error((await r.json()).detail || 'Lỗi trang bị');
    toast('Đã cập nhật trang bị!');
    clearApiCache();
    await fetchUser();
    renderProfile(currentUser.id);
  } catch(e) {
    toast(e.message, 'error');
  }
};
"""

if "function renderShop" not in js:
    # insert before window.renderProfile
    render_profile_index = js.find("async function renderProfile")
    js = js[:render_profile_index] + shop_function + "\n  " + js[render_profile_index:]

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("done")
