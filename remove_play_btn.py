with open('temp.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<div class="play-btn" title="Xem nhanh">&#128065;</div>', '')

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(content)
