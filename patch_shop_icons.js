const fs = require('fs');

let content = fs.readFileSync('temp.js', 'utf8');

const regex = /html \+= `<div class="video-grid animate-in" style="--cols:4">`;\s*items\.forEach\(item => \{\s*let style = '';\s*if\(item\.item_type === 'name_color'\) \{\s*style = `color: \$\{item\.metadata_value\}; font-weight:bold;`;\s*\} else if\(item\.item_type === 'avatar_frame'\) \{\s*style = `border: \$\{item\.metadata_value\}; border-radius:50%; width: 48px; height: 48px;[\s\S]*?display:inline-block; margin-bottom:10px;`;\s*\}\s*html \+= `\s*<div class="video-card">\s*<div class="card-body" style="text-align:center; padding: 20px;">\s*<div style="\$\{style\}">\$\{item\.item_type === 'avatar_frame' \? '' : 'A'\}<\/div>\s*<h3 style="margin-top:10px; \$\{item\.item_type === 'name_color' \? style : ''\}">\$\{esc\(item\.name\)\}<\/h3>/;

const match = content.match(regex);
if (match) {
    console.log("MATCHED!");
    const replacement = `let filterHtml = \`<div class="shop-filters" style="margin-bottom:20px; display:flex; gap:10px; flex-wrap:wrap;">
          <button class="btn btn-outline active" onclick="filterShop('all', this)">Tất cả</button>
          <button class="btn btn-outline" onclick="filterShop('name_color', this)">Màu tên</button>
          <button class="btn btn-outline" onclick="filterShop('avatar_frame', this)">Khung Avatar</button>
          <button class="btn btn-outline" onclick="filterShop('badge', this)">Huy hiệu</button>
        </div>\`;
        html = html.replace('</div>', '</div>' + filterHtml);
        html += \`<div class="video-grid animate-in" id="shop-grid" style="--cols:4">\`;
        items.forEach(item => {
          let style = '';
          let metaVal = item.metadata_value;
          let iconUrl = '';
          try {
            const m = JSON.parse(item.metadata_value);
            metaVal = m.value;
            iconUrl = m.icon;
          } catch(e) {}

          if(item.item_type === 'name_color') {
            style = \`color: \${metaVal}; font-weight:bold;\`;
          } else if(item.item_type === 'avatar_frame') {
            style = \`box-shadow: \${metaVal}; border-radius:50%; width: 48px; height: 48px; display:inline-flex; align-items:center; justify-content:center; margin-bottom:10px;\`;
          }
          
          html += \`
          <div class="video-card shop-item" data-type="\${item.item_type}">
            <div class="card-body" style="text-align:center; padding: 20px;">
              <div style="\${style}">\${iconUrl ? \`<img src="\${iconUrl}" style="width:100%;height:100%;object-fit:contain;border-radius:50%"/>\` : (item.item_type === 'avatar_frame' ? '' : 'A')}</div>
              <h3 style="margin-top:10px; \${item.item_type === 'name_color' ? style : ''}">\${esc(item.name)}</h3>\``;
    content = content.replace(regex, replacement);
    fs.writeFileSync('temp.js', content, 'utf8');
} else {
    console.log("NOT MATCHED");
}
