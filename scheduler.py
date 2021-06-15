import schedule
import time

from acquisition import acquire
from trade_manager import trade_manager
from util.log import logger


def job():
    print("I'm working...")


def sync():
    trade_manager.sync()


def save_quote():
    acquire.save_quote()


def schedule_task():
    # schedule.every(10).seconds.do(job)
    # schedule.every(10).minutes.do(job)
    # schedule.every().hour.do(job)
    schedule.every().day.at("09:10").do(sync)
    schedule.every().day.at("21:00").do(save_quote)
    # schedule.every(5).to(10).minutes.do(job)
    # schedule.every().monday.do(job)
    # schedule.every().wednesday.at("13:15").do(job)
    # schedule.every().minute.at(":17").do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    logger.info('scheduler is running')
    schedule_task()
    logger.info('scheduler is stopped')
