import io

with io.open('temp.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Look for the start of the users fetch in renderTab
start_idx = content.find('apiFetch(\'/users\').then(users => {')
end_idx = content.find('});', start_idx) + 3

if start_idx != -1:
    new_js = '''apiFetch('/users').then(users => {
            const el = document.getElementById('tournament_users_checkboxes');
            if(el) {
                const nonAdmins = users.filter(u => u.role !== 'ADMIN');
                window._tournamentUsers = nonAdmins;
                
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
                };
            }
        });'''
    content = content[:start_idx] + new_js + content[end_idx:]
    with io.open('temp.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched temp.js JS successfully")
else:
    print("Could not find start idx")
