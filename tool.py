import datetime

from acquisition import acquire
from util import dt
from util.log import logger


def save_quote():
    acquire.save_quote()


if __name__ == '__main__':
    save_quote()
