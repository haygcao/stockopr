import datetime
from functools import wraps

import schedule
import time

from acquisition import acquire
from trade_manager import trade_manager
from util import singleten, dt
from util.log import logger


def handle_exception(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error('in func[{0}], error message: {1} '.format(func.__name__, e))
    return inner


@handle_exception
def job():
    print("I'm working...")
    raise Exception('xxx')


@handle_exception
def sync():
    trade_manager.sync()


@handle_exception
def save_quote():
    acquire.save_quote()


@handle_exception
def patrol():
    trade_manager.patrol()


@handle_exception
def create_position_price_limited():
    trade_manager.create_position_price_limited()


def schedule_task():
    now = datetime.datetime.now()
    if not dt.istradeday() or now.hour >= 18:
        return

    me = singleten.SingleInstance()

    # schedule.every(10).seconds.do(job)
    # schedule.every(10).minutes.do(job)
    # schedule.every().hour.do(job)
    schedule.every().day.at("15:05").do(sync)
    # 通达信盘后数据在 15:45 后才能下载
    schedule.every().day.at("15:50").do(save_quote)
    # schedule.every(5).to(10).minutes.do(job)
    # schedule.every().monday.do(job)
    # schedule.every().wednesday.at("13:15").do(job)
    # schedule.every().minute.at(":00").do(patrol)
    # schedule.every().minute.at(":00").do(create_position_price_limited)
    schedule.every().hour.at("00:00").do(patrol)
    schedule.every().hour.at("00:00").do(create_position_price_limited)

    while now.hour < 18:
        schedule.run_pending()
        now = datetime.datetime.now()
        time.sleep(1)


if __name__ == '__main__':
    logger.info('scheduler is running')
    schedule_task()
    logger.info('scheduler is stopped')
