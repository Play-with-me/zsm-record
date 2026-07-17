from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import engine, Base, AsyncSessionLocal
from backend.app import models
import asyncio

async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(setup_db())

client = TestClient(app)

from backend.app.auth import create_access_token

async def create_users():
    async with AsyncSessionLocal() as db:
        admin = models.User(username='admin_api5_b', email='a5_b@t.com', password_hash='xx', role=models.RoleEnum.ADMIN)
        db.add(admin)
        users = [models.User(username=f'u_api5_b_{i}', email=f'u_api5_b_{i}@t.com', password_hash='xx', role=models.RoleEnum.USER) for i in range(5)]
        db.add_all(users)
        await db.commit()
        await db.refresh(admin)
        for u in users:
            await db.refresh(u)
        return admin.username, [u.id for u in users]

admin_uname, user_ids = asyncio.run(create_users())
token = create_access_token(data={'sub': admin_uname})

response = client.post(
    '/api/v1/record-board/tournaments',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'name': 'Test API 5 B',
        'description': 'test 5',
        'participants': user_ids
    }
)
print('STATUS:', response.status_code)
print('BODY:', response.json())
