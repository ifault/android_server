import uuid
from contextlib import asynccontextmanager
import os
import logging
from faker import Faker
from fastapi import FastAPI
from tortoise import fields, models, Tortoise
from tortoise.contrib.fastapi import register_tortoise
from api import api_router
from ws import ws_router
from models import Account

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)


@asynccontextmanager
async def lifespan(fapp: FastAPI):
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",
        modules={"models": ["models"]},
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


app = FastAPI(lifespan=lifespan)
register_tortoise(app)


@app.get("/")
async def root():
    fake = Faker()
    for i in range(10):
        account = Account(
            uuid=str(uuid.uuid4()),
            username=f"test{i}",
            password=f"test{i}",
            status=-1,
            orderStr=f"test{i}",
            create_time="2024-04-06",
            pay_time="2024-04-06",
            details="很多个"
        )
        await account.save()
    return {"message": "Hello World"}


app.include_router(api_router, prefix="/api")
app.include_router(ws_router, prefix="/ws")
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.getenv("HOST"), port=1234)
