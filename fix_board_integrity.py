import re

with open(r'backend\app\routers\board.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = '''    new_t = models.Tournament(
        name=t.name,
        description=t.description,
        map_id=t.map_id,
        start_time=t.start_time,
        end_time=t.end_time,
        is_active=t.is_active,
        format=t.format,
        status=models.TournamentStatusEnum.ONGOING if len(t.participants) > 1 else models.TournamentStatusEnum.DRAFT
    )
    db.add(new_t)
    await db.commit()
    await db.refresh(new_t)'''

new_code = '''    new_t = models.Tournament(
        name=t.name,
        description=t.description,
        map_id=t.map_id,
        start_time=t.start_time,
        end_time=t.end_time,
        is_active=t.is_active,
        format=t.format,
        status=models.TournamentStatusEnum.ONGOING if len(t.participants) > 1 else models.TournamentStatusEnum.DRAFT
    )
    db.add(new_t)
    try:
        await db.commit()
        await db.refresh(new_t)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=" Tên gi?i d?u dã t?n t?i ho?c d? li?u không h?p l?\)'''

content = content.replace(old_code, new_code)

with open(r'backend\app\routers\board.py', 'w', encoding='utf-8') as f:
 f.write(content)
print(\Fixed board.py integrity!\)
