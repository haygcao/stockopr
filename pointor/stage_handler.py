# import redis
from config.config import dbip, dbport
import time

# conn = redis.StrictRedis(tr='192.168.1.227', port=6379, db=0, password='server')
# conn = redis.StrictRedis(tr=dbip, port=dbport, db=0)

today = None


def set_day(day):
    global today
    today = day


def same_day():
    global today
    _tm = time.localtime()
    if today and today == _tm.tm_yday:
        return True
    set_day(_tm.tm_yday)

    return False


def save_to_db(stock_info):
    with open(stock_info['name'], 'wb') as f:
        import pickle
        pickle.dump(stock_info, f)


def load_data_from_db(stock_info):
    with open(stock_info['name'], 'rb') as f:
        import pickle
        _stock_info = pickle.load(f)
    return _stock_info


class Stage:
    def __init__(self):
        self.tr = None
        self.cur_stage = None
        self.pre_stage = None
        self.stages = []
        # start, 记录状态改变的日期
        self.stage_info = {}  # {stage:{'start':'', 'end':'', 'min':'', 'max':'', 'min_tmp':'', 'max_tmp':''}, }
        self.stage_info_history = []

    def get_cur_stage(self):
        return self.cur_stage

    def set_cur_stage(self, stage):
        self.cur_stage = stage
        self.stages.append(stage)

    def get_pre_stage(self):
        return self.pre_stage

    def set_pre_stage(self, stage):
        self.pre_stage = stage

    def get_stage_info(self, stage):
        return self.stage_info[stage]

    # def set_stage_info(self, stage, start, end, min, max):
    def set_stage_info(self, stage, min, max):
        # print(stage, 'set_stage_info...')
        # print(self.tr.quote.index[self.tr.ind], min, max)
        # print("*"*50)
        # self.stage_info[stage] = {'start':start, 'end':end, 'min':min, 'max':max}
        # _dt = self.tr.quote.index[self.tr.ind]
        _dt = self.tr.dt
        if stage in self.stage_info:
            self.stage_info[stage].update({'min':min, 'max':max, 'end':_dt})
        else:
            self.stage_info.update({stage:{'min':min, 'max':max, 'end':_dt}})

    def update_stage_info(self, stage, **info):
        self.stage_info[stage].update(info)

    def chg_stage(self, cur_stage, _min, _max):
        # print('%s %5s %f %f' % (self.tr.quote.index[self.tr.ind], cur_stage, _min, _max))
        # print(self.stage_info)

        if self.stage_info is None and (cur_stage == '3' or cur_stage == '4'):
            self.stage_info_history.append(self.stage_info)
            self.stage_info = {}

        # 设置
        self.set_cur_stage(cur_stage)
        self.set_stage_info(cur_stage, _min, _max)
        # dt = self.tr.quote.index[self.tr.ind]
        _dt = self.tr.dt
        self.update_stage_info(cur_stage, start=_dt)

        # cur_stage_idx = cur_stage[len(cur_stage) - 1]
        # if cur_stage_idx == '3' or cur_stage_idx == '4':
        # open_stock_realtime_graph(stock_info, cur_stage_idx)

        # threading.Thread(target=draw_simplified_realtime_graph, kwargs=stock_info).start() #各种错误, TypeError: draw_simplified_realtime_graph() got an unexpected keyword argument 'lowest'
        # draw_simplified_realtime_graph(stock_info)

    def print_stage_info(self):
        _cnt = ''

        def _gen_stage_info(_stage_info):
            cnt = '%5s %s %s %5.2f %5.2f' % (stage, _stage_info['start'], _stage_info['end'], _stage_info['min'], _stage_info['max'])
            return cnt

        key_list = ['start', 'end', 'min', 'max']
        _2d = len(self.stage_info_history)
        _1d = len(self.stages)
        i = 0
        for stage_info in self.stage_info_history:
            while 1:
                stage = self.stages[i]
                if stage not in stage_info:
                    break
                _cnt += _gen_stage_info(stage_info[stage]) + '\n'
                i += 1
            _cnt += '-'*50 + '\n'
        while i < len(self.stages):
            stage = self.stages[i]

            _cnt += _gen_stage_info(self.stage_info[stage]) + '\n'
            i += 1

        print(_cnt)

    def save_cur_stage(self, stock_info):
        # same day
        if not same_day():
            self.del_stage(stock_info)

        # 历史数据
        # 3 -> 3 or 3 -> 4 or 4 -> 3 or 4 -> 4 过程中发生过的状态, 持续时间, 价格变化幅度...
        # 以分析哪个阶段持续时间最长, 价格变化幅度最大
        # 哪些状态出现最频繁

        # 是否需要分库 stockminer
        # create table stage (code varchar(8), start date, end date, substart date, subend date, stage varchar(8), min float, max float);
        # exec_cmd('hset', stock_info['stock_info'], 'cur_stage', stock_info['cur_stage'])
        # exec_cmd('rpush', 'cur_stage_%s' % stock_info['name'], stock_info['cur_stage'])

    def del_stage(self, stock_info):
        pass

    def get_all_stage(self):
        return self.stages

    def del_all_stages(self):
        pass


if __name__ == '__main__':
    pass
