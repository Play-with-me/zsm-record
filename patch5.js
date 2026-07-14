const fs = require('fs');
let c = fs.readFileSync('temp.js', 'utf8');

// 1. Add customConfirm function
const customConfirmCode = `window.customConfirm = function(msg, onConfirm) {
  const overlay = document.createElement('div');
  overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);z-index:9999;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(5px);';
  overlay.innerHTML = \`
    <div class="card animate-in" style="min-width:300px;text-align:center;padding:24px;border:1px solid rgba(255,255,255,0.1);box-shadow:0 20px 40px rgba(0,0,0,0.5);">
      <h3 style="margin-bottom:15px;font-size:1.2rem;color:var(--orange);">Xác nhận</h3>
      <p style="margin-bottom:20px;color:var(--text);font-size:0.95rem;">\${msg}</p>
      <div style="display:flex;gap:10px;justify-content:center;">
        <button class="btn btn-outline" id="btn-cancel" style="flex:1;">Hủy</button>
        <button class="btn btn-primary" id="btn-ok" style="flex:1;">Đồng ý</button>
      </div>
    </div>
  \`;
  document.body.appendChild(overlay);
  document.getElementById('btn-cancel').onclick = () => overlay.remove();
  document.getElementById('btn-ok').onclick = () => { overlay.remove(); onConfirm(); };
};
`;
if(!c.includes('window.customConfirm')) {
    c = c.replace("window.buyShopItem = async function(itemId, price) {", customConfirmCode + "\nwindow.buyShopItem = async function(itemId, price) {");
}

// 2. Update buyShopItem to use customConfirm
const oldBuy = `    if(!confirm(\`Xác nhận mua vật phẩm này với giá \${price} 🪙?\`)) return;
    
    try {
      const r = await fetch(\`\${API}/shop/buy/\${itemId}\`, {
        method: 'POST',
        headers: { 'Authorization': \`Bearer \${getToken()}\` }
      });
      if(!r.ok) throw new Error((await r.json()).detail || 'Lỗi mua đồ');
      toast('Mua thành công! Vào Hồ Sơ để trang bị nhạc.');
      clearApiCache();
      await fetchUser();
      renderNav();
    } catch(e) {
      toast(e.message, 'error');
    }`;
const newBuy = `    customConfirm(\`Bạn có chắc muốn mua vật phẩm này với giá \${formatCoins(price)} Z-Coins?\`, async () => {
      try {
        const r = await fetch(\`\${API}/shop/buy/\${itemId}\`, {
          method: 'POST',
          headers: { 'Authorization': \`Bearer \${getToken()}\` }
        });
        if(!r.ok) throw new Error((await r.json()).detail || 'Lỗi mua đồ');
        toast('Mua thành công! Vật phẩm đã được chuyển vào Túi đồ.');
        clearApiCache();
        await fetchUser();
        renderNav();
        renderShop();
      } catch(e) {
        toast(e.message, 'error');
      }
    });`;
c = c.replace(oldBuy, newBuy);

// 3. Update toggleUserMenu to add Inventory link
const oldUserMenu = `<button class="dd-item" onclick="navigate('/profile/'+currentUser.id);closeMenu()">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        Hồ sơ của tôi
      </button>`;
const newUserMenu = `<button class="dd-item" onclick="navigate('/profile/'+currentUser.id);closeMenu()">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        Hồ sơ của tôi
      </button>
      <button class="dd-item" onclick="navigate('/inventory');closeMenu()">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><path d="M4 10h16M10 16h4M4 4h16v6H4z"/></svg>
        Túi đồ 🎒
      </button>`;
c = c.replace(oldUserMenu, newUserMenu);

// 4. Update router
c = c.replace("if(hash==='/shop') return renderShop();", "if(hash==='/shop') return renderShop();\n  if(hash==='/inventory') return renderInventory();");

// 5. Add renderInventory function
const renderInvCode = `
window.renderInventory = async function() {
  $('app').innerHTML = \`<div class="animate-in"><div class="skeleton" style="height:100px;border-radius:var(--radius-lg);margin-bottom:24px"></div><div class="video-grid">\${skCards(4)}</div></div>\`;
  try {
    const items = await apiFetch('/shop/my-items');
    
    let html = \`<div class="page-header animate-in">
      <h1>Túi Đồ 🎒</h1>
      <p>Danh sách các vật phẩm bạn đã sở hữu. Chọn để trang bị hoặc tháo ra.</p>
    </div>\`;
    
    if(items.length === 0) {
      html += '<div class="empty">Túi đồ của bạn đang trống! Hãy ghé thăm <a href="#/shop" style="color:var(--orange)">Cửa hàng</a> nhé.</div>';
    } else {
      html += \`<div class="video-grid animate-in" id="inventory-grid">\`;
      items.forEach(ui => {
        const item = ui.item;
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
        
        html += \`<div class="video-card shop-item" data-type="\${item.item_type}" style="transition: transform 0.3s, box-shadow 0.3s; position:relative; overflow:hidden; border: \${ui.is_equipped ? '2px solid var(--orange)' : '1px solid rgba(255,255,255,0.1)'};">
            \${ui.is_equipped ? '<div style="position:absolute;top:5px;right:5px;background:var(--orange);color:#fff;font-size:0.6rem;padding:2px 6px;border-radius:4px;font-weight:bold;">ĐANG DÙNG</div>' : ''}
            <div class="card-body" style="text-align:center; padding: 20px; position:relative; z-index:1;">
              <div style="position:absolute; top:-50%; left:-50%; width:200%; height:200%; background: radial-gradient(circle, \${item.item_type==='avatar_frame'?'rgba(138,43,226,0.1)':'rgba(255,255,255,0.05)'} 0%, transparent 70%); z-index:-1; pointer-events:none;"></div>
              <div style="width:60px;height:60px;margin:0 auto;display:flex;align-items:center;justify-content:center;\${style}">\${iconUrl ? \`<img src="\${iconUrl}" style="max-width:100%;max-height:100%;object-fit:contain;image-rendering:pixelated;" onerror="this.style.display='none'"/>\` : (item.item_type === 'avatar_frame' ? '' : 'A')}</div>
              <h3 style="margin-top:10px; \${item.item_type === 'name_color' ? style : ''}">\${esc(item.name)}</h3>
            <p style="color:var(--text-dim); font-size:0.85rem; margin-top:5px; height: 40px;">\${esc(item.description)}</p>
            <button class="btn \${ui.is_equipped ? 'btn-outline' : 'btn-primary'}" style="margin-top:10px; width: 100%;" onclick="equipShopItem('\${ui.id}')">\${ui.is_equipped ? 'Tháo ra' : 'Trang bị'}</button>
          </div>
        </div>\`;
      });
      html += \`</div>\`;
    }
    $('app').innerHTML = html;
  } catch(err) {
    $('app').innerHTML = \`<div class="empty">Lỗi tải túi đồ: \${err.message}</div>\`;
  }
};
`;

if(!c.includes('window.renderInventory = async function()')) {
    c = c.replace("window.equipShopItem = async function(userItemId) {", renderInvCode + "\nwindow.equipShopItem = async function(userItemId) {");
}

// 6. Fix equipShopItem to also re-render inventory if we are on it
c = c.replace(
    "toast('Đã cập nhật trang bị!');",
    "toast('Đã cập nhật trang bị!'); if(window.location.hash === '#/inventory') renderInventory(); if(window.location.hash.startsWith('#/profile')) renderProfile(currentUser.id);"
);

// 7. Fix max-width in Shop icons for uniformity (renderShopItems)
c = c.replace(
    `<img src="\${iconUrl}" style="width:40px;height:40px;object-fit:contain;image-rendering:pixelated;" onerror="this.style.display='none'"/>`,
    `<img src="\${iconUrl}" style="max-width:100%;max-height:100%;object-fit:contain;image-rendering:pixelated;" onerror="this.style.display='none'"/>`
);
// Also wrap the style div in 60x60 in shop
c = c.replace(
    `<div style="\${style}; display:flex; justify-content:center; align-items:center;">\${iconUrl`,
    `<div style="\${style}; width:60px; height:60px; margin:0 auto; display:flex; justify-content:center; align-items:center;">\${iconUrl`
);


fs.writeFileSync('temp.js', c, 'utf8');
console.log("Patched temp.js for Inventory, custom confirm modal, and icon alignment.");
