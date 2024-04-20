import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models import fake_accounts

api_router = APIRouter()


@api_router.get("/accounts")
async def get_accounts():
    accouts = fake_accounts(10)
    return JSONResponse(content={"accounts": json.dumps(accouts)}, status_code=200)
