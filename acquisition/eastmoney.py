from typing import List, Dict, Union

import multitasking as multitasking
import pandas
from jsonpath import jsonpath
from retry.api import retry
from tqdm import tqdm

from acquisition.em_util import to_numeric, get_quote_id, session

# 请求头
EASTMONEY_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Referer': 'http://quote.eastmoney.com/center/gridlist.html',
}

# 股票、ETF、债券 K 线表头
# EASTMONEY_KLINE_FIELDS = {
#     'f51': '日期',
#     'f52': '开盘',
#     'f53': '收盘',
#     'f54': '最高',
#     'f55': '最低',
#     'f56': '成交量',
#     'f57': '成交额',
#     'f58': '振幅',
#     'f59': '涨跌幅',
#     'f60': '涨跌额',
#     'f61': '换手率'
# }
EASTMONEY_KLINE_FIELDS = {
    'f51': 'trade_date',
    'f52': 'open',
    'f53': 'close',
    'f54': 'high',
    'f55': 'low',
    'f56': 'volume',
    'f57': 'amount',
    'f58': 'amplitude',
    'f59': 'percent',
    'f60': 'price_change',
    'f61': 'turnover_ratio'
}


@to_numeric
def get_quote_history_single(code: str,
                             beg: str = '19000101',
                             end: str = '20500101',
                             klt: int = 101,
                             fqt: int = 1,
                             **kwargs) -> pandas.DataFrame:
    fields = list(EASTMONEY_KLINE_FIELDS.keys())
    columns = list(EASTMONEY_KLINE_FIELDS.values())
    fields2 = ",".join(fields)
    if kwargs.get('quote_id_mode'):
        quote_id = code
    else:
        quote_id = get_quote_id(code)
    params = (
        ('fields1', 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13'),
        ('fields2', fields2),
        ('beg', beg),
        ('end', end),
        ('rtntype', '6'),
        ('secid', quote_id),
        ('klt', f'{klt}'),
        ('fqt', f'{fqt}'),
    )

    url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get'

    json_response = session.get(
        url, headers=EASTMONEY_REQUEST_HEADERS, params=params).json()
    klines: List[str] = jsonpath(json_response, '$..klines[:]')
    if not klines:
        columns.insert(0, '代码')
        columns.insert(0, '名称')
        return pandas.DataFrame(columns=columns)

    rows = [kline.split(',') for kline in klines]
    # name = json_response['data']['name']
    code = quote_id.split('.')[-1]
    df = pandas.DataFrame(rows, columns=columns)
    df.insert(0, 'code', code.zfill(6))
    # df.insert(0, 'name', name)
    df = df.set_index('trade_date')
    df = df.sort_index()

    return df


def get_quote_history_multi(codes: List[str],
                            beg: str = '19000101',
                            end: str = '20500101',
                            klt: int = 101,
                            fqt: int = 1,
                            tries: int = 3,
                            **kwargs
                            ) -> Dict[str, pandas.DataFrame]:
    """
    获取多只股票、债券历史行情信息

    """

    dfs: Dict[str, pandas.DataFrame] = {}
    total = len(codes)

    @multitasking.task
    @retry(tries=tries, delay=1)
    def start(code: str):
        _df = get_quote_history_single(
            code,
            beg=beg,
            end=end,
            klt=klt,
            fqt=fqt,
            **kwargs)
        dfs[code] = _df
        pbar.update(1)
        pbar.set_description_str(f'Processing => {code}')

    pbar = tqdm(total=total)
    for code in codes:
        start(code)
    multitasking.wait_for_tasks()
    pbar.close()
    return dfs


def get_quote_history(codes: Union[str, List[str]],
                      beg: str = '19000101',
                      end: str = '20500101',
                      klt: int = 101,
                      fqt: int = 1,
                      **kwargs) -> Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]:
    """
    获取股票、ETF、债券的 K 线数据

    Parameters
    ----------
    codes : Union[str,List[str]]
        股票、债券代码 或者 代码构成的列表
    beg : str, optional
        开始日期，默认为 ``'19000101'`` ，表示 1900年1月1日
    end : str, optional
        结束日期，默认为 ``'20500101'`` ，表示 2050年1月1日
    klt : int, optional
        行情之间的时间间隔，默认为 ``101`` ，可选示例如下

        - ``1`` : 分钟
        - ``5`` : 5 分钟
        - ``15`` : 15 分钟
        - ``30`` : 30 分钟
        - ``60`` : 60 分钟
        - ``101`` : 日
        - ``102`` : 周
        - ``103`` : 月

    fqt : int, optional
        复权方式，默认为 ``1`` ，可选示例如下

        - ``0`` : 不复权
        - ``1`` : 前复权
        - ``2`` : 后复权

    Returns
    -------
    Union[DataFrame, Dict[str, DataFrame]]
        股票、债券的 K 线数据

        - ``DataFrame`` : 当 ``codes`` 是 ``str`` 时
        - ``Dict[str, DataFrame]`` : 当 ``codes`` 是 ``List[str]`` 时

    """

    if isinstance(codes, str):
        return get_quote_history_single(codes,
                                        beg=beg,
                                        end=end,
                                        klt=klt,
                                        fqt=fqt,
                                        **kwargs)

    elif hasattr(codes, '__iter__'):
        codes = list(codes)
        return get_quote_history_multi(codes,
                                       beg=beg,
                                       end=end,
                                       klt=klt,
                                       fqt=fqt,
                                       **kwargs)
    else:
        raise TypeError(
            '代码数据类型输入不正确！'
        )
