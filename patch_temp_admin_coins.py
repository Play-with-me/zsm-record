import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update the call
call_target = r"onclick=\"adminEditUser('${u.id}', '${esc(u.username)}', '${esc(u.email)}')\""
call_replacement = r"onclick=\"adminEditUser('${u.id}', '${esc(u.username)}', '${esc(u.email)}', ${u.coins || 0})\""
js = js.replace(call_target, call_replacement)

# 2. Update the definition
def_target = r"window.adminEditUser = function(id, curName, curEmail) {"
def_replacement = r"window.adminEditUser = function(id, curName, curEmail, curCoins) {"
js = js.replace(def_target, def_replacement)

# 3. Update the form
form_target = r"""        <div class="form-group"><label class="form-label">Email</label><input class="form-input" name="em" value="${curEmail}" required/></div>"""
form_replacement = r"""        <div class="form-group"><label class="form-label">Email</label><input class="form-input" name="em" value="${curEmail}" required/></div>
        <div class="form-group"><label class="form-label">Z-Coins</label><input class="form-input" name="coins" type="number" value="${curCoins}" required/></div>"""
js = js.replace(form_target, form_replacement)

# 4. Update the fetch payload
fetch_target = r"""await apiFetch(`/users/${id}/admin`, {method:'PUT', body:JSON.stringify({username: e.target.un.value, email: e.target.em.value})});"""
fetch_replacement = r"""await apiFetch(`/users/${id}/admin`, {method:'PUT', body:JSON.stringify({username: e.target.un.value, email: e.target.em.value, coins: parseInt(e.target.coins.value)})});"""
js = js.replace(fetch_target, fetch_replacement)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("done")
