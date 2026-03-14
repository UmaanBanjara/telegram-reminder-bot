from app.models.app_models import Users , Remainder
import asyncio
from app.database.connection_config import base , engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)
        print('TABLES CREATED SUCCESSFULLY')


if __name__ == '__main__':
    asyncio.run(create_tables())