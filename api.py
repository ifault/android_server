from fastapi.responses import JSONResponse
from tortoise.expressions import Q
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from models import Account, RequestData, Users
from service import create_access_token, create_refresh_token, is_token_expired

api_router = APIRouter()
security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization credentials")
    access_token = credentials.credentials
    if is_token_expired(access_token):
        # refresh_token = create_refresh_token()
        # new_access_token = create_access_token(refresh_token)
        # if new_access_token is not None:
        #     credentials.credentials = new_access_token
        # else:
        raise HTTPException(status_code=401, detail="Access token expired")


@api_router.get("/accounts")
async def get_accounts(verified_token: HTTPAuthorizationCredentials = Depends(verify_token)):
    accounts = await Account.filter(~Q(status=-1)).values()
    results = {
        "errorMsg": "",
        "errorCode": "0",
        "data": {"items": list(accounts)}
    }
    return JSONResponse(content=results, status_code=200)


@api_router.post("/accounts")
async def add_accounts(data: RequestData, verified_token: HTTPAuthorizationCredentials = Depends(verify_token)):
    username = process_string(data.username)
    password = data.password
    print(username, password)
    return JSONResponse(content={'errorCode': 0}, status_code=200)


@api_router.post("/accounts/del")
async def delete_accounts(verified_token: HTTPAuthorizationCredentials = Depends(verify_token)):
    await Account.delete()
    return JSONResponse(content={'errorCode': 0}, status_code=200)


@api_router.post("/account/del/{uuid}")
async def delete_account(uuid: str, verified_token: HTTPAuthorizationCredentials = Depends(verify_token)):
    print("delete account", uuid)
    await Account.filter(uuid=uuid.strip()).delete()
    return JSONResponse(content={'errorCode': 0}, status_code=200)

@api_router.post("/pay/{uuid}")
async def pay(uuid: str, verified_token: HTTPAuthorizationCredentials = Depends(verify_token)):
    print("pay account", uuid)
    await Account.filter(uuid=uuid.strip()).update(status=-1)
    return JSONResponse(content={'errorCode': 0}, status_code=200)


@api_router.post("/verify/{token}")
async def verify(token: str):
    user = await Users.filter(token=token.strip()).first()
    print(user)
    if user:
        access_token = create_access_token(subject=user.username)
        refersh_token = create_refresh_token(subject=user.username)
        user.access_token = access_token
        await user.save()
        results = {"data": {"accessToken": access_token, "tokenType": "bearer", "refreshToken": refersh_token},
                   'errorCode': 0}
        return JSONResponse(
            content=results,
            status_code=200)
    return JSONResponse(content={'errorCode': 0}, status_code=401)


def process_string(string):
    string = string.replace(" ", "").replace("\n", "").replace("\r", "")
    string = string.replace("，", ",")
    array = string.split(",")
    return array
