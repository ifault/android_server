from pydantic import BaseModel
from faker import Faker
from typing import List


class IAccount(BaseModel):
    username: str
    password: str
    status: str
    orderStr: str


def fake_accounts(quantity: int) -> List[IAccount]:
    fake = Faker()
    accounts = []

    for _ in range(quantity):
        account = IAccount(
            username=fake.user_name(),
            password=fake.password(),
            status=fake.random_element(["有效", "无效", "完成"]),
            orderStr=fake.pystr(min_chars=5, max_chars=10)
        )
        accounts.append(account.dict())

    return accounts
