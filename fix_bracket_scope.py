import io
import re

with io.open(r'temp.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the renderTournamentBracket function
start_idx = content.find('async function renderTournamentBracket(tid)')
if start_idx != -1:
    end_idx = content.find('// --- ADMIN CRUD LOGIC ---', start_idx)
    func_code = content[start_idx:end_idx]
    
    # Remove it from inside renderAdmin
    content = content[:start_idx] + content[end_idx:]
    
    # Append it to the global scope at the bottom, just before router()
    router_idx = content.find('// --- ROUTER')
    content = content[:router_idx] + func_code + '\n' + content[router_idx:]

with io.open(r'temp.js', 'w', encoding='utf-8') as f:
    f.write(content)
print(" Moved renderTournamentBracket to global scope!\)
