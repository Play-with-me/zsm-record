import re
with open('temp.js', 'r', encoding='utf-8') as f:
    content = f.read()
m = re.search(r'function renderAdmin\(\) \{([\s\S]*?)\n\}\n', content)
if m:
    with open('admin_temp.js', 'w', encoding='utf-8') as f2:
        f2.write(m.group(1))
