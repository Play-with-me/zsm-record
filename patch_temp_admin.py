import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Patch renderAdmin tabs
old_tabs = '''          <button class="tab-btn${tab==='pets'?' active':''}" onclick="adminTab('pets')">Pets (${pets.length})</button>
          <button class="tab-btn${tab==='users'?' active':''}" onclick="adminTab('users')">Tài khoản (${users.length})</button>'''

new_tabs = '''          <button class="tab-btn${tab==='pets'?' active':''}" onclick="adminTab('pets')">Pets (${pets.length})</button>
          <button class="tab-btn${tab==='users'?' active':''}" onclick="adminTab('users')">Tài khoản (${users.length})</button>
          <button class="tab-btn${tab==='tournaments'?' active':''}" onclick="adminTab('tournaments')">Giải đấu</button>'''

js = js.replace(old_tabs, new_tabs)

# 2. Patch renderAdmin body
old_body = '''<td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${u.id}</td></tr>`).join('')}</tbody>
          </table></div>
        `:''}
      </div>`;
    }'''

new_body = '''<td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${u.id}</td></tr>`).join('')}</tbody>
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
            $('admin-t-list').innerHTML = '<div class="card" style="overflow:hidden"><table class="data-table"><thead><tr><th>Tên giải</th><th>Map</th><th>Bắt đầu</th><th>Kết thúc</th></tr></thead><tbody>' + tList.map(t=>`<tr><td style="font-weight:600">${esc(t.name)}</td><td>${esc(maps.find(m=>m.id===t.map_id)?.name||t.map_id)}</td><td>${dateStr(t.start_time)}</td><td>${dateStr(t.end_time)}</td></tr>`).join('') + '</tbody></table></div>';
          }else{
            $('admin-t-list').innerHTML = '<div class="empty">Chưa có giải đấu nào.</div>';
          }
        }).catch(e=>$('admin-t-list').innerHTML = 'Lỗi tải: ' + e.message);
      }
    }'''

js = js.replace(old_body, new_body)

# 3. Patch adminAdd logic
old_adminAdd = '''        } else {
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

js = js.replace(old_adminAdd, new_adminAdd)

# 4. Patch renderInsights
new_insights = '''
// --- Insights (Meta Siêu Xe & Pets) ---
async function renderInsights() {
  $('app').innerHTML = `<div class="animate-in"><div class="skeleton" style="height:400px;border-radius:12px"></div></div>`;
  try {
    const [carData, petData] = await Promise.all([
      apiFetch('/record-board/analytics/meta'),
      apiFetch('/record-board/analytics/meta-pets').catch(()=>[])
    ]);
    
    // Sort by count
    carData.sort((a,b) => b.count - a.count);
    petData.sort((a,b) => b.count - a.count);
    const maxCarCount = carData.length > 0 ? carData[0].count : 1;
    const maxPetCount = petData.length > 0 ? petData[0].count : 1;

    $('app').innerHTML = `
      <div class="animate-in fade-in slide-in">
        <div class="section-header" style="text-align:center; margin-bottom:40px;">
          <h2 style="font-size:2.5rem; text-shadow:var(--neon-glow-cyan);">📊 Meta Thịnh Hành</h2>
          <p style="color:var(--text-secondary);margin-top:8px;">Thống kê top Siêu Xe và Pets được cộng đồng ưa chuộng nhất</p>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:32px;">
          
          <!-- Cars Column -->
          <div style="background:var(--card-bg); border-radius:var(--radius-lg); padding:32px; border:1px solid rgba(0, 255, 255, 0.2); box-shadow:0 0 20px rgba(0,255,255,0.05);">
            <h3 style="color:var(--neon-cyan); margin-bottom:24px; font-size:1.5rem; text-align:center;">🚗 Top Siêu Xe</h3>
            ${carData.length > 0 ? `
              <div style="display:flex; flex-direction:column; gap:20px;">
                ${carData.map((item, i) => `
                  <div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                      <div style="font-weight:bold; color:var(--text-primary);">
                        <span style="color:var(--text-secondary); margin-right:8px;">#${i+1}</span>
                        ${esc(item.car)}
                      </div>
                      <div style="font-size:0.9rem; color:var(--text-secondary);">${item.count} Lượt</div>
                    </div>
                    <div style="width:100%; height:12px; background:rgba(255,255,255,0.05); border-radius:6px; overflow:hidden;">
                      <div style="height:100%; width:${(item.count / maxCarCount) * 100}%; background:linear-gradient(90deg, var(--neon-blue), var(--neon-cyan)); border-radius:6px; transition:width 1s ease-in-out;"></div>
                    </div>
                  </div>
                `).join('')}
              </div>
            ` : '<div class="empty">Chưa có dữ liệu.</div>'}
          </div>

          <!-- Pets Column -->
          <div style="background:var(--card-bg); border-radius:var(--radius-lg); padding:32px; border:1px solid rgba(255, 107, 158, 0.2); box-shadow:0 0 20px rgba(255,107,158,0.05);">
            <h3 style="color:var(--neon-pink); margin-bottom:24px; font-size:1.5rem; text-align:center;">🐉 Top Pets</h3>
            ${petData.length > 0 ? `
              <div style="display:flex; flex-direction:column; gap:20px;">
                ${petData.map((item, i) => `
                  <div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                      <div style="font-weight:bold; color:var(--text-primary);">
                        <span style="color:var(--text-secondary); margin-right:8px;">#${i+1}</span>
                        ${esc(item.pet)}
                      </div>
                      <div style="font-size:0.9rem; color:var(--text-secondary);">${item.count} Lượt</div>
                    </div>
                    <div style="width:100%; height:12px; background:rgba(255,255,255,0.05); border-radius:6px; overflow:hidden;">
                      <div style="height:100%; width:${(item.count / maxPetCount) * 100}%; background:linear-gradient(90deg, #ff8c00, var(--neon-pink)); border-radius:6px; transition:width 1s ease-in-out;"></div>
                    </div>
                  </div>
                `).join('')}
              </div>
            ` : '<div class="empty">Chưa có dữ liệu.</div>'}
          </div>

        </div>
      </div>
    `;
  } catch(e) {
    $('app').innerHTML = `<div class="empty">Lỗi tải dữ liệu meta: ${e.message}</div>`;
  }
}
'''

# Replace renderInsights completely using regex
js = re.sub(r'async function renderInsights\(\) \{.*?\n// --- Tournaments', new_insights + '\n// --- Tournaments', js, flags=re.DOTALL)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
