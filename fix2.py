with open('temp.js', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('\\"', '"').replace('\\$', '$')
with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(c)
