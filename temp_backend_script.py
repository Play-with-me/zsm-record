import re

# 1. Update models.py
with open('backend/app/models.py', 'r', encoding='utf-8') as f:
    c = f.read()
if 'avatar_update_count' not in c:
    c = c.replace('last_avatar_update = Column(DateTime, nullable=True)', 'last_avatar_update = Column(DateTime, nullable=True)\n    avatar_update_count = Column(Integer, default=0)')
    with open('backend/app/models.py', 'w', encoding='utf-8') as f:
        f.write(c)

# 2. Update schemas.py
with open('backend/app/schemas.py', 'r', encoding='utf-8') as f:
    c = f.read()
if 'avatar_update_count' not in c:
    c = c.replace('last_avatar_update: Optional[datetime] = None', 'last_avatar_update: Optional[datetime] = None\n    avatar_update_count: int = 0')
    with open('backend/app/schemas.py', 'w', encoding='utf-8') as f:
        f.write(c)

# 3. Update main.py startup
with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    c = f.read()
if 'ALTER TABLE users ADD COLUMN avatar_update_count' not in c:
    startup_block = """@app.on_event("startup")
async def startup_db_client():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    from sqlalchemy import text
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text("ALTER TABLE users ADD COLUMN avatar_update_count INTEGER DEFAULT 0"))
            await session.commit()
        except Exception:
            pass"""
    c = c.replace('async def startup_db_client():\n    async with engine.begin() as conn:\n        await conn.run_sync(models.Base.metadata.create_all)', startup_block)
    with open('backend/app/main.py', 'w', encoding='utf-8') as f:
        f.write(c)

print('Updated models, schemas, main')
