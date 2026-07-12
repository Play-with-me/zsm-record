import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Add tournament tab button
js = re.sub(
    r'(<button class="tab-btn\$\{tab===\'users\'\?\' active\':\'\'\}" onclick="adminTab\(\'users\'\)">.*?)(</div></div>)',
    r'\1\n          <button class="tab-btn${tab===\'tournaments\'?\' active\':\'\'}" onclick="adminTab(\'tournaments\')">Giải đấu</button>\n        \2',
    js
)

# 2. Add tournaments logic right after users logic
users_end = r"</table></div>`:''}\n      </div>`;"
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
js = js.replace(users_end, users_end.replace("      </div>`;", tournaments_html + "      </div>`;"))

# 3. Add adminAdd for tournaments
js = re.sub(
    r'(} else if\(type===\'pets\'\) \{.*?\})',
    r'\1 else if(type===\'tournament\') {\n          const n=$(\'t_name\').value, d=$(\'t_desc\').value, m=$(\'t_map\').value, s=$(\'t_start\').value, e=$(\'t_end\').value;\n          if(!n || !m || !s || !e) { toast(\'Vui lòng điền đủ thông tin *\',\'error\'); return; }\n          await apiFetch(\'/record-board/tournaments\', { method:\'POST\', body:JSON.stringify({name:n, description:d, map_id:m, start_time: new Date(s).toISOString(), end_time: new Date(e).toISOString()}) });\n        }',
    js,
    flags=re.DOTALL
)

# 4. Add the delete button for users
js = re.sub(
    r'(<td><button class="btn btn-sm btn-outline" onclick="adminEditUser\(\'\$\{u\.id\}\', \'\$\{esc\(u\.username\)\}\', \n?\'\$\{esc\(u\.email\)\}\'\)">.*?</button>)(</td>)',
    r'\1 <button class="btn btn-danger btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminDelete(\'user\',\'${u.id}\',\'${esc(u.username).replace(/\'/g, \\"\\\\\'\\")}\')">🗑️</button>\2',
    js
)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("done")
