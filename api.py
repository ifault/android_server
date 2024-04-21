import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from tortoise.expressions import Q

from models import fake_accounts, Account

api_router = APIRouter()


@api_router.get("/accounts")
async def get_accounts():
    accounts = await Account.filter(~Q(status=-1)).values()
    results = {
        "errorMsg": "",
        "errorCode": "0",
        "data": {"items": list(accounts)}
    }
    return JSONResponse(content=results, status_code=200)


@api_router.post("/pay/{account_id}")
async def pay(account_id: int):
    await Account.filter(id=account_id).delete()
