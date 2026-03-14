import os
from dotenv import load_dotenv
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine , AsyncSession
from sqlalchemy.orm import sessionmaker , declarative_base
from sqlalchemy import text


load_dotenv()
url = os.getenv('DATABASE_URL')
print(f'DATABASE URL IS : {url} ')
base = declarative_base()


engine = create_async_engine(url=url , echo=True)

mysession = sessionmaker(engine , expire_on_commit=False , class_=AsyncSession)

async def test_connection():
    try:
        async with mysession() as session:
            result = await session.execute(text('SELECT 1'))
            print('CONNECTION SUCCESSFULL', result)
    except Exception as e:
        print('SOMETHING WENT WRONG WHILE CONNECTING TO DATABASE')

if __name__ == '__main__':
    asyncio.run(test_connection())