
tx_latest_day_quote_url = 'http://stock.gtimg.cn/data/get_hs_xls.php?id=ranka&type=1&metric=chr'
tx_min_url = 'https://web.ifzq.gtimg.cn/appstock/app/kline/mkline?param={code},{period},,{count}'
# tx_day_url = 'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param={code},{period},{start_date},,{count},qfq'  # 2020-7-16,2021-5-7,
tx_day_url = 'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param={code},{period},{start_date},{end_date},{count},qfq'
xl_min_quote_url = 'https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData?symbol={code}&scale={period}&ma=no&datalen={count}'

"""
股票名称、今日开盘价、昨日收盘价、当前价格、今日最高价、今日最低价、竞买价、竞卖价、成交股数、成交金额、买1手、买1报价、买2手、买2报价、…、买5报价、…、卖5报价、日期、时间
var hq_str_sz300502="新易盛,48.000,47.500,48.210,48.400,47.530,48.210,48.220,4009118,192785421.290,3312,48.210,500,48.140,7500,48.130,2000,48.100,400,48.090,23800,48.220,40900,48.250,200,48.260,3900,48.280,400,48.290,2021-05-31,11:30:03,00";
"""
xl_realtime_quote_url = 'http://hq.sinajs.cn/list={code}'

"""
[{"symbol":"sh688981","code":"688981","name":"\u4e2d\u82af\u56fd\u9645","trade":"55.730","pricechange":0,"changepercent":0,"buy":"0.000","sell":"0.000","settlement":"55.730","open":"0.000","high":"0.000","low":"0.000","volume":0,"amount":0,"ticktime":"09:01:15","per":83.179,"pb":4.368,"mktcap":44029922.58725,"nmc":6106074.169,"turnoverratio":0}]
[{'symbol': 'sh688981',
  'code': '688981',
  'name': '中芯国际',
  'trade': '55.730',
  'pricechange': 0,
  'changepercent': 0,
  'buy': '0.000',
  'sell': '0.000',
  'settlement': '55.730',
  'open': '0.000',
  'high': '0.000',
  'low': '0.000',
  'volume': 0,
  'amount': 0,
  'ticktime': '09:01:15',
  'per': 83.179,
  'pb': 4.368,
  'mktcap': 44029922.58725,
  'nmc': 6106074.169,
  'turnoverratio': 0}]
  """
xl_day_price_url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?num=80&sort=code&asc=0&node=%s&symbol=&_s_r_a=page&page=%s'

fh_day_url = 'http://api.finance.ifeng.com/akdaily/?code=sh600000&type=last'
fh_min_url = 'http://api.finance.ifeng.com/akmin?scode=sh000300&type=30'

fh_page_url = 'http://app.finance.ifeng.com/list/stock.php?t=hs&f=chg_pct&o=desc&p=1'

"""
v_sz300502="51~新易盛~300502~33.05~34.34~34.50~92020~43095~48924~33.05~85~33.04~110~33.03~53~33.02~11~33.01~6~33.06~2~33.07~62~33.08~827~33.10~1~33.14~25~~20210608161503~-1.29~-3.76~34.55~32.90~33.05/92020/308176183~92020~30818~2.81~30.59~~34.55~32.90~4.80~108.34~167.59~4.71~41.21~27.47~0.96~-652~33.49~37.27~34.08~~~1.29~30817.6183~0.0000~0~ A~GP-A-CYB~-16.19~-0.51~0.59~15.41~12.83~59.63~24.96~8.01~28.50~14.56~327795898~507086211";
"""
tx_last_url = 'https://qt.gtimg.cn/q=sh688131,sh688319,sz300502&r=449365993'