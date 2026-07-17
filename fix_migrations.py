import io
with io.open(r'backend\app\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Find the start of startup_event
start_idx = content.find('async def startup_event():')

# Replace the entire startup_event
old_startup = '''async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Try to add missing columns to avoid breaking if table already exists
        try:
            await conn.execute(text(" ALTER TABLE tournaments ADD COLUMN format VARCHAR 50 DEFAULT SINGLE \))
 except Exception:
 pass
 try:
 await conn.execute(text(\ALTER TABLE tournaments ADD COLUMN status VARCHAR 50 DEFAULT DRAFT \))
 except Exception:
 pass
 # Drop NOT NULL constraints that were modified in models.py
 try:
 await conn.execute(text(\ALTER TABLE tournaments ALTER COLUMN map_id DROP NOT NULL\))
 except Exception:
 pass
 try:
 await conn.execute(text(\ALTER TABLE tournaments ALTER COLUMN start_time DROP NOT NULL\))
 except Exception:
 pass
 try:
 await conn.execute(text(\ALTER TABLE tournaments ALTER COLUMN end_time DROP NOT NULL\))
 except Exception:
 pass
 
 try:
 pass
 await conn.execute(text(\ALTER TABLE maps ADD COLUMN difficulty INTEGER DEFAULT 1\))
 except Exception:
 pass

 try:
 async with engine.begin() as conn:
 await conn.execute(text(\ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE\))
 except Exception:
 pass

 try:
 async with engine.begin() as conn:
 await conn.execute(text(\ALTER TABLE users ADD COLUMN avatar_update_count INTEGER DEFAULT 0\))
 except Exception:
 pass

 try:
 async with engine.begin() as conn:
 await conn.execute(text(\ALTER TABLE users ADD COLUMN exp INTEGER DEFAULT 0\))
 except Exception:
 pass

 try:
 async with engine.begin() as conn:
 await conn.execute(text(\ALTER TABLE users ADD COLUMN coins INTEGER DEFAULT 0\))
 except Exception:
 pass

 try:
 await reseed_maps()
 except Exception as e:
 print(\Error reseeding maps:\, e)'''

new_startup = '''async def startup_event():
 # Run create_all in its own transaction
 async with engine.begin() as conn:
 await conn.run_sync(Base.metadata.create_all)
 
 # Helper to run raw SQL safely without aborting other migrations in PostgreSQL
 async def run_sql(sql):
 try:
 async with engine.begin() as conn:
 await conn.execute(text(sql))
 except Exception as e:
 pass

 await run_sql(\ALTER TABLE tournaments ADD COLUMN format VARCHAR 50 DEFAULT SINGLE \)
 await run_sql(\ALTER TABLE tournaments ADD COLUMN status VARCHAR 50 DEFAULT DRAFT \)
 
 await run_sql(\ALTER TABLE tournaments ALTER COLUMN map_id DROP NOT NULL\)
 await run_sql(\ALTER TABLE tournaments ALTER COLUMN start_time DROP NOT NULL\)
 await run_sql(\ALTER TABLE tournaments ALTER COLUMN end_time DROP NOT NULL\)
 
 await run_sql(\ALTER TABLE maps ADD COLUMN difficulty INTEGER DEFAULT 1\)
 await run_sql(\ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE\)
 await run_sql(\ALTER TABLE users ADD COLUMN avatar_update_count INTEGER DEFAULT 0\)
 await run_sql(\ALTER TABLE users ADD COLUMN exp INTEGER DEFAULT 0\)
 await run_sql(\ALTER TABLE users ADD COLUMN coins INTEGER DEFAULT 0\)
 
 try:
 await reseed_maps()
 except Exception as e:
 print(\Error reseeding maps:\, e)'''

content = content.replace(old_startup, new_startup)

with io.open(r'backend\app\main.py', 'w', encoding='utf-8') as f:
 f.write(content)
print(\Fixed main migrations!\)
