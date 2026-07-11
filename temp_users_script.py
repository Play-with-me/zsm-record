import re

# Update users.py
with open('backend/app/routers/users.py', 'r', encoding='utf-8') as f:
    c = f.read()

old_logic = '''    now = datetime.utcnow()
    if current_user.last_avatar_update:
        diff = (now - current_user.last_avatar_update).total_seconds()
        if diff < 86400:
            raise HTTPException(status_code=400, detail="Bạn chỉ có thể đổi ảnh đại diện 1 lần mỗi ngày.")'''

new_logic = '''    now = datetime.utcnow()
    if current_user.last_avatar_update:
        diff = (now - current_user.last_avatar_update).total_seconds()
        if diff < 86400:
            if current_user.avatar_update_count >= 5:
                raise HTTPException(status_code=400, detail="Bạn đã hết lượt đổi ảnh (tối đa 5 lần/ngày).")
            else:
                current_user.avatar_update_count += 1
        else:
            current_user.avatar_update_count = 1
    else:
        current_user.avatar_update_count = 1'''

if old_logic in c:
    c = c.replace(old_logic, new_logic)
else:
    print('Failed to find old logic in users.py')

with open('backend/app/routers/users.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('Updated users.py')
