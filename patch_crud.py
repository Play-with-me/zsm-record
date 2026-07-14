import re
with open('backend/app/crud.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r"if\s+user\.coins\s*<\s*item\.price:\s*return\s+False,\s*\"[^\"]*Z-Coins\"\s*user\.coins\s*-=\s*item\.price"

def repl(m):
    return """if user.role != 'ADMIN':
          if user.coins < item.price:
              return False, "Không đủ Z-Coins"
          user.coins -= item.price"""

new_content, count = re.subn(pattern, repl, content)
if count > 0:
    with open('backend/app/crud.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Patched successfully")
else:
    print("Not found")
