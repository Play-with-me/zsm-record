import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_renderBoard = '''  const [maps,cars,pets]=await Promise.all([cachedApiFetch('/maps', 300000), cachedApiFetch('/cars', 300000), cachedApiFetch('/pets', 300000)]);
  $('app').querySelector('.skeleton').outerHTML=`<div class="filter-bar">
    <h2>Lọc Dữ Liệu</h2>
    <div class="filter-grid">
      <div class="form-group"><label class="form-label">Bản đồ</label>${mkCombobox('bmap',maps.map(m=>({label:m.name,value:m.id})),'Tất cả bản đồ')}</div>
      <div class="form-group"><label class="form-label">Siêu xe</label>${mkCombobox('bcar',cars.map(c=>({label:c.name,value:c.id})),'Tất cả siêu xe')}</div>
      <div class="form-group"><label class="form-label">Pet</label>${mkCombobox('bpet',pets.map(p=>({label:p.name,value:p.id})),'Tất cả pet')}</div>
    </div>
    <button class="btn btn-purple btn-sm" style="margin-top:14px" onclick="loadBoard()">Áp dụng</button>
    <button class="btn btn-outline btn-sm" style="margin-top:14px" onclick="clearCB('bmap','Tất cả bản đồ');clearCB('bcar','Tất cả siêu xe');clearCB('bpet','Tất cả pet');loadBoard()">Khôi phục</button>
  </div>`;
  loadBoard();'''

new_renderBoard = '''  const [maps,cars,pets,allVideos]=await Promise.all([cachedApiFetch('/maps', 300000), cachedApiFetch('/cars', 300000), cachedApiFetch('/pets', 300000), cachedApiFetch('/videos?limit=500', 30000)]);
  
  let defaultMapId = '';
  if (allVideos && allVideos.length > 0 && maps && maps.length > 0) {
      const mapCounts = {};
      allVideos.forEach(v => {
          if(v.map_id) mapCounts[v.map_id] = (mapCounts[v.map_id] || 0) + 1;
      });
      let mostPopularMapId = null;
      let maxCount = 0;
      for (const [mid, count] of Object.entries(mapCounts)) {
          if (count > maxCount) { maxCount = count; mostPopularMapId = mid; }
      }
      if (mostPopularMapId) {
          defaultMapId = mostPopularMapId;
      }
  }

  $('app').querySelector('.skeleton').outerHTML=`<div class="filter-bar">
    <h2>Lọc Dữ Liệu</h2>
    <div class="filter-grid">
      <div class="form-group"><label class="form-label">Bản đồ</label>${mkCombobox('bmap',maps.map(m=>({label:m.name,value:m.id})),'Tất cả bản đồ',defaultMapId)}</div>
      <div class="form-group"><label class="form-label">Siêu xe</label>${mkCombobox('bcar',cars.map(c=>({label:c.name,value:c.id})),'Tất cả siêu xe')}</div>
      <div class="form-group"><label class="form-label">Pet</label>${mkCombobox('bpet',pets.map(p=>({label:p.name,value:p.id})),'Tất cả pet')}</div>
    </div>
    <button class="btn btn-purple btn-sm" style="margin-top:14px" onclick="loadBoard()">Áp dụng</button>
    <button class="btn btn-outline btn-sm" style="margin-top:14px" onclick="clearCB('bmap','Tất cả bản đồ');clearCB('bcar','Tất cả siêu xe');clearCB('bpet','Tất cả pet');loadBoard()">Khôi phục</button>
  </div>`;
  loadBoard();'''

js = js.replace(old_renderBoard, new_renderBoard)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
