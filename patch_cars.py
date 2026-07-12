import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Cars
old_cars = """<tbody>${cars.map(c=>`<tr><td style="font-weight:600">${esc(c.name)}</td><td><span class="badge badge-orange">${esc(c.car_class||'?')}</span></td><td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${c.id}</td></tr>`).join('')}</tbody>"""

new_cars = """<tbody>${cars.map(c=>`<tr><td style="font-weight:600">${esc(c.name)}</td><td><span class="badge badge-orange">${esc(c.car_class||'?')}</span></td><td style="font-family:monospace;font-size:0.7rem;color:var(--text-dim)">${c.id}</td><td><button class="btn btn-outline btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminEdit('car','${c.id}', '${encodeURIComponent(JSON.stringify(c))}')">✏️</button> <button class="btn btn-danger btn-sm" style="padding:2px 8px;font-size:0.7rem" onclick="adminDelete('car','${c.id}','${esc(c.name).replace(/'/g, "\\'")}')">🗑️</button></td></tr>`).join('')}</tbody>"""

js = js.replace(old_cars, new_cars)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("done")
