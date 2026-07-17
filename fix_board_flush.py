import re

with open(r'backend\app\routers\board.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = '''                    next_match_id=next_mid
                )
                db.add(m)
                
        await db.commit()'''

new_code = '''                    next_match_id=next_mid
                )
                db.add(m)
            await db.flush()
                
        await db.commit()'''

content = content.replace(old_code, new_code)

with open(r'backend\app\routers\board.py', 'w', encoding='utf-8') as f:
    f.write(content)
print(" Fixed board.py flush!\)
