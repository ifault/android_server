import datetime
import uuid

from pydantic import BaseModel
from faker import Faker
from typing import List, Optional
from tortoise import fields
from tortoise.models import Model


class ILogin(BaseModel):
    username: str
    password: str


class IAccount(BaseModel):
    uuid: str
    username: str
    password: str
    orderStr: str
    details: str
    create_time: str
    pay_time: str
    status: int


class Account(Model):
    uuid = fields.CharField(pk=True, max_length=50)
    username = fields.CharField(max_length=50)
    password = fields.CharField(max_length=50)
    order_str = fields.TextField(null=True, default="")
    details = fields.TextField(null=True)
    status = fields.IntField(default=0)


class Users(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True, index=True)
    password = fields.CharField(max_length=255, unique=True, index=True, default=str(uuid.uuid4().hex))
    expired = fields.DatetimeField(default=datetime.datetime.now() + datetime.timedelta(days=30))
    created_at = fields.DatetimeField(auto_now_add=True)
    access_token = fields.CharField(max_length=255, null=True)


class Paid(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255)
    order_str = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)


def fake_accounts(quantity: int) -> List[IAccount]:
    fake = Faker()
    accounts = []

    for i in range(quantity):
        account = IAccount(
            uuid=str(uuid.uuid4()),
            username=f"test{i}",
            password=f"test{i}",
            status=fake.random_element([0, 1, 2]),
            orderStr=f"test{i}",
            create_time="2024-04-06",
            pay_time="2024-04-06",
            details="很多个"
        )
        accounts.append(account.dict())

    return accounts


class RequestData(BaseModel):
    password: str
    username: str
    status: Optional[int] = 0


class DeleteData(BaseModel):
    uuid: Optional[str] = None
    status: Optional[str] = None


class statusData(BaseModel):
    uuid: str
    status: int


class bindData(BaseModel):
    uuid: str
    card: str