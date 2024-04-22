import uuid

from pydantic import BaseModel
from faker import Faker
from typing import List
from tortoise import fields
from tortoise.models import Model


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
    uuid = fields.CharField(pk=True,max_length=50)
    username = fields.CharField(max_length=50)
    password = fields.CharField(max_length=50)
    orderStr = fields.TextField()
    details = fields.TextField()
    status = fields.IntField()


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
