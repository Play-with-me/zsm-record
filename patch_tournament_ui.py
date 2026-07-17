import re

with open('temp.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace HTML template for tournament tab
old_html = r'''        tab==='tournaments'\?`
            <div class="card"><div class="card-body">
              <div style="font-size:0.85rem;font-weight:700;margin-bottom:10px">Thêm Giải Đấu Mới</div>
              <div class="admin-add-form" style="display:flex;flex-direction:column;gap:12px;">
                <div class="form-group"><label class="form-label">Tên giải đấu \*</label><input class="form-input" id="t_name" placeholder="VD: Mùa giải Mùa Hè"/></div>
                <div class="form-group"><label class="form-label">Mô tả</label><input class="form-input" id="t_desc" placeholder="Giải thưởng 100k"/></div>
                <div id="tournament_users_checkboxes" style="max-height: 200px; overflow-y: auto; background: rgba\(0,0,0,0\.2\); padding: 10px; border-radius: 5px;">Đang tải danh sách người chơi...</div>
                <button class="btn btn-primary btn-sm" onclick="adminAdd\('tournament'\)">\+ Tạo Giải & Bốc Thăm \(Random\) Ngay</button>
              </div>
            </div></div>
            <div id="admin-t-list" style="margin-top:20px;">Đang tải danh sách giải...</div>
          `:''\}'''

new_html = r'''        tab==='tournaments'?`
            <div class="card" style="background: linear-gradient(145deg, rgba(20,20,25,0.9), rgba(30,30,40,0.9)); border: 1px solid rgba(var(--primary-rgb, 255,215,0), 0.3); box-shadow: 0 8px 32px rgba(0,0,0,0.5);">
              <div class="card-body">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom: 20px;">
                  <div style="width: 40px; height: 40px; border-radius: 8px; background: linear-gradient(135deg, var(--primary), #ff8c00); display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">🏆</div>
                  <div>
                    <div style="font-size:1.2rem; font-weight:800; color: #fff; text-transform: uppercase; letter-spacing: 1px;">Khởi Tạo Giải Đấu</div>
                    <div style="font-size:0.75rem; color: var(--text-dim);">Thiết lập giải đấu chuyên nghiệp và bốc thăm tự động</div>
                  </div>
                </div>
                
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                  <div class="form-group">
                    <label class="form-label" style="color:var(--primary); font-weight:600;">Tên giải đấu *</label>
                    <input class="form-input" id="t_name" placeholder="VD: Mùa giải Mùa Hè 2026" style="background: rgba(0,0,0,0.3); border-color: rgba(255,255,255,0.1); font-size:1rem; padding:10px;"/>
                  </div>
                  <div class="form-group">
                    <label class="form-label" style="color:var(--primary); font-weight:600;">Mô tả / Thể thức</label>
                    <input class="form-input" id="t_desc" placeholder="Loại trực tiếp - Phần thưởng 100k" style="background: rgba(0,0,0,0.3); border-color: rgba(255,255,255,0.1); font-size:1rem; padding:10px;"/>
                  </div>
                </div>
                
                <div style="margin-bottom: 20px;">
                  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <label class="form-label" style="color:var(--primary); font-weight:600; margin:0;">Tuyển thủ tham gia (<span id="t_selected_count">0</span>)</label>
                    <button class="btn btn-outline btn-sm" onclick="toggleAllTournamentUsers()" style="font-size:0.7rem;">Chọn tất cả</button>
                  </div>
                  <div id="tournament_users_checkboxes" style="display:grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; max-height: 250px; overflow-y: auto; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="text-align:center; padding:20px; color:var(--text-dim); grid-column: 1 / -1;">Đang tải danh sách người chơi... <div class="spinner" style="display:inline-block; margin-left:10px;"></div></div>
                  </div>
                </div>
                
                <button class="btn btn-primary" onclick="adminAdd('tournament')" style="width: 100%; padding: 12px; font-size: 1.1rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 4px 15px rgba(var(--primary-rgb, 255,215,0), 0.4); border-radius: 8px;">
                  ⚔️ TẠO GIẢI & BỐC THĂM TỰ ĐỘNG
                </button>
              </div>
            </div>
            
            <div style="margin-top: 30px; display:flex; align-items:center; gap:10px; margin-bottom:15px;">
              <div style="width:4px; height:20px; background:var(--primary); border-radius:2px;"></div>
              <h3 style="margin:0; font-size:1.1rem;">DANH SÁCH GIẢI ĐẤU</h3>
            </div>
            <div id="admin-t-list">
              <div style="text-align:center; padding:40px;"><div class="spinner"></div></div>
            </div>
          `:''}'''

content = re.sub(old_html, new_html, content)


# Replace JS script for populating the grid
old_js = r'''                  el\.innerHTML = '<div style=\"margin-bottom:8px;font-size:0\.9rem\"><b>Chọn Tuyển Thủ Tham Gia:</b></div>' \+ \n                    nonAdmins\.map\(u => `<label style=\"display:flex;align-items:center;gap:8px;margin-bottom:5px;cursor:pointer;\"><input type=\"checkbox\" class=\"t_user_checkbox\" value=\"\$\{u\.id\}\"/> \$\{esc\(u\.username\)\}</label>`\)\.join\(''\);'''

new_js = r'''                  window._tournamentUsers = nonAdmins;
                  
                  // UI grid generation
                  el.innerHTML = nonAdmins.map(u => {
                      const uname = u.username || u.name || 'Unknown';
                      
                      return `
                      <div class="t-user-card" id="tcard_${u.id}" onclick="toggleTournamentUser('${u.id}')" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 8px 12px; display: flex; align-items: center; gap: 10px; cursor: pointer; transition: all 0.2s; user-select: none;">
                          <div class="t-chk" id="tchk_${u.id}" style="min-width: 18px; height: 18px; border-radius: 4px; border: 2px solid rgba(255,255,255,0.3); display: flex; align-items: center; justify-content: center; transition: all 0.2s;"></div>
                          <div style="width: 24px; height: 24px; border-radius: 50%; background: #333; overflow: hidden; display: flex; align-items: center; justify-content: center; font-size:10px; color:#aaa; font-weight:bold;">${uname.substring(0,2).toUpperCase()}</div>
                          <div style="font-weight: 600; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1;">${esc(uname)}</div>
                      </div>
                      <input type="checkbox" class="t_user_checkbox" value="${u.id}" id="tcb_${u.id}" style="display:none;" />
                      `;
                  }).join('');
                  
                  // Helper function for UI toggle
                  window.toggleTournamentUser = function(uid) {
                      const cb = document.getElementById('tcb_' + uid);
                      const card = document.getElementById('tcard_' + uid);
                      const chk = document.getElementById('tchk_' + uid);
                      if(!cb || !card || !chk) return;
                      
                      cb.checked = !cb.checked;
                      
                      if(cb.checked) {
                          card.style.borderColor = 'var(--primary)';
                          card.style.background = 'rgba(255, 215, 0, 0.1)'; 
                          card.style.boxShadow = '0 0 10px rgba(255, 215, 0, 0.2)';
                          chk.style.borderColor = '#000';
                          chk.style.background = 'var(--primary)';
                          chk.innerHTML = '<span style="color:#000; font-size:12px; font-weight:bold;">✓</span>';
                      } else {
                          card.style.borderColor = 'rgba(255,255,255,0.1)';
                          card.style.background = 'rgba(255,255,255,0.03)';
                          card.style.boxShadow = 'none';
                          chk.style.borderColor = 'rgba(255,255,255,0.3)';
                          chk.style.background = 'transparent';
                          chk.innerHTML = '';
                      }
                      
                      // Update count
                      const count = document.querySelectorAll('.t_user_checkbox:checked').length;
                      const countEl = document.getElementById('t_selected_count');
                      if(countEl) countEl.textContent = count;
                  };
                  
                  window.toggleAllTournamentUsers = function() {
                      const allCbs = document.querySelectorAll('.t_user_checkbox');
                      const checkedCount = document.querySelectorAll('.t_user_checkbox:checked').length;
                      const shouldCheck = checkedCount < allCbs.length; // if not all are checked, check all. else uncheck all.
                      
                      allCbs.forEach(cb => {
                          if(cb.checked !== shouldCheck) {
                              window.toggleTournamentUser(cb.value);
                          }
                      });
                  };'''

content = re.sub(old_js, new_js, content)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(content)
