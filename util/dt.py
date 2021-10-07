# -*- encoding: utf-8 -*-
import re
import time
import datetime
from datetime import datetime as date

holiday_str = '''
2021
一、元旦：2021年1月1日至3日放假，共3天。
二、春节：2月11日至17日放假调休，共7天。2月7日（星期日）、2月20日（星期六）上班。
三、清明节：4月3日至5日放假调休，共3天。
四、劳动节：5月1日至5日放假调休，共5天。4月25日（星期日）、5月8日（星期六）上班。
五、端午节：6月12日至14日放假，共3天。
六、中秋节：9月19日至21日放假调休，共3天。9月18日（星期六）上班。
七、国庆节：10月1日至7日放假调休，共7天。9月26日（星期日）、10月9日（星期六）上班。
'''
lastday = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def mktime(_datetime):
    # time.mktime((tm_today.tm_year, tm_today.tm_mon, tm_today.tm_mday, 9, 30, 0, 0, 0, 0))
    return int(time.mktime(_datetime.timetuple()))

today = datetime.date.today()
start_time_am = mktime(datetime.datetime(today.year, today.month, today.day, 9, 30))
end_time_pm = mktime(datetime.datetime(today.year, today.month, today.day, 15))
end_time_day = mktime(datetime.datetime(today.year, today.month, today.day, 23, 59, 59))

def set_today():
    global today
    today = datetime.date.today()

def set_trade_time():
    global start_time_am
    global end_time_pm
    global end_time_day
    start_time_am = mktime(datetime.datetime(today.year, today.month, today.day, 9, 30))
    end_time_pm = mktime(datetime.datetime(today.year, today.month, today.day, 15))
    end_time_day = mktime(datetime.datetime(today.year, today.month, today.day, 23, 59, 59))


#day_str: 2016-1-17
def isholiday(day=None):
    if not day:
        day = today

    '''
    [('1', '1', '3'),
     ('2', '11', '17'),
     ('4', '3', '5'),
     ('5', '1', '5'),
     ('6', '12', '14'),
     ('9', '19', '21'),
     ('0', '1', '7')]
     '''
    p = '.*([0-9]+)月([0-9]+)日至([0-9]+)日.*'   # ('0', '1', '7')
    p = '.*?([0-9]+)月([0-9]+)日至([0-9]+)日.*'   # ('10', '1', '7')
    prog = re.compile(p)
    r = prog.findall(holiday_str)
    for month, day_start, day_end in r:
        month = int(month)
        day_start = int(day_start)
        day_end = int(day_end)

        if month == day.month:
            if day_start <= day.day <= day_end:
                return True

    return False


def isweedend(day=None):
    if not day:
        day = today

    # date.weekday(), Return the day of the week as an integer, where Monday is 0 and Sunday is 6
    # date.isoweekday(), Return the day of the week as an integer, where Monday is 1 and Sunday is 7
    weekday = date.isoweekday(day)
    if weekday > 5:
        return True
    return False


def istradeday(day=None):
    if not day:
        day = today

    if isweedend(day) or isholiday(day):
        return False

    return True


def get_trade_date():
    if not istradeday():
        return get_pre_trade_date(prev=1)

    now = datetime.datetime.now()
    if now >= datetime.datetime(year=now.year, month=now.month, day=now.day, hour=9, minute=15):
        return now.date()

    return get_pre_trade_date(prev=2)


def get_pre_trade_date(date=None, prev=2):
    date = date if date else datetime.date.today()
    d = 0
    while True:
        if istradeday(date):
            d += 1
        if d == prev:
            break
        date = date - datetime.timedelta(days=1)

    return date


def istradetime():
    if not istradeday(today):
        return False

    now = time.time()
    if now < start_time_am or now > end_time_pm:
        return False

    # if start_time_am + 2 * 3600 < now < end_time_pm - 2 * 3600:
    #     return False

    return True


def sumofweektradeday(day):
    sum = 0
    year = day.year
    mon = day.month
    day = day.day
    if mon == 2 and year % 4 == 0: #
        lastday[1] = 29
    for d in range(day, lastday[mon - 1] + 1):
        day_str = [0, 0, 0]
        day_str[0] = year
        day_str[1] = mon
        day_str[2] = d
        #mktime(tm_day)
        if isweedend(day_str):
            break
        if isholiday(day_str):
            continue
        sum += 1
    #tm_day.tm_mday = day #
    return sum


def sumofmonthtradeday(day): #tm_day, is str
    sum = 0
    year = day.year
    mon = day.month
    day = day.day
    lastday_tmp = lastday[mon - 1] + 1
    if mon == 2 and year % 4 == 0: #ÔÂ·ÝŽÓ1ÔÂ¿ªÊŒ, Äê·ÝÎªÊµŒÊÄê·Ý, ²»ÓÃŒÓ1900
        lastday_tmp = 29 #È«ŸÖ±äÁ¿!!!
    for d in range(day, lastday_tmp):
        day_str = [0, 0, 0]
        day_str[0] = year
        day_str[1] = mon
        day_str[2] = d
        #mktime(tm_day)
        if istradeday(day_str):
            sum += 1
    #tm_day.tm_mday = day #
    return sum
tm_day = time.localtime()


def sumofyeartradeday(y):
    days = 0
    for m in range(1, 13):
        day = date(y, m, 1)
        days += sumofmonthtradeday(day)
    return days


def dt64_to_dt(dt64):
    return dt64.astype('M8[D]').astype('O')  #'M8[ms]'
