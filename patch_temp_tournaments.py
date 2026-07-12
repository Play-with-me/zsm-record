import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Patch renderAdmin tabs
old_tabs = '''<button class="tab-btn${tab==='users'?' active':''}" onclick="adminTab('users')">Tài khoản (${users.length})</button>'''
new_tabs = '''<button class="tab-btn${tab==='users'?' active':''}" onclick="adminTab('users')">Tài khoản (${users.length})</button>\n          <button class="tab-btn${tab==='tournaments'?' active':''}" onclick="adminTab('tournaments')">Giải đấu</button>'''
if "adminTab('tournaments')" not in js:
    js = js.replace(old_tabs, new_tabs)

# 2. Patch renderAdmin body for Tournaments
old_body = '''<td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${u.id}</td><td><button class="btn btn-outline btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminEdit('user','${u.id}', '${encodeURIComponent(JSON.stringify(u))}')">✏️</button> <button class="btn btn-danger btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminDelete('user','${u.id}','${esc(u.username).replace(/'/g, "\\\\'")}')">🗑️</button></td></tr>`).join('')}</tbody>
          </table></div>
        `:''}
      </div>`;'''
new_body = '''<td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${u.id}</td><td><button class="btn btn-outline btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminEdit('user','${u.id}', '${encodeURIComponent(JSON.stringify(u))}')">✏️</button> <button class="btn btn-danger btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminDelete('user','${u.id}','${esc(u.username).replace(/'/g, "\\\\'")}')">🗑️</button></td></tr>`).join('')}</tbody>
          </table></div>
        `:''}

        ${tab==='tournaments'?`
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
              <button class="btn btn-primary" onclick="adminAdd('tournament')">+ Thêm Giải Đấu</button>
            </div>
          </div></div>
          <div id="admin-t-list" style="margin-top:20px;">Đang tải danh sách giải...</div>
        `:''}
      </div>`;
      
      if(tab==='tournaments'){
        apiFetch('/record-board/tournaments').then(tList=>{
          if(tList && tList.length){
            $('admin-t-list').innerHTML = '<div class="card" style="overflow:hidden"><table class="data-table"><thead><tr><th>Tên giải</th><th>Map</th><th>Bắt đầu</th><th>Kết thúc</th><th>Hành động</th></tr></thead><tbody>' + tList.map(t=>`<tr><td style="font-weight:600">${esc(t.name)}</td><td>${esc(maps.find(m=>m.id===t.map_id)?.name||t.map_id)}</td><td>${dateStr(t.start_time)}</td><td>${dateStr(t.end_time)}</td><td><button class="btn btn-outline btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminEdit('tournament','${t.id}', '${encodeURIComponent(JSON.stringify(t))}')">✏️</button> <button class="btn btn-danger btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminDelete('tournament','${t.id}','${esc(t.name).replace(/'/g, "\\\\'")}')">🗑️</button></td></tr>`).join('') + '</tbody></table></div>';
          }else{
            $('admin-t-list').innerHTML = '<div class="empty">Chưa có giải đấu nào.</div>';
          }
        }).catch(e=>$('admin-t-list').innerHTML = 'Lỗi tải: ' + e.message);
      }
'''
if "tab==='tournaments'" not in js:
    js = js.replace(old_body, new_body)

# 3. Patch adminAdd logic for Tournaments
old_adminAdd = '''        } else if(type==='pets') {
          const n=$('pn').value; if(!n){toast('Vui lòng nhập tên','error');return;}
          await apiFetch('/admin/pets',{method:'POST',body:JSON.stringify({name:n})});
        }'''
new_adminAdd = '''        } else if(type==='pets') {
          const n=$('pn').value; if(!n){toast('Vui lòng nhập tên','error');return;}
          await apiFetch('/admin/pets',{method:'POST',body:JSON.stringify({name:n})});
        } else if(type==='tournament') {
          const n=$('t_name').value, d=$('t_desc').value, m=$('t_map').value, s=$('t_start').value, e=$('t_end').value;
          if(!n || !m || !s || !e) { toast('Vui lòng điền đủ thông tin *','error'); return; }
          await apiFetch('/record-board/tournaments', {
            method:'POST', 
            body:JSON.stringify({name:n, description:d, map_id:m, start_time: new Date(s).toISOString(), end_time: new Date(e).toISOString()})
          });
        }'''
if "type==='tournament'" not in js:
    js = js.replace(old_adminAdd, new_adminAdd)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("done tournaments")
