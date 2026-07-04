with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(lines[:539])
    f.write('<script src="temp.js?v=2"></script>\n</body>\n</html>\n')
