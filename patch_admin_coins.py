import asyncio
from backend.app.database import AsyncSessionLocal
from backend.app.models import User
from sqlalchemy.future import select

async def main():
    async with AsyncSessionLocal() as session:
        # Find the admin user
        result = await session.execute(select(User).filter(User.role == 'ADMIN'))
        admin_user = result.scalars().first()
        if admin_user:
            admin_user.coins = 9999999999999
            await session.commit()
            print("Admin coins updated to 9999999999999!")
        else:
            print("Admin user not found!")

if __name__ == "__main__":
    asyncio.run(main())
