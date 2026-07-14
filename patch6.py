import re

with open('temp.js', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Remove the old renderShop completely (up to customConfirm)
# It starts with "async function renderShop() {" and ends before "window.customConfirm = function"
pattern = r'async function renderShop\(\)\s*\{.*?(?=window\.customConfirm = function)'
c = re.sub(pattern, '', c, flags=re.DOTALL)

# 2. Remove the old filterShop completely
pattern2 = r'window\.filterShop = function.*?btn\.classList\.add\(\'active\'\);\s*\};'
c = re.sub(pattern2, '', c, flags=re.DOTALL)

# 3. Add the new robust code
new_code = """
  window.currentShopItems = [];
  window.currentShopFilter = 'all';
  window.currentShopSort = 'default';

  window.renderShopItems = function() {
    let items = [...window.currentShopItems];
    if(window.currentShopFilter !== 'all') {
      items = items.filter(i => i.item_type === window.currentShopFilter);
    }
    if(window.currentShopSort === 'price_asc') items.sort((a,b) => a.price - b.price);
    if(window.currentShopSort === 'price_desc') items.sort((a,b) => b.price - a.price);
    if(window.currentShopSort === 'rarity') {
      const getRarity = name => {
        if(name.includes('Đỏ')) return 5;
        if(name.includes('Vàng')) return 4;
        if(name.includes('Tím')) return 3;
        if(name.includes('Xanh Dương')) return 2;
        return 1;
      };
      items.sort((a,b) => getRarity(b.name) - getRarity(a.name));
    }
    
    let html = '';
    items.forEach(item => {
      let meta = item.metadata_value;
      let style = '', iconUrl = '';
      try {
        const p = JSON.parse(meta);
        meta = p.value || p.css || '';
        iconUrl = p.icon || '';
      } catch(e) {}
      if(item.item_type === 'name_color') style = `color:${meta}`;
      if(item.item_type === 'avatar_frame') {
        style = `box-shadow:${meta}`;
      }
      if(item.item_type === 'badge') style = 'font-size:2rem';
      
      html += `<div class="video-card shop-item" data-type="${item.item_type}" style="transition: transform 0.3s, box-shadow 0.3s; position:relative; overflow:hidden;">
        <div class="card-body" style="text-align:center; padding: 20px; position:relative; z-index:1;" onmouseenter="this.parentElement.style.transform='scale(1.05)'; this.parentElement.style.boxShadow='0 10px 20px rgba(0,0,0,0.5)'" onmouseleave="this.parentElement.style.transform='scale(1)'; this.parentElement.style.boxShadow='none'">
          <div style="position:absolute; top:-50%; left:-50%; width:200%; height:200%; background: radial-gradient(circle, ${item.item_type==='avatar_frame'?'rgba(138,43,226,0.1)':'rgba(255,255,255,0.05)'} 0%, transparent 70%); z-index:-1; pointer-events:none;"></div>
          
          <div style="width:60px; height:60px; margin:0 auto; display:flex; justify-content:center; align-items:center; ${item.item_type==='avatar_frame'?'border-radius:50%;':''} ${style}">
            ${iconUrl ? `<img src="${iconUrl}" style="max-width:100%;max-height:100%;object-fit:contain;image-rendering:pixelated;" onerror="this.style.display='none'"/>` : (item.item_type === 'avatar_frame' ? '' : 'A')}
          </div>
          
          <h3 style="margin-top:10px; ${item.item_type === 'name_color' ? style : ''}">${esc(item.name)}</h3>
          <p style="color:var(--text-dim); font-size:0.85rem; margin-top:5px; height: 40px;">${esc(item.description)}</p>
          <div style="margin-top:15px; font-weight:bold; color:var(--orange);">🪙 ${formatCoins(item.price)}</div>
          <button class="btn btn-primary" style="margin-top:10px; width: 100%;" onclick="buyShopItem('${item.id}', ${item.price})">Mua Ngay</button>
        </div>
      </div>`;
    });
    
    const grid = document.getElementById('shop-grid');
    if(grid) grid.innerHTML = html;
  };

  window.filterShop = function(type, btn) {
    window.currentShopFilter = type;
    const btns = btn.parentElement.querySelectorAll('button');
    btns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    window.renderShopItems();
  };
  
  window.sortShop = function(sortType) {
    window.currentShopSort = sortType;
    window.renderShopItems();
  };

  async function renderShop() {
    $('app').innerHTML = `<div class="animate-in"><div class="skeleton" style="height:100px;border-radius:var(--radius-lg);margin-bottom:24px"></div><div class="video-grid">${skCards(4)}</div></div>`;
    try {
      const items = await apiFetch('/shop/items');
      
      let html = `<div class="page-header animate-in">
        <h1>Cửa Hàng 🛍️</h1>
        <p>Dùng Z-Coins 🪙 của bạn để mua vật phẩm trang trí hồ sơ.</p>
      </div>`;
      
      if(!items || items.length === 0) {
        html += `<div class="empty animate-in">Chưa có vật phẩm nào được bày bán.</div>`;
      } else {
        window.currentShopItems = items;
        html += `<div class="shop-filters" style="margin-bottom:20px; display:flex; gap:10px; flex-wrap:wrap; align-items:center; justify-content:space-between;">
            <div style="display:flex; gap:10px;">
              <button class="btn btn-outline active" onclick="filterShop('all', this)">Tất cả</button>
              <button class="btn btn-outline" onclick="filterShop('name_color', this)">Màu tên</button>
              <button class="btn btn-outline" onclick="filterShop('avatar_frame', this)">Khung Avatar</button>
              <button class="btn btn-outline" onclick="filterShop('badge', this)">Huy hiệu</button>
            </div>
            <select class="form-select" style="width:auto" onchange="sortShop(this.value)">
              <option value="default">Sắp xếp mặc định</option>
              <option value="price_asc">Giá: Thấp đến Cao</option>
              <option value="price_desc">Giá: Cao đến Thấp</option>
              <option value="rarity">Độ hiếm</option>
            </select>
          </div>
          <div class="video-grid animate-in" id="shop-grid" style="--cols:4"></div>`;
      }
      
      $('app').innerHTML = html; 
      if(items && items.length > 0) setTimeout(() => window.renderShopItems(), 50);
    } catch(err) {
      $('app').innerHTML = `<div class="empty">Lỗi tải cửa hàng: ${err.message}</div>`;
    }
  }

"""

# Insert the new robust code exactly where the old renderShop was
# We will just prepend it to the window.customConfirm
c = c.replace("window.customConfirm = function", new_code + "\n  window.customConfirm = function")


with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch 6 successfully applied.")
