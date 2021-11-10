import redis
from config import dbip, dbport
import time

# conn = redis.StrictRedis(host='192.168.1.227', port=6379, db=0, password='server')
conn = redis.StrictRedis(host=dbip, port=dbport, db=0)


def exec_cmd(*args, **options):
    r = conn.execute_command(*args, **options)
    return r


def set_day(day):
    exec_cmd('set', 'today', day)


def same_day():
    r = exec_cmd('get', 'today')
    _tm = time.localtime()
    if r and int(r) == _tm.tm_yday:
        return True
    set_day(_tm.tm_yday)

    return False


def save_cur_stage(stock_info):
    # same day
    if not same_day():
        del_stage(stock_info)

    # exec_cmd('hset', stock_info['stock_info'], 'cur_stage', stock_info['cur_stage'])
    exec_cmd('rpush', 'cur_stage_%s' % stock_info['name'], stock_info['cur_stage'])


def load_cur_stage(stock_info):
    # r = exec_cmd('hget', stock_info['stock_info'], 'cur_stage')
    r = exec_cmd('lrange', 'cur_stage_%s' % stock_info['name'], -1, -1)[0] #not pop
    return r.decode()


def load_all_stage(stock_info):

    r = exec_cmd('lrange', 'cur_stage_%s' % stock_info['name'], 0, -1)
    return r


def del_stage(stock_info):

    exec_cmd('del', 'cur_stage_%s' % stock_info['name'])


def del_all_stages():
    _stages = exec_cmd('keys', 'cur_stage_*')
    for key in _stages:
        exec_cmd('del', key)


def save_stage_info(stock_info, stage, max_min):

    # cnt = "%d-%d" % (max_min.get('max'), max_min.get('min'))
    cnt = "%.2f:%.2f:%d" % (max_min[0], max_min[1], int(time.time()))
    exec_cmd('hset', 'stage_info_%s' % stock_info['name'], stage, cnt)


def load_stage_info(stock_info, stage, ret_t = False):
    r = exec_cmd('hget', 'stage_info_%s' % stock_info['name'], stage).decode()
    _max, _min, t = r.split(':')
    if ret_t:
        return float(_max), float(_min), int(t)
    else:
        return float(_max), float(_min)


def save_to_db(stock_info):

    for key in stock_info:
        exec_cmd('hset', stock_info['name'], key, stock_info[key])
    # exec_cmd('save')


def load_data_from_db(stock_info):

    r = exec_cmd('hgetall', stock_info['name'])
    _stock_info = {}
    for i in range(0, len(r) - 1, 2):
        key = r[i].decode()
        val = r[i + 1].decode()
        if key == 'last_min':
            val = float(val)
        _stock_info.setdefault(key, val)
    return _stock_info


if __name__ == '__main__':
    pass
