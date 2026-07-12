import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace(r'\"\\\'\"', r'"\\\'"')

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
