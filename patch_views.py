import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

pattern = r'(<span class="count-up" data-val="\$\{video\.views\|\|0\}">)0(</span>)'
js = re.sub(pattern, r'\g<1>${video.views||0}\g<2>', js)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
