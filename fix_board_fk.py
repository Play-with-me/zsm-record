import re

with open(r'backend\app\routers\board.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I need to change:
# for r in range(1, total_rounds + 1):
# To:
# for r in range(total_rounds, 0, -1):
# But there are two loops! The first one just populates matches_dict, order doesn't matter.
# The second one creates the objects and adds to db!
# If I reverse the second loop, it will insert round total_rounds first, which has next_mid=None.
# Then round total_rounds-1 will point to round total_rounds which is already inserted!

old_code = '''        for r in range(1, total_rounds + 1):
            matches_in_round = bracket_size // (2 ** r)
            for i in range(matches_in_round):
                mid = matches_dict[(r, i)]'''

new_code = '''        # Reverse order to satisfy PostgreSQL foreign key constraints
        for r in range(total_rounds, 0, -1):
            matches_in_round = bracket_size // (2 ** r)
            for i in range(matches_in_round):
                mid = matches_dict[(r, i)]'''

content = content.replace(old_code, new_code)

with open(r'backend\app\routers\board.py', 'w', encoding='utf-8') as f:
    f.write(content)
print(" Fixed board.py FK order!\)
