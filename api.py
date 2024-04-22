import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from tortoise.expressions import Q
from tortoise.tortoise import Tortoise

from models import fake_accounts, Account, RequestData

api_router = APIRouter()


@api_router.get("/accounts")
async def get_accounts():
    accounts = await Account.filter(~Q(status=-1)).values()
    results = {
        "errorMsg": "",
        "errorCode": "0",
        "data": {"items": list(accounts)}
    }
    print(len(accounts))
    return JSONResponse(content=results, status_code=200)


@api_router.post("/accounts")
async def add_accounts(data: RequestData):
    username = process_string(data.username)
    password = data.password
    print(username, password)
    return JSONResponse(content={'errorCode': 0}, status_code=200)


@api_router.post("/accounts/del")
async def delete_accounts():
    print("delete all accounts")
    return JSONResponse(content={'errorCode': 0}, status_code=200)


@api_router.post("/pay/{uuid}")
async def pay(uuid: str):
    print("pay account", uuid)
    await Account.filter(uuid=uuid.strip()).update(status=-1)
    return JSONResponse(content={'errorCode': 0}, status_code=200)


def process_string(string):
    string = string.replace(" ", "").replace("\n", "").replace("\r", "")
    string = string.replace("，", ",")
    array = string.split(",")
    return array
