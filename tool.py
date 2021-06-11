import datetime

from acquisition import acquire
from util import dt
from util.log import logger


def save_quote():
    if not dt.istradeday():
        pass
        # exit(0)
    xls = None
    # xls = 'data/xls/2021-05-24.xls'
    t1 = datetime.datetime.now()
    acquire.save_quote(xls)
    now = datetime.datetime.now()
    logger.info('save quote cost [{}]'.format((now - t1).seconds, 2))


if __name__ == '__main__':
    save_quote()
