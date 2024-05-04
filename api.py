import uuid
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer)
from models import Account, IRequestData, Users, ILogin, IDeleteData, IStatusData, IBindData, Paid
from service import create_access_token, is_token_expired

api_router = APIRouter()
security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization credentials")
    access_token = credentials.credentials
    if is_token_expired(access_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token expired")


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
async def add_account(data: IRequestData,verified_token: HTTPAuthorizationCredentials = Depends(verify_token)):
    username = process_string(data.username)
    password = data.password
    for name in username:
        account = await Account.get_or_none(username=name)
        if account:
            account.password = password
            account.status = "free"
        else:
            account = Account(username=name, password=password, uuid=str(uuid.uuid4()), status=data.status)
        await account.save()

    return JSONResponse(content={"message": f"{data.username} 添加成功", "success": True}, status_code=200)


@api_router.post("/account/delete")
async def remove_account(data: IDeleteData,verified_token: HTTPAuthorizationCredentials = Depends(verify_token)):
    if data.uuid:
        await Account.filter(uuid=data.uuid).delete()
    elif data.status:
        await Account.filter(status__in=data.status.split(",")).delete()

    return JSONResponse(content={"message": "删除成功", "success": True}, status_code=200)


@api_router.post("/account/status")
async def update_account(data: IStatusData,verified_token: HTTPAuthorizationCredentials = Depends(verify_token)):
    await Account.filter(uuid=data.uuid).update(status=data.status)
    return JSONResponse(content={"message": "更改成功", "success": True}, status_code=200)


@api_router.post("/account/pay/{uuid}")
async def pay_account(uuid: str):
    account = await Account.get(uuid=uuid)
    if account:
        account.status = "paid"
        await account.save()
        await Paid(username=account.username, order_str=account.order).save()
    return JSONResponse(content={"message": "删除成功", "success": True}, status_code=200)


@api_router.post("/account/bind")
async def bind_account(data: IBindData,verified_token: HTTPAuthorizationCredentials = Depends(verify_token)):
    account = await Account.get(uuid=data.uuid)
    if account:
        pass
    else:
        return JSONResponse(content={'code': -1, "message": "用户不存在"}, status_code=200)
    return JSONResponse(content={"message": "绑定成功", "success": True}, status_code=200)


@api_router.get("/accounts")
async def get_accounts(verified_token: HTTPAuthorizationCredentials = Depends(verify_token)):
    accounts = await Account.all()
    accounts = [{
        "uuid": account.uuid,
        "username": account.username,
        "password": account.password,
        "details": account.details,
        "status": account.status,
        "order": account.order,
        "order_time": account.order_time.strftime('%Y年%m月%d日 %H时%M分%S秒') if account.order_time else "",
    } for account in accounts]
    result = process_data(accounts)
    # print(result)
    return JSONResponse(content=result, status_code=200)


def process_data(data):
    free = []
    waiting = []
    pending = []
    for item in data:
        if item['status'] == "free":
            free.append(item)
        elif item['status'] == "waiting":
            waiting.append(item)
        elif item['status'] == "pending":
            pending.append(item)
    return {"free": free, "waiting": waiting, "pending": pending}
