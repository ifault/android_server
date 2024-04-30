import uuid

from fastapi.responses import JSONResponse
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from flask import Request

from models import Account, RequestData, Users, ILogin, DeleteData, statusData, Paid, bindData
from service import create_access_token, is_token_expired

api_router = APIRouter()
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization credentials")
    access_token = credentials.credentials
    if is_token_expired(access_token):
        raise HTTPException(status_code=200, detail="Access token expired")


def process_string(string):
    string = string.replace(" ", "").replace("\n", "").replace("\r", "")
    string = string.replace("，", ",")
    array = string.split(",")
    return array


@api_router.post("/login")
async def login(form: ILogin):
    user = await Users.filter(username=form.username, password=form.password).first()
    if user:
        access_token = create_access_token(subject=user.username)
        user.access_token = access_token
        await user.save()
        return JSONResponse(content={"token": access_token, "success": True, "message": ""}, status_code=200)
    return JSONResponse(content={"token": "", "success": False, "message": "用户不存在"}, status_code=200)


@api_router.post("/account")
async def add_account(data: RequestData,verified_token: HTTPAuthorizationCredentials = Depends(verify_token)):
    username = process_string(data.username)
    password = data.password
    for name in username:
        account = await Account.get_or_none(username=name)
        if account:
            account.password = password
            account.status = 0
        else:
            account = Account(username=name, password=password, uuid=str(uuid.uuid4()), status=data.status)
        await account.save()

    return JSONResponse(content={'code': 0, "message": "保存成功"}, status_code=200)


@api_router.post("/account/delete")
async def remove_account(data: DeleteData,verified_token: HTTPAuthorizationCredentials = Depends(verify_token)):
    if data.uuid:
        await Account.filter(uuid=data.uuid).delete()
    elif data.status:
        await Account.filter(status=data.status).delete()

    return JSONResponse(content={'code': 0, "message": "删除成功"}, status_code=200)


@api_router.post("/account/status")
async def update_account(data: statusData,verified_token: HTTPAuthorizationCredentials = Depends(verify_token)):
    await Account.filter(uuid=data.uuid).update(status=data.status)
    return JSONResponse(content={'code': 0, "message": "删除成功"}, status_code=200)


@api_router.post("/account/pay/{uuid}")
async def pay_account(uuid: str,verified_token: HTTPAuthorizationCredentials = Depends(verify_token)):
    account = await Account.get(uuid=uuid)
    if account:
        account.status = 2
        await account.save()
        await Paid(username=account.username, order_str=account.order_str).save()
    return JSONResponse(content={'code': 0, "message": "删除成功"}, status_code=200)


@api_router.post("/account/bind")
async def pay_account(data: bindData):
    account = await Account.get(uuid=data.uuid)
    if account:
        pass
    else:
        return JSONResponse(content={'code': -1, "message": "用户不存在"}, status_code=200)
    return JSONResponse(content={'code': 0, "message": "绑定成功"}, status_code=200)

