import re

with open('temp.js', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Update adminEdit to support shopItem
edit_shop = r"""  } else if(type==='shopItem') {
    let m = {value:'', icon:''};
    try { 
      let p = JSON.parse(item.metadata_value); 
      m.value = p.value || ''; 
      m.icon = p.icon || '';
    } catch(e) { m.value = item.metadata_value; }
    formHtml = `
      <div class="form-group"><label>Tên</label><input id="edit_name" class="form-input" value="${esc(item.name)}"/></div>
      <div class="form-group"><label>Mô tả</label><input id="edit_desc" class="form-input" value="${esc(item.description)}"/></div>
      <div class="form-group"><label>Giá (Z-Coins)</label><input id="edit_price" type="number" class="form-input" value="${item.price}"/></div>
      <div class="form-group"><label>URL Icon (Dán link Pinterest, Imgur...)</label><input id="edit_icon" class="form-input" value="${esc(m.icon)}"/></div>
      <input type="hidden" id="edit_rawmeta" value="${esc(m.value)}"/>
    `;
"""

pattern_edit = r"(\} else if\(type==='tournament'\) \{)"
c = re.sub(pattern_edit, edit_shop + r"  \1", c)


# 2. Update doAdminEdit to support shopItem
do_edit_shop = r"""      else if(type==='shopItem') {
        const m = {
          value: modal.querySelector('#edit_rawmeta').value,
          icon: modal.querySelector('#edit_icon').value
        };
        bodyData = {
          name: modal.querySelector('#edit_name').value,
          description: modal.querySelector('#edit_desc').value,
          price: parseInt(modal.querySelector('#edit_price').value),
          metadata_value: JSON.stringify(m)
        };
      }
"""

pattern_do_edit = r"(      else if\(type==='tournament'\) bodyData = \{)"
c = re.sub(pattern_do_edit, do_edit_shop + r"\1", c)


# 3. Fix endpoint for shopItem in doAdminEdit
# it already has `if(type==='tournament') endpoint = ...;`
# we need to add `if(type==='shopItem') endpoint = ...;`
pattern_endpoint = r"(if\(type==='tournament'\) endpoint = `/record-board/tournaments/\$\{id\}`;)"
c = re.sub(pattern_endpoint, r"\1\n      if(type==='shopItem') endpoint = `/shop/admin/items/${id}`;", c)


# 4. Add the edit button in the shop items list in adminTab
# Old: <td><button class="btn btn-danger btn-sm" ... onclick="adminDelete('shopItem'...
# New: <td><button class="btn btn-outline btn-sm" onclick="adminEdit('shopItem'...">Sửa</button> <button class="btn btn-danger...
pattern_admin_list = r"(<td>)(<button class=\"btn btn-danger btn-sm\"[^>]*onclick=\"adminDelete\('shopItem')"
new_admin_list = r"\1<button class=\"btn btn-outline btn-sm\" style=\"padding:2px 8px;font-size:0.7rem;margin-right:5px;\" onclick=\"adminEdit('shopItem','${s.id}', '${encodeURIComponent(JSON.stringify(s))}')\">✏️</button>\2"
c = re.sub(pattern_admin_list, new_admin_list, c)


with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch 10 applied!")
