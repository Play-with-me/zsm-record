import os

js_code = """
window.openInventory = async function() {
  if (!currentUser) { toast('Vui lòng đăng nhập', 'error'); return; }
  
  const overlay = document.createElement('div');
  overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);z-index:9999;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(5px);';
  
  const modal = document.createElement('div');
  modal.style.cssText = 'background:var(--card-bg); border:1px solid rgba(255,255,255,0.1); border-radius:var(--radius-lg); padding:20px; width:90%; max-width:600px; max-height:80vh; overflow-y:auto; box-shadow:var(--shadow-lg);';
  
  modal.innerHTML = `<h2 style="margin-bottom:15px;text-align:center;color:var(--neon-blue);">🎒 Túi Đồ Của Tôi</h2><div id="inv-loading" style="text-align:center;padding:20px;">Đang tải...</div>`;
  
  overlay.appendChild(modal);
  document.body.appendChild(overlay);
  
  overlay.onclick = (e) => { if(e.target === overlay) overlay.remove(); };
  
  try {
    const items = await apiFetch('/shop/my-items');
    if (!items || items.length === 0) {
      modal.innerHTML = `<h2 style="margin-bottom:15px;text-align:center;color:var(--neon-blue);">🎒 Túi Đồ Của Tôi</h2><div style="text-align:center;padding:20px;color:var(--text-dim);">Túi đồ trống. Hãy mua đồ trong cửa hàng nhé!</div>`;
    } else {
      let invHtml = `<h2 style="margin-bottom:15px;text-align:center;color:var(--neon-blue);">🎒 Túi Đồ Của Tôi</h2>`;
      invHtml += `<div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(140px, 1fr)); gap:15px;">`;
      
      items.forEach(ui => {
        const item = ui.item;
        let meta = item.metadata_value;
        let style = '', iconUrl = '';
        try {
          const p = JSON.parse(meta);
          meta = p.value || p.css || '';
          iconUrl = p.icon || '';
        } catch(e) {}
        
        if(item.item_type === 'name_color') style = `color:${meta}`;
        if(item.item_type === 'avatar_frame') style = `box-shadow:${meta}`;
        if(item.item_type === 'badge') style = 'font-size:2rem';
        
        invHtml += `<div style="background:var(--bg-dark); border:1px solid rgba(255,255,255,0.05); border-radius:var(--radius-md); padding:15px; text-align:center; position:relative;">
          <div style="width:60px; height:60px; margin:0 auto 10px; display:flex; justify-content:center; align-items:center; ${item.item_type==='avatar_frame'?'border-radius:50%;':''} ${style}">
            ${iconUrl ? `<img src="${iconUrl}" style="max-width:100%;max-height:100%;object-fit:contain;image-rendering:pixelated;" onerror="this.style.display='none'"/>` : (item.item_type === 'avatar_frame' ? '' : 'A')}
          </div>
          <div style="font-size:0.9rem; font-weight:bold; margin-bottom:5px; height:36px; overflow:hidden; ${item.item_type === 'name_color' ? style : ''}">${esc(item.name)}</div>
          <button class="btn ${ui.is_equipped ? 'btn-danger' : 'btn-primary'} btn-sm" style="width:100%;" onclick="equipItem('${ui.id}', this)">
            ${ui.is_equipped ? 'Tháo ra' : 'Sử dụng'}
          </button>
        </div>`;
      });
      
      invHtml += `</div>`;
      modal.innerHTML = invHtml;
    }
  } catch(e) {
    modal.innerHTML = `<h2 style="margin-bottom:15px;text-align:center;color:var(--neon-blue);">🎒 Túi Đồ Của Tôi</h2><div style="text-align:center;padding:20px;color:red;">Lỗi tải túi đồ: ${e.message}</div>`;
  }
};

window.equipItem = async function(userItemId, btn) {
  try {
    const prevText = btn.innerText;
    btn.innerText = '...';
    btn.disabled = true;
    const r = await fetch(`${API}/shop/equip/${userItemId}`, {
      method: 'POST',
      headers: { 'Authorization': \`Bearer \${getToken()}\` }
    });
    if(!r.ok) throw new Error((await r.json()).detail || 'Lỗi trang bị');
    
    toast('Đã cập nhật trang bị!');
    clearApiCache();
    await fetchUser();
    renderNav();
    if(window.location.hash.startsWith('#profile')) {
      const parts = window.location.hash.split('/');
      if(parts[1]) renderProfile(parts[1]);
    }
    
    // Refresh inventory modal silently by re-clicking (or we can just close it, but refreshing is better)
    btn.innerText = prevText === 'Sử dụng' ? 'Tháo ra' : 'Sử dụng';
    if(btn.innerText === 'Tháo ra') {
      btn.className = 'btn btn-danger btn-sm';
    } else {
      btn.className = 'btn btn-primary btn-sm';
    }
    btn.disabled = false;
    
  } catch(e) {
    toast(e.message, 'error');
    btn.disabled = false;
    btn.innerText = 'Lỗi';
  }
};
"""

with open("temp.js", "a", encoding="utf-8") as f:
    f.write("\n" + js_code)
print("Inventory patched to temp.js")
