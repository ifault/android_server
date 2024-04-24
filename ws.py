import logging
import uuid

import asyncio
from fastapi import APIRouter, WebSocket, HTTPException
from starlette.websockets import WebSocketDisconnect

from models import Account
from service import is_token_expired

ws_router = APIRouter()
ws = {}


async def verify_token(token: str):
    if token is None or token == "":
        raise HTTPException(status_code=401, detail="token不存在")
    if is_token_expired(token):
        raise HTTPException(status_code=401, detail="token过期,请重新验证")


@ws_router.websocket("/")
async def websocket_endpoint(websocket: WebSocket, token: str):
    await verify_token(token)
    await websocket.accept()
    await process_websocket(websocket)


async def process_websocket(websocket: WebSocket):
    socket_id = str(uuid.uuid4())
    ws[socket_id] = websocket
    periodically = None
    task = None
    try:
        periodically = asyncio.create_task(send_message_periodically(socket_id))
        task = asyncio.create_task(handle_task(socket_id))
        while True:
            data = await websocket.receive_text()
            logging.info(f"Receive: {data}")
    except WebSocketDisconnect:
        del ws[socket_id]
    except Exception as e:
        logging.error(e)
        del ws[socket_id]
    finally:
        if periodically:
            periodically.cancel()
        if task:
            task.cancel()


async def send_message_periodically(socket_id: str):
    try:
        while True:
            await notify(socket_id, 0, "服务器运行正常")
            await asyncio.sleep(10)
    except asyncio.CancelledError:
        await notify(socket_id, 0, "服务器发生异常，任务结束")


async def handle_task(socket_id: str):
    tasks = []

    accounts = await Account.filter(status=0).all()
    for account in accounts:
        task = asyncio.create_task(handle_order(socket_id, account))
        tasks.append(task)

    await asyncio.gather(*tasks)
    await notify(socket_id, -1, "所有订单处理完成")


async def handle_order(socket_id: str, account: Account):
    try:
        while True:
            logging.info(f"处理订单: {account.uuid}")
            status = await handle_status()
            if status:
                account.status = 1
                account.orderStr = "订单详情"
                account.details = "等待支付"
                await account.save()
                await notify(socket_id, 1, "订单等待支付")
                break
            else:
                await asyncio.sleep(10)
    except Exception as e:
        account.details = "订单发生异常"
        await account.save()
        await notify(socket_id, 1, "订单发生异常")


async def handle_status():
    await asyncio.sleep(10)
    return True


async def notify(socket_id, code=0, message=""):
    message = {
        "code": code,
        "message": message
    }
    await ws[socket_id].send_json(message)
