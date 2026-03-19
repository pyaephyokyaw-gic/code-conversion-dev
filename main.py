# main.py
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from models.organization import Org
app = FastAPI()


# @app.get("/")
# async def root():
#     return {"status": "Application is running without checking DB schema."}


# @app.post("/insert")
# async def create_org(name: str, db: AsyncSession = Depends(get_db)):
#     new_org = Org(name=name)
#     db.add(new_org)
#     await db.commit()
#     return new_org
