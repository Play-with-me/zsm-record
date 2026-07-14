import re
content = open('temp.js', encoding='utf-8').read()
content = content.replace('</h3>`\n            <p style="color:var(--text-dim)', '</h3>\n            <p style="color:var(--text-dim)')
content = content.replace('</h3>`\r\n            <p style="color:var(--text-dim)', '</h3>\r\n            <p style="color:var(--text-dim)')
open('temp.js', 'w', encoding='utf-8').write(content)
print("Fixed!")
