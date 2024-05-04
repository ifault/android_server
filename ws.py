import logging
import uuid

import asyncio
from fastapi import APIRouter, WebSocket, HTTPException
from starlette.websockets import WebSocketDisconnect
from chain import SequentialExecution
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
    # await verify_token(token)
    await websocket.accept()
    await process_websocket(websocket)


async def process_websocket(websocket: WebSocket):
    socket_id = str(uuid.uuid4())
    ws[socket_id] = websocket
    task = None
    try:
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
        if task:
            task.cancel()


async def handle_task(socket_id: str):
    tasks = []
    accounts = await Account.filter(status=0).all()
    for account in accounts:
        # task = asyncio.create_task(SequentialExecution().execute(account))
        # tasks.append(task)
        pass
    if len(tasks) > 0:
        await asyncio.gather(*tasks)
    await notify(socket_id, -1, "无待抢票")


async def handle_status():
    await asyncio.sleep(10)
    return True


async def notify(socket_id, code=0, message=""):
    message = {
        "code": code,
        "message": message
    }
    await ws[socket_id].send_json(message)
