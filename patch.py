import re

# 1. Fix temp.js
c = open('temp.js', 'r', encoding='utf-8').read()

# Fix adminEditUser call
c = c.replace(
    "onclick=\"adminEditUser('${u.id}', '${esc(u.username)}', '${esc(u.email)}')\"",
    "onclick=\"adminEditUser('${u.id}', '${esc(u.username)}', '${esc(u.email)}', ${u.coins})\""
)

# Fix Leaderboard missing table (rest = board instead of rest = board.slice(3))
c = re.sub(
    r"let rest = board\.slice\(3\);",
    "let rest = board;",
    c
)

open('temp.js', 'w', encoding='utf-8').write(c)

# 2. Fix index.html (Navbar styling)
html = open('index.html', 'r', encoding='utf-8').read()
html = re.sub(
    r"\.navbar \{([^}]+)\}",
    r".navbar { position:sticky; top:0; z-index:100; background:rgba(10,12,18,0.85); backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px); border-bottom:1px solid rgba(212,175,55,0.4); box-shadow:0 4px 20px rgba(0,0,0,0.5); }",
    html
)
html = re.sub(
    r"\.nav-link \{([^}]+)\}",
    r".nav-link { font-weight:700; color:var(--text-muted); text-decoration:none; padding:16px 12px; display:flex; flex-direction:column; align-items:center; gap:3px; position:relative; transition:var(--transition); font-family:'Rajdhani', sans-serif; font-size:1.05rem; letter-spacing:0.03em; }",
    html
)
html = re.sub(
    r"\.nav-link:hover \{([^}]+)\}",
    r".nav-link:hover { color:var(--gold); }",
    html
)
html = re.sub(
    r"\.nav-link\.active \{([^}]+)\}",
    r".nav-link.active { color:var(--gold); } \n    .nav-link.active::after { content:''; position:absolute; bottom:-1px; left:0; width:100%; height:3px; background:var(--gold); box-shadow:0 -2px 10px rgba(212,175,55,0.6); }",
    html
)

open('index.html', 'w', encoding='utf-8').write(html)
