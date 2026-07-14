const fs = require('fs');
let content = fs.readFileSync('temp.js', 'utf8');

// Patch buyShopItem
content = content.replace(
    "if((currentUser.coins||0) < price) { toast('Không đủ Z-Coins', 'error'); return; }",
    "if(currentUser.role !== 'ADMIN' && (currentUser.coins||0) < price) { toast('Không đủ Z-Coins', 'error'); return; }"
);

// Add filterShop function
const filterShopCode = `
  window.filterShop = function(type, btn) {
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
  };

  if(hash==='/upload') return renderUpload();`;

content = content.replace("  if(hash==='/upload') return renderUpload();", filterShopCode);

fs.writeFileSync('temp.js', content, 'utf8');
console.log("Patched temp.js");
