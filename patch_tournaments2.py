import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Inject the tournaments body
stable_marker = r"</table></div>`:''}" + "\n" + r"      </div>`;"

tournaments_html = r"""
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
"""

if "tab==='tournaments'?" not in js:
    js = js.replace(stable_marker, stable_marker.replace("      </div>`;", tournaments_html + "      </div>`;"))

# 2. Inject fetch and render for tournament list
fetch_marker = "window.adminTab=(t)=>{ tab=t; renderTab(); };"
fetch_code = r"""
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
"""

if "apiFetch('/record-board/tournaments')" not in js:
    js = js.replace(fetch_marker, fetch_code + "\n    " + fetch_marker)

# 3. Inject user Edit and Delete
# We can just keep existing adminEditUser but let's replace users table to use our adminEdit and adminDelete
# Actually user table already has ✏️ Sửa button for adminEditUser which is old function, let's keep it but add Delete button

old_users_row = r"`<tr>\n            <td>${u.avatar?`<img src=\"${esc(optimizedImage(u.avatar, 48))}\" width=\"28\" height=\"28\" loading=\"lazy\" \ndecoding=\"async\" style=\"width:28px;height:28px;border-radius:50%;object-fit:cover\"/>`:`<div class=\"avatar \navatar-sm\">${esc(u.username[0].toUpperCase())}</div>`}</td>\n            <td style=\"font-weight:600\">${esc(u.username)}</td>\n            <td style=\"color:var(--text-dim)\">${esc(u.email)}</td>\n            <td><span class=\"badge ${u.role==='ADMIN'?'badge-red':'badge-blue'}\">${esc(u.role)}</span></td>\n            <td style=\"font-family:monospace;font-size:0.7rem;color:var(--text-dim)\">${u.id}</td>\n            <td><button class=\"btn btn-sm btn-outline\" onclick=\"adminEditUser('${u.id}', '${esc(u.username)}', \n'${esc(u.email)}')\">&#9998; Sửa</button></td>\n          </tr>`"

new_users_row = r"`<tr>\n            <td>${u.avatar?`<img src=\"${esc(optimizedImage(u.avatar, 48))}\" width=\"28\" height=\"28\" loading=\"lazy\" \ndecoding=\"async\" style=\"width:28px;height:28px;border-radius:50%;object-fit:cover\"/>`:`<div class=\"avatar \navatar-sm\">${esc(u.username[0].toUpperCase())}</div>`}</td>\n            <td style=\"font-weight:600\">${esc(u.username)}</td>\n            <td style=\"color:var(--text-dim)\">${esc(u.email)}</td>\n            <td><span class=\"badge ${u.role==='ADMIN'?'badge-red':'badge-blue'}\">${esc(u.role)}</span></td>\n            <td style=\"font-family:monospace;font-size:0.7rem;color:var(--text-dim)\">${u.id}</td>\n            <td style=\"display:flex;gap:4px;\"><button class=\"btn btn-sm btn-outline\" onclick=\"adminEditUser('${u.id}', '${esc(u.username)}', \n'${esc(u.email)}')\">&#9998; Sửa</button><button class=\"btn btn-danger btn-sm\" style=\"padding:2px 8px;font-size:0.7rem\" onclick=\"adminDelete('user','${u.id}','${esc(u.username).replace(/'/g, \"\\\\'\")}')\">🗑️</button></td>\n          </tr>`"
js = js.replace(old_users_row, new_users_row)


with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("done")
