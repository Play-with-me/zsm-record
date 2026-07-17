from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import engine, Base
import asyncio

async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(setup_db())

client = TestClient(app)

from backend.app.auth import create_access_token
from backend.app.models import RoleEnum
from backend.app.database import AsyncSessionLocal
from backend.app import models

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = models.User(username='admin_test2', email='admin2@test.com', password_hash='xx', role=RoleEnum.ADMIN)
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        return admin.id

admin_id = asyncio.run(create_admin())
token = create_access_token(data={'sub': admin_id})

response = client.post(
    '/api/v1/record-board/tournaments',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'name': 'Test Tourny API 2',
        'description': 'test',
        'participants': [admin_id, admin_id]
    }
)
print('STATUS:', response.status_code)
print('BODY:', response.json())
