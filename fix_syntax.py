import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Fix the escaped quotes that broke JS syntax
js = js.replace(r'\"', '"')
# Fix the replace string
js = js.replace(r"\\\\'", r"\\'")

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
