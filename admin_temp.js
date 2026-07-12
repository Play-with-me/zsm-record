
  if(!currentUser||currentUser.role!=='ADMIN'){ toast('Bạn không có quyền truy cập trang này!','error'); navigate('/'); return; }
  let tab='maps';

  async function renderTab() {
    const [maps,cars,pets,users,shopItems]=await Promise.all([cachedApiFetch('/maps', 300000),cachedApiFetch('/cars', 300000),cachedApiFetch('/pets', 300000),apiFetch('/users'),apiFetch('/shop/items')]);
    $('app').innerHTML=`<div class="animate-in" style="display:flex;flex-direction:column;gap:20px;">
      <div><h1 style="font-size:1.7rem;font-weight:800">&#128736; Bảng Quản Trị</h1><p style="color:var(--text-muted);font-size:0.85rem">Quản lý dữ liệu hệ thống.</p></div>
      <div><div class="tabs">
        <button class="tab-btn${tab==='maps'?' active':''}" onclick="adminTab('maps')">Bản đồ (${maps.length})</button>
        <button class="tab-btn${tab==='cars'?' active':''}" onclick="adminTab('cars')">Siêu xe (${cars.length})</button>
        <button class="tab-btn${tab==='pets'?' active':''}" onclick="adminTab('pets')">Pets (${pets.length})</button>
        <button class="tab-btn${tab==='users'?' active':''}" onclick="adminTab('users')">Tài khoản (${users.length})</button>
          <button class="tab-btn${tab==='tournaments'?' active':''}" onclick="adminTab('tournaments')">Giải đấu</button>
      </div></div>

      ${tab==='maps'?`
        <div class="card"><div class="card-body">
          <div style="font-size:0.85rem;font-weight:700;margin-bottom:10px">Thêm Bản đồ mới</div>
          <div class="admin-add-form">
            <div class="form-group"><label class="form-label">Tên bản đồ *</label><input class="form-input" id="mn" placeholder="Tên bản đồ"/></div>
            <div class="form-group" style="max-width:90px"><label class="form-label">Độ khó (sao)</label><input class="form-input" id="md" type="number" min="1" max="10" value="1"/></div>
            <button class="btn btn-primary btn-sm" onclick="adminAdd('map')">+ Thêm</button>
          </div>
        </div></div>
        <div class="card" style="overflow:hidden"><table class="data-table"><thead><tr><th>Tên</th><th>Độ khó</th><th>Mã ID</th><th>Hành động</th></tr></thead>
        <tbody>${maps.map(m=>`<tr><td style="font-weight:600">${esc(m.name)}</td><td><span style="color:var(--yellow)">${'★'.repeat(m.difficulty||1)}</span></td><td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${m.id}</td><td><button class="btn btn-outline btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminEdit('map','${m.id}', '${encodeURIComponent(JSON.stringify(m))}')">✏️</button> <button class="btn btn-danger btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminDelete('map','${m.id}','${esc(m.name).replace(/'/g, "\\'")}')">🗑️</button></td></tr>`).join('')}</tbody>
        </table></div>`:
      tab==='cars'?`
        <div class="card"><div class="card-body">
          <div style="font-size:0.85rem;font-weight:700;margin-bottom:10px">Thêm Siêu xe mới</div>
          <div class="admin-add-form">
            <div class="form-group"><label class="form-label">Tên xe *</label><input class="form-input" id="cn" placeholder="Tên xe"/></div>
            <div class="form-group" style="max-width:90px"><label class="form-label">Phân khúc</label><input class="form-input" id="cc" placeholder="S, A..."/></div>
            <button class="btn btn-sm" style="background:var(--orange);color:#fff" onclick="adminAdd('car')">+ Thêm</button>
          </div>
        </div></div>
        <div class="card" style="overflow:hidden"><table class="data-table"><thead><tr><th>Tên</th><th>Phân khúc</th><th>Mã ID</th><th>Hành động</th></tr></thead>
        <tbody>${cars.map(c=>`<tr><td style="font-weight:600">${esc(c.name)}</td><td><span class="badge badge-orange">${esc(c.car_class||'?')}</span></td><td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${c.id}</td><td><button class="btn btn-outline btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminEdit('car','${c.id}', '${encodeURIComponent(JSON.stringify(c))}')">✏️</button> <button class="btn btn-danger btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminDelete('car','${c.id}','${esc(c.name).replace(/'/g, "\'")}')">🗑️</button></td></tr>`).join('')}</tbody>
        </table></div>`:
      tab==='pets'?`<div class="card"><div class="card-body">
          <div style="font-size:0.85rem;font-weight:700;margin-bottom:10px">Thêm Pet mới</div>
          <div class="admin-add-form">
            <div class="form-group"><label class="form-label">Tên Pet *</label><input class="form-input" id="pn" placeholder="Tên Pet"/></div>
            <button class="btn btn-sm" style="background:var(--purple);color:#fff" onclick="adminAdd('pet')">+ Thêm</button>
          </div>
        </div></div>
        <div class="card" style="overflow:hidden"><table class="data-table"><thead><tr><th>Tên</th><th>Mã ID</th><th>Hành động</th></tr></thead>
        <tbody>${pets.map(p=>`<tr><td style="font-weight:600">${esc(p.name)}</td><td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${p.id}</td><td><button class="btn btn-outline btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminEdit('pet','${p.id}', '${encodeURIComponent(JSON.stringify(p))}')">✏️</button> <button class="btn btn-danger btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminDelete('pet','${p.id}','${esc(p.name).replace(/'/g, "\\'")}')">🗑️</button></td></tr>`).join('')}</tbody>
        </table></div>`:
      tab==='users'?`
        <div class="card" style="overflow:hidden"><table class="data-table"><thead><tr><th>Avatar</th><th>Tài khoản</th><th>Email</th><th>Quyền</th><th>Mã ID</th><th>Hành động</th></tr></thead>
        <tbody>${users.map(u=>`<tr>
          <td>${u.avatar?`<img src="${esc(optimizedImage(u.avatar, 48))}" width="28" height="28" loading="lazy" decoding="async" style="width:28px;height:28px;border-radius:50%;object-fit:cover"/>`:`<div class="avatar avatar-sm">${esc(u.username[0].toUpperCase())}</div>`}</td>
          <td style="font-weight:600">${esc(u.username)}</td>
          <td style="color:var(--text-dim)">${esc(u.email)}</td>
          <td><span class="badge ${u.role==='ADMIN'?'badge-red':'badge-blue'}">${esc(u.role)}</span></td>
          <td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${u.id}</td>
          <td><button class="btn btn-sm btn-outline" onclick="adminEditUser('${u.id}', '${esc(u.username)}', '${esc(u.email)}')">&#9998; Sửa</button> <button class="btn btn-danger btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminDelete(\'user\',\'${u.id}\',\'${esc(u.username).replace(/\'/g, "\\\'")}\')">🗑️</button></td>
        </tr>`).join('')}</tbody>
        </table></div>`:
        tab==='tournaments'?`
          <div class="card"><div class="card-body">
            <div style="font-size:0.85rem;font-weight:700;margin-bottom:10px">Thêm Giải Đấu Mới</div>
            <div class="admin-add-form" style="display:flex;flex-direction:column;gap:12px;">
              <div class="form-group"><label class="form-label">Tên giải đấu *</label><input class="form-input" id="t_name" placeholder="VD: Asian Cup 2026"/></div>
              <div class="form-group"><label class="form-label">Mô tả</label><input class="form-input" id="t_desc" placeholder="Mô tả giải đấu"/></div>
              <div class="form-group"><label class="form-label">Map ID *</label><select class="form-select" id="t_map">${maps.map(m=>`<option value="${m.id}">${esc(m.name)}</option>`).join('')}</select></div>
              <div style="display:flex;gap:12px;">
                <div class="form-group" style="flex:1"><label class="form-label">Bắt đầu *</label><input class="form-input" type="datetime-local" id="t_start"/></div>
                <div class="form-group" style="flex:1"><label class="form-label">Kết thúc *</label><input class="form-input" type="datetime-local" id="t_end"/></div>
              </div>
              <button class="btn btn-primary btn-sm" onclick="adminAdd('tournament')">+ Thêm Giải Đấu</button>
            </div>
          </div></div>
          <div id="admin-t-list" style="margin-top:20px;">Đang tải danh sách giải...</div>
        `:''}
      </div>`;
    }

  
      if(tab==='tournaments'){
        apiFetch('/record-board/tournaments').then(tList=>{
          if(tList && tList.length){
            const html = '<div class="card" style="overflow:hidden"><table class="data-table"><thead><tr><th>Tên giải</th><th>Map</th><th>Bắt đầu</th><th>Kết thúc</th><th>Hành động</th></tr></thead><tbody>' + tList.map(t=>`<tr><td style="font-weight:600">${esc(t.name)}</td><td>${esc(maps.find(m=>m.id===t.map_id)?.name||t.map_id)}</td><td>${dateStr(t.start_time)}</td><td>${dateStr(t.end_time)}</td><td><button class="btn btn-outline btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminEdit('tournament','${t.id}', '${encodeURIComponent(JSON.stringify(t))}')">✏️</button> <button class="btn btn-danger btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminDelete('tournament','${t.id}','${esc(t.name).replace(/'/g, "\\'")}')">🗑️</button></td></tr>`).join('') + '</tbody></table></div>';
            const el = document.getElementById('admin-t-list');
            if(el) el.innerHTML = html;
          }else{
            const el = document.getElementById('admin-t-list');
            if(el) el.innerHTML = '<div class="empty">Chưa có giải đấu nào.</div>';
          }
        }).catch(e=>{
            const el = document.getElementById('admin-t-list');
            if(el) el.innerHTML = 'Lỗi tải: ' + e.message;
        });
      }

    window.adminTab=(t)=>{ tab=t; renderTab(); };
  
// --- ADMIN CRUD LOGIC ---
window.adminDelete = async function(type, id, name) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `<div class="modal">
    <h3 style="margin-bottom:10px;color:var(--red)">Xác nhận Xóa</h3>
    <p style="margin-bottom:20px;">Bạn có chắc chắn muốn xóa <b>${esc(name)}</b>?<br/>Hành động này không thể hoàn tác.</p>
    <div class="modal-actions">
      <button class="btn btn-outline btn-sm" onclick="this.closest('.modal-overlay').remove()">Hủy</button>
      <button class="btn btn-danger btn-sm" onclick="doAdminDelete('${type}', '${id}', this.closest('.modal-overlay'))">Xóa</button>
    </div>
  </div>`;
  document.body.appendChild(overlay);
};

window.doAdminDelete = async function(type, id, modal) {
  modal.querySelector('button.btn-danger').disabled = true;
  modal.querySelector('button.btn-danger').innerHTML = 'Đang xóa...';
  try {
    let endpoint = `/admin/${type}s/${id}`;
    if(type==='tournament') endpoint = `/record-board/tournaments/${id}`;
    await apiFetch(endpoint, {method: 'DELETE'});
    toast('Đã xóa thành công!');
    modal.remove();
    clearApiCache();
    if(window.location.hash.includes('admin')) {
        document.querySelector('.tab-btn.active').click();
    }
  } catch(e) {
    toast('Lỗi xóa: ' + e.message, 'error');
    modal.querySelector('button.btn-danger').disabled = false;
    modal.querySelector('button.btn-danger').innerHTML = 'Xóa';
  }
};

window.adminEdit = async function(type, id, itemObj) {
  const item = JSON.parse(decodeURIComponent(itemObj));
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  let formHtml = '';
  
  if(type==='map') {
    formHtml = `
      <div class="form-group"><label>Tên</label><input id="edit_name" class="form-input" value="${esc(item.name)}"/></div>
      <div class="form-group"><label>Độ khó (sao)</label><input id="edit_diff" type="number" class="form-input" value="${item.difficulty||1}"/></div>
    `;
  } else if(type==='car') {
    formHtml = `
      <div class="form-group"><label>Tên</label><input id="edit_name" class="form-input" value="${esc(item.name)}"/></div>
      <div class="form-group"><label>Class</label><input id="edit_class" class="form-input" value="${esc(item.car_class||'A')}"/></div>
    `;
  } else if(type==='pet') {
    formHtml = `
      <div class="form-group"><label>Tên</label><input id="edit_name" class="form-input" value="${esc(item.name)}"/></div>
    `;
  } else if(type==='user') {
    formHtml = `
      <div class="form-group"><label>Username</label><input class="form-input" value="${esc(item.username)}" disabled/></div>
      <div class="form-group"><label>Role</label><select id="edit_role" class="form-select"><option value="USER" ${item.role==='USER'?'selected':''}>USER</option><option value="ADMIN" ${item.role==='ADMIN'?'selected':''}>ADMIN</option></select></div>
    `;
  } else if(type==='tournament') {
    formHtml = `
      <div class="form-group"><label>Tên</label><input id="edit_name" class="form-input" value="${esc(item.name)}"/></div>
      <div class="form-group"><label>Mô tả</label><input id="edit_desc" class="form-input" value="${esc(item.description)}"/></div>
      <div class="form-group"><label>Map ID</label><input id="edit_map" class="form-input" value="${esc(item.map_id)}"/></div>
      <div style="display:flex;gap:10px;">
        <div class="form-group" style="flex:1"><label>Bắt đầu</label><input id="edit_start" type="datetime-local" class="form-input" value="${item.start_time ? item.start_time.substring(0,16) : ''}"/></div>
        <div class="form-group" style="flex:1"><label>Kết thúc</label><input id="edit_end" type="datetime-local" class="form-input" value="${item.end_time ? item.end_time.substring(0,16) : ''}"/></div>
      </div>
    `;
  }

  overlay.innerHTML = `<div class="modal">
    <h3 style="margin-bottom:15px;color:var(--neon-cyan)">Sửa Thông Tin</h3>
    ${formHtml}
    <div class="modal-actions" style="margin-top:20px;">
      <button class="btn btn-outline btn-sm" onclick="this.closest('.modal-overlay').remove()">Hủy</button>
      <button class="btn btn-primary btn-sm" onclick="doAdminEdit('${type}', '${id}', this.closest('.modal-overlay'))">Lưu</button>
    </div>
  </div>`;
  document.body.appendChild(overlay);
};

window.doAdminEdit = async function(type, id, modal) {
  try {
    let bodyData = {};
    if(type==='map') bodyData = {name: modal.querySelector('#edit_name').value, difficulty: parseInt(modal.querySelector('#edit_diff').value)};
    else if(type==='car') bodyData = {name: modal.querySelector('#edit_name').value, car_class: modal.querySelector('#edit_class').value};
    else if(type==='pet') bodyData = {name: modal.querySelector('#edit_name').value};
    else if(type==='user') bodyData = {role: modal.querySelector('#edit_role').value};
    else if(type==='tournament') bodyData = {
      name: modal.querySelector('#edit_name').value, 
      description: modal.querySelector('#edit_desc').value, 
      map_id: modal.querySelector('#edit_map').value, 
      start_time: new Date(modal.querySelector('#edit_start').value).toISOString(),
      end_time: new Date(modal.querySelector('#edit_end').value).toISOString()
    };
    
    let endpoint = `/admin/${type}s/${id}`;
    if(type==='tournament') endpoint = `/record-board/tournaments/${id}`;
    
    await apiFetch(endpoint, {method: 'PUT', body: JSON.stringify(bodyData)});
    toast('Đã cập nhật thành công!');
    modal.remove();
    clearApiCache();
    if(window.location.hash.includes('admin')) {
        document.querySelector('.tab-btn.active').click();
    }
  } catch(e) {
    toast('Lỗi cập nhật: ' + e.message, 'error');
  }
};

  window.adminAdd=async(type)=>{
    try {
      if(type==='map'){
        const n=$('mn').value; if(!n){toast('Vui lòng nhập tên','error');return;}
        await apiFetch('/admin/maps',{method:'POST',body:JSON.stringify({name:n, difficulty: parseInt($('md').value||1)})});
      } else if(type==='car'){
        const n=$('cn').value; if(!n){toast('Vui lòng nhập tên','error');return;}
        await apiFetch('/admin/cars',{method:'POST',body:JSON.stringify({name:n,car_class:$('cc').value||'A'})});
      } else {
        const n=$('pn').value; if(!n){toast('Vui lòng nhập tên','error');return;}
        await apiFetch('/admin/pets',{method:'POST',body:JSON.stringify({name:n})});
      }
      clearApiCache();
      toast('Đã thêm thành công!'); renderTab();
    } catch(e){ toast(e.message,'error'); }
  };

  renderTab();