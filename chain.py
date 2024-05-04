import asyncio
from desney.tools import *
from models import Account
from status import Status


class SequentialExecution:
    def __init__(self, debug=True):
        self.debug = debug
        self.price = None
        self.total_price = None
        self.quantity = None
        self.start_time = None
        self.target_date_cn = None
        self.target_date_en = None
        self.username = None
        self.password = None
        self.account = None
        self.card = "222424198302052810"
        self.desiney = Desney(str(uuid.uuid4()))

    async def update_details(self, details):
        self.account.details = details
        await self.account.save()

    async def execute(self, account):
        self.account = account
        if not self.account:
            print("账号不存在")
            return
        valid, message = self.desiney.login(account.username, account.password)
        if not valid:
            await self.update_details(message)
            return
        self.desiney.php_sync()
        self.desiney.get_token()
        valid, message, eligibe_res = self.desiney.get_current_eligible()
        if not valid:
            await self.update_details(message)
            return
        vids = eligibe_res['vids']
        self.target_date_en = eligibe_res['target_date_en']
        self.target_date_cn = eligibe_res['target_date_cn']
        self.quantity = len(vids)
        self.start_time = eligibe_res['start_time']
        price_res = self.desiney.get_morning_target_day_price(eligibe_res['target_date_en'])
        self.total_price = str(int(price_res['totalPrice']) * self.quantity)
        self.price = price_res['price']
        details = f"""
{message}
预定日期:{self.target_date_cn}
总价:{self.total_price}
        """
        await self.update_details(details)
        while True:
            valid, valid_days = self.desiney.check_monirng_calander()
            if not valid:
                await self.update_details(f"{details}\n 检查日期时出错")
                return
            if self.target_date_en in valid_days:
                break
            await asyncio.sleep(1)
        print("start to ordedr")
        if self.debug:
            return
        self.desiney.get_commerce_token()
        valid, session_id, message = self.desiney.confirm_morning_order(vids, self.card,
                                                                        self.start_time,
                                                                        self.target_date_en,
                                                                        self.target_date_cn,
                                                                        self.price,
                                                                        self.total_price)
        if not valid:
            await self.update_details(message)
            return
        valid, order_str, message = self.desiney.get_alipay_order_str(session_id)
        if not valid or not order_str:
            self.account.orderStr = order_str
            self.account.status = Status.SUCCESS.value
            await self.account.save()


async def main():
    tasks = []
    account = await Account.filter(uuid='fdada1c9-fc01-4ceb-aaaf-7b4221a8a339').first()
    task = asyncio.create_task(SequentialExecution().execute(account))
    tasks.append(task)
    await asyncio.gather(*tasks)

#
# loop = asyncio.get_event_loop()
# try:
#     loop.run_until_complete(main())
# finally:
#     loop.close()
