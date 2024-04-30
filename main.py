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
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

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


@app.exception_handler(HTTPException)
async def handle_authentication_exception(request: Request, exc: HTTPException):
    if exc.status_code == 403:
        return JSONResponse(content={"code": -1, "message": "密钥验证失败,请重新登录获取"}, status_code=exc.status_code)
    return JSONResponse(content={"code": -1, "message": str(exc.detail)}, status_code=exc.status_code)


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
