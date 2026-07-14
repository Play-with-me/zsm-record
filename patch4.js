const fs = require('fs');
let c = fs.readFileSync('temp.js', 'utf8');

// 1. Add formatCoins function at the top
if (!c.includes('function formatCoins')) {
    c = c.replace(
        "const esc=str=>String(str).replace(/[&<>'\"/]/g, m=>({'&':'&amp;','<':'&lt;','>':'&gt;','\\'':'&#39;','\"':'&quot;','/':'&#x2F;'}[m]));",
        "const esc=str=>String(str).replace(/[&<>'\"/]/g, m=>({'&':'&amp;','<':'&lt;','>':'&gt;','\\'':'&#39;','\"':'&quot;','/':'&#x2F;'}[m]));\nfunction formatCoins(n){if(n>=1e9)return(n/1e9).toFixed(1).replace(/\\.0$/,'')+'b';if(n>=1e6)return(n/1e6).toFixed(1).replace(/\\.0$/,'')+'m';if(n>=1e3)return(n/1e3).toFixed(1).replace(/\\.0$/,'')+'k';return n;}"
    );
}

// 2. Fix Admin coins in buyShopItem
c = c.replace(
    "if(currentUser.coins < price) { toast('Bạn không đủ Z-Coins! Hãy kiếm thêm bằng cách up kỷ lục.', 'error'); return; }",
    "if(currentUser.role !== 'ADMIN' && currentUser.coins < price) { toast('Bạn không đủ Z-Coins! Hãy kiếm thêm bằng cách up kỷ lục.', 'error'); return; }"
);

// 3. Format coins in Nav Bar
c = c.replace(
    '<span style="color:var(--orange)">🪙 ${currentUser.coins||0}</span>',
    '<span style="color:var(--orange)">🪙 ${currentUser.role === "ADMIN" ? "9999999999999" : formatCoins(currentUser.coins||0)}</span>'
);

// 4. Update Shop Rendering (Sorting and uniform icons)
// We will replace window.filterShop and the renderShop list part
const oldFilter = `  window.filterShop = function(type, btn) {
    const grid = document.getElementById('shop-grid');
    if(!grid) return;
    const items = grid.querySelectorAll('.shop-item');
    items.forEach(el => {
      if(type === 'all' || el.dataset.type === type) el.style.display = 'block';
      else el.style.display = 'none';
    });
    const btns = btn.parentElement.querySelectorAll('button');
    btns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  };`;

const newFilter = `  window.currentShopItems = [];
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
      if(item.item_type === 'name_color') style = \`color:\${meta}\`;
      if(item.item_type === 'avatar_frame') {
        style = \`width:60px;height:60px;border-radius:50%;margin:0 auto;box-shadow:\${meta}\`;
      }
      if(item.item_type === 'badge') style = 'font-size:2rem';
      
      html += \`<div class="video-card shop-item" data-type="\${item.item_type}" style="transition: transform 0.3s, box-shadow 0.3s; position:relative; overflow:hidden;">
        <div class="card-body" style="text-align:center; padding: 20px; position:relative; z-index:1;" onmouseenter="this.parentElement.style.transform='scale(1.05)'; this.parentElement.style.boxShadow='0 10px 20px rgba(0,0,0,0.5)'" onmouseleave="this.parentElement.style.transform='scale(1)'; this.parentElement.style.boxShadow='none'">
          <div style="position:absolute; top:-50%; left:-50%; width:200%; height:200%; background: radial-gradient(circle, \${item.item_type==='avatar_frame'?'rgba(138,43,226,0.1)':'rgba(255,255,255,0.05)'} 0%, transparent 70%); z-index:-1; pointer-events:none;"></div>
          <div style="\${style}; display:flex; justify-content:center; align-items:center;">\${iconUrl ? \`<img src="\${iconUrl}" style="width:40px;height:40px;object-fit:contain;image-rendering:pixelated;" onerror="this.style.display='none'"/>\` : (item.item_type === 'avatar_frame' ? '' : 'A')}</div>
          <h3 style="margin-top:10px; \${item.item_type === 'name_color' ? style : ''}">\${esc(item.name)}</h3>
          <p style="color:var(--text-dim); font-size:0.85rem; margin-top:5px; height: 40px;">\${esc(item.description)}</p>
          <div style="margin-top:15px; font-weight:bold; color:var(--orange);">🪙 \${formatCoins(item.price)}</div>
          <button class="btn btn-primary" style="margin-top:10px; width: 100%;" onclick="buyShopItem('\${item.id}', \${item.price})">Mua Ngay</button>
        </div>
      </div>\`;
    });
    
    document.getElementById('shop-grid').innerHTML = html;
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
  };`;

c = c.replace(oldFilter, newFilter);

// We need to modify renderShop to use the new HTML and call renderShopItems
const renderShopOld = `    let html = \`<div class="page-header animate-in">
      <p>Dùng Z-Coins 🪙 của bạn để mua vật phẩm trang trí hồ sơ.</p>
    </div>\`;
    
    if(items.length === 0) {
      html += '<div class="empty">Cửa hàng hiện đang trống</div>';
    } else {
      html += \`<div class="filters animate-in" style="margin-bottom: 20px; display:flex; gap:10px; flex-wrap:wrap">
        <button class="btn btn-outline active" onclick="filterShop('all', this)">Tất cả</button>
        <button class="btn btn-outline" onclick="filterShop('name_color', this)">Màu tên</button>
        <button class="btn btn-outline" onclick="filterShop('avatar_frame', this)">Khung Avatar</button>
        <button class="btn btn-outline" onclick="filterShop('badge', this)">Huy hiệu</button>
      </div>\`;
      html += \`<div class="video-grid animate-in" id="shop-grid">\`;
      items.forEach(item => {
        let meta = item.metadata_value;
        let style = '', iconUrl = '';
        try {
          const p = JSON.parse(meta);
          meta = p.value || p.css || '';
          iconUrl = p.icon || '';
        } catch(e) {}
        if(item.item_type === 'name_color') style = \`color:\${meta}\`;
        if(item.item_type === 'avatar_frame') {
          style = \`width:60px;height:60px;border-radius:50%;margin:0 auto;box-shadow:\${meta}\`;
        }
        if(item.item_type === 'badge') style = 'font-size:2rem';
        
        html += \`<div class="video-card shop-item" data-type="\${item.item_type}" style="transition: transform 0.3s, box-shadow 0.3s; position:relative; overflow:hidden;">
            <div class="card-body" style="text-align:center; padding: 20px; position:relative; z-index:1;" onmouseenter="this.parentElement.style.transform='scale(1.05)'; this.parentElement.style.boxShadow='0 10px 20px rgba(0,0,0,0.5)'" onmouseleave="this.parentElement.style.transform='scale(1)'; this.parentElement.style.boxShadow='none'">
              <div style="position:absolute; top:-50%; left:-50%; width:200%; height:200%; background: radial-gradient(circle, \${item.item_type==='avatar_frame'?'rgba(138,43,226,0.1)':'rgba(255,255,255,0.05)'} 0%, transparent 70%); z-index:-1; pointer-events:none;"></div>
              <div style="\${style}">\${iconUrl ? \`<img src="\${iconUrl}" style="width:100%;height:100%;object-fit:contain;border-radius:50%"/>\` : (item.item_type === 'avatar_frame' ? '' : 'A')}</div>
              <h3 style="margin-top:10px; \${item.item_type === 'name_color' ? style : ''}">\${esc(item.name)}</h3>
            <p style="color:var(--text-dim); font-size:0.85rem; margin-top:5px; height: 40px;">\${esc(item.description)}</p>
            <div style="margin-top:15px; font-weight:bold; color:var(--orange);">🪙 \${item.price}</div>
            <button class="btn btn-primary" style="margin-top:10px; width: 100%;" onclick="buyShopItem('\${item.id}', \${item.price})">Mua Ngay</button>
          </div>
        </div>\`;
      });
      html += \`</div>\`;
    }`;

const renderShopNew = `    let html = \`<div class="page-header animate-in">
      <p>Dùng Z-Coins 🪙 của bạn để mua vật phẩm trang trí hồ sơ.</p>
    </div>\`;
    
    if(items.length === 0) {
      html += '<div class="empty">Cửa hàng hiện đang trống</div>';
    } else {
      window.currentShopItems = items;
      html += \`<div class="filters animate-in" style="margin-bottom: 20px; display:flex; gap:10px; flex-wrap:wrap; align-items:center; justify-content:space-between;">
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
      <div class="video-grid animate-in" id="shop-grid"></div>\`;
    }`;

c = c.replace(renderShopOld, renderShopNew);

// 5. In renderShop, add setTimeout to call renderShopItems after injecting html
c = c.replace(
    "$('app').innerHTML = html;",
    "$('app').innerHTML = html; if(items.length > 0) setTimeout(() => window.renderShopItems(), 50);"
);

fs.writeFileSync('temp.js', c, 'utf8');
console.log("Patched temp.js for pixelarticons, sorting, and formatCoins.");
