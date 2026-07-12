import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add adminEdit and adminDelete logic
crud_funcs = r'''
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
'''

if "window.adminDelete = async function" not in js:
    js = js.replace('window.adminAdd=async(type)=>{', crud_funcs + '\n  window.adminAdd=async(type)=>{')

# Now patch the table renders
# Maps
old_maps = "<tbody>${maps.map(m=>`<tr><td style=\"font-weight:600\">${esc(m.name)}</td><td><span style=\"color:var(--yellow)\">${'★'.repeat(m.difficulty||1)}</span></td><td style=\"font-family:monospace;font-size:0.7rem;color:var(--text-dim)\">${m.id}</td></tr>`).join('')}</tbody>"
new_maps = r"<tbody>${maps.map(m=>`<tr><td style=\"font-weight:600\">${esc(m.name)}</td><td><span style=\"color:var(--yellow)\">${'★'.repeat(m.difficulty||1)}</span></td><td style=\"font-family:monospace;font-size:0.7rem;color:var(--text-dim)\">${m.id}</td><td><button class=\"btn btn-outline btn-sm\" style=\"padding:2px 8px;font-size:0.7rem\" onclick=\"adminEdit('map','${m.id}', '${encodeURIComponent(JSON.stringify(m))}')\">✏️</button> <button class=\"btn btn-danger btn-sm\" style=\"padding:2px 8px;font-size:0.7rem\" onclick=\"adminDelete('map','${m.id}','${esc(m.name).replace(/'/g, \"\\\\'\")}')\">🗑️</button></td></tr>`).join('')}</tbody>"
if "<th>Hành động</th>" not in js[js.find('<th>Mã ID</th>'):js.find('<th>Mã ID</th>')+50]:
    js = js.replace('<th>Mã ID</th></tr></thead>', '<th>Mã ID</th><th>Hành động</th></tr></thead>')
js = js.replace(old_maps, new_maps)

# Cars
old_cars = "<tbody>${cars.map(c=>`<tr><td style=\"font-weight:600\">${esc(c.name)}</td><td><span class=\"badge bg-purple\">${c.car_class||'A'}</span></td><td style=\"font-family:monospace;font-size:0.7rem;color:var(--text-dim)\">${c.id}</td></tr>`).join('')}</tbody>"
new_cars = r"<tbody>${cars.map(c=>`<tr><td style=\"font-weight:600\">${esc(c.name)}</td><td><span class=\"badge bg-purple\">${c.car_class||'A'}</span></td><td style=\"font-family:monospace;font-size:0.7rem;color:var(--text-dim)\">${c.id}</td><td><button class=\"btn btn-outline btn-sm\" style=\"padding:2px 8px;font-size:0.7rem\" onclick=\"adminEdit('car','${c.id}', '${encodeURIComponent(JSON.stringify(c))}')\">✏️</button> <button class=\"btn btn-danger btn-sm\" style=\"padding:2px 8px;font-size:0.7rem\" onclick=\"adminDelete('car','${c.id}','${esc(c.name).replace(/'/g, \"\\\\'\")}')\">🗑️</button></td></tr>`).join('')}</tbody>"
js = js.replace(old_cars, new_cars)

# Pets
old_pets = "<tbody>${pets.map(p=>`<tr><td style=\"font-weight:600\">${esc(p.name)}</td><td style=\"font-family:monospace;font-size:0.7rem;color:var(--text-dim)\">${p.id}</td></tr>`).join('')}</tbody>"
new_pets = r"<tbody>${pets.map(p=>`<tr><td style=\"font-weight:600\">${esc(p.name)}</td><td style=\"font-family:monospace;font-size:0.7rem;color:var(--text-dim)\">${p.id}</td><td><button class=\"btn btn-outline btn-sm\" style=\"padding:2px 8px;font-size:0.7rem\" onclick=\"adminEdit('pet','${p.id}', '${encodeURIComponent(JSON.stringify(p))}')\">✏️</button> <button class=\"btn btn-danger btn-sm\" style=\"padding:2px 8px;font-size:0.7rem\" onclick=\"adminDelete('pet','${p.id}','${esc(p.name).replace(/'/g, \"\\\\'\")}')\">🗑️</button></td></tr>`).join('')}</tbody>"
js = js.replace(old_pets, new_pets)

# Users
old_users = "<tbody>${users.map(u=>`<tr><td><div style=\"display:flex;align-items:center;gap:8px\"><img src=\"${u.avatar||'https://placehold.co/40x40/000/fff?text='+(u.username?u.username[0]:'U')}\" style=\"width:30px;height:30px;border-radius:50%;object-fit:cover\"/> <span style=\"font-weight:600\">${esc(u.username)}</span></div></td><td>${u.role==='ADMIN'?'<span class=\"badge bg-red\">ADMIN</span>':'<span class=\"badge bg-blue\">USER</span>'}</td><td style=\"font-family:monospace;font-size:0.7rem;color:var(--text-dim)\">${u.id}</td></tr>`).join('')}</tbody>"
new_users = r"<tbody>${users.map(u=>`<tr><td><div style=\"display:flex;align-items:center;gap:8px\"><img src=\"${u.avatar||'https://placehold.co/40x40/000/fff?text='+(u.username?u.username[0]:'U')}\" style=\"width:30px;height:30px;border-radius:50%;object-fit:cover\"/> <span style=\"font-weight:600\">${esc(u.username)}</span></div></td><td>${u.role==='ADMIN'?'<span class=\"badge bg-red\">ADMIN</span>':'<span class=\"badge bg-blue\">USER</span>'}</td><td style=\"font-family:monospace;font-size:0.7rem;color:var(--text-dim)\">${u.id}</td><td><button class=\"btn btn-outline btn-sm\" style=\"padding:2px 8px;font-size:0.7rem\" onclick=\"adminEdit('user','${u.id}', '${encodeURIComponent(JSON.stringify(u))}')\">✏️</button> <button class=\"btn btn-danger btn-sm\" style=\"padding:2px 8px;font-size:0.7rem\" onclick=\"adminDelete('user','${u.id}','${esc(u.username).replace(/'/g, \"\\\\'\")}')\">🗑️</button></td></tr>`).join('')}</tbody>"
js = js.replace(old_users, new_users)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("done")
