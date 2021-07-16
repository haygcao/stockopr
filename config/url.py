
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
https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?num=80&sort=code&asc=1&node=hs_a&symbol=&_s_r_a=page&page=1
[{
  "symbol": "sz000001",
  "code": "000001",
  "name": "\u5e73\u5b89\u94f6\u884c",
  "trade": "21.410",
  "pricechange": -0.21,
  "changepercent": -0.971,
  "buy": "21.400",
  "sell": "21.410",
  "settlement": "21.620",
  "open": "21.410",
  "high": "21.820",
  "low": "21.320",
  "volume": 30535068,
  "amount": 657188702,
  "ticktime": "10:53:51",
  "per": 15.293,
  "pb": 1.372,
  "mktcap": 41548070.861918,
  "nmc": 41547720.330975,
  "turnoverratio": 0.15735
}, ...]
  """
xl_day_price_url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?num=80&sort=code&asc=0&node=%s&symbol=&_s_r_a=page&page=%s'

fh_day_url = 'http://api.finance.ifeng.com/akdaily/?code=sh600000&type=last'
fh_min_url = 'http://api.finance.ifeng.com/akmin?scode=sh000300&type=30'

fh_page_url = 'http://app.finance.ifeng.com/list/stock.php?t=hs&f=chg_pct&o=desc&p=1'

"""
v_sz300502="51~新易盛~300502~33.05~34.34~34.50~92020~43095~48924~33.05~85~33.04~110~33.03~53~33.02~11~33.01~6~33.06~2~33.07~62~33.08~827~33.10~1~33.14~25~~20210608161503~-1.29~-3.76~34.55~32.90~33.05/92020/308176183~92020~30818~2.81~30.59~~34.55~32.90~4.80~108.34~167.59~4.71~41.21~27.47~0.96~-652~33.49~37.27~34.08~~~1.29~30817.6183~0.0000~0~ A~GP-A-CYB~-16.19~-0.51~0.59~15.41~12.83~59.63~24.96~8.01~28.50~14.56~327795898~507086211";
"""
tx_last_url = 'https://qt.gtimg.cn/q=sh688131,sh688319,sz300502&r=449365993'

"""
http://quotes.money.163.com/service/chddata.html?code=1300502&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP   # 下载 csv
http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?num=80&sort=code&asc=0&node=hs_a&symbol=&_s_r_a=page&page=1   # 昨收 settlement - pricechange
http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param=sz300502,day,2021-06-01,2021-06-07,3,qfq   # 没有昨收
http://app.finance.ifeng.com/list/stock.php?t=hs&f=chg_pct&o=desc&p=1   # 昨收盘
http://quotes.money.163.com/hs/service/diyrank.php?host=http%3A%2F%2Fquotes.money.163.com%2Fhs%2Fservice%2Fdiyrank.php&page={0}&query=STYPE%3AEQA&fields=NO%2CSYMBOL%2CNAME%2CPRICE%2CPERCENT%2CUPDOWN%2CFIVE_MINUTE%2COPEN%2CYESTCLOSE%2CHIGH%2CLOW%2CVOLUME%2CTURNOVER%2CHS%2CLB%2CWB%2CZF%2CPE%2CMCAP%2CTCAP%2CMFSUM%2CMFRATIO.MFRATIO2%2CMFRATIO.MFRATIO10%2CSNAME%2CCODE%2CANNOUNMT%2CUVSNEWS&sort=PERCENT&order=desc&count={1}&type=query

https://hq.sinajs.cn/list=s_sh000001,s_sz399001,s_sz399006,s_sh000688
var hq_str_s_sh000001="上证指数,3525.5039,-28.2116,-0.79,3508778,52685867";   3508778手 52，685867万
var hq_str_s_sz399001="深证成指,14882.90,-57.143,-0.38,439891606,67025971";
var hq_str_s_sz399006="创业板指,3432.96,23.368,0.69,22197969,10613087";
var hq_str_s_sh000688="科创50,1610.7749,40.7469,2.60,117347,6614575";

http://api.money.126.net/data/feed/sh000001,money.api

urllib.request.urlopen('http://api.money.126.net/data/feed/{0},money.api'.format('1399300')).read().decode('gbk')
0000001 上证指数
1399001 深证成指
1399006 创业板指
0000688 科创50
'_ntes_quote_callback({"0000001":{"code": "0000001", "percent": -0.006632, "askvol1": 0, "askvol3": 0, "askvol2": 0, "askvol5": 0, "askvol4": 0, "price": 3530.15, "open": 3557.22, "bid5": 0, "bid4": 0, "bid3": 0, "bid2": 0, "bid1": 0, "high": 3558.68, "low": 3528.5, "updown": -23.57, "type": "SH", "bidvol1": 0, "status": 0, "bidvol3": 0, "bidvol2": 0, "symbol": "000001", "update": "2021/07/08 13:16:10", "bidvol5": 0, "bidvol4": 0, "volume": 24468520700, "ask5": 0, "ask4": 0, "ask1": 0, "name": "\\u4e0a\\u8bc1\\u6307\\u6570", "ask3": 0, "ask2": 0, "arrow": "\\u2193", "time": "2021/07/08 13:16:10", "yestclose": 3553.72, "turnover": 364138801453} });'

https://qt.gtimg.cn/q=sh000001,sz399001,sz399006,sh000688
v_sh000001="1~上证指数~000001~3525.50~3553.72~3557.22~350877857~175438929~175438929~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~~20210708153055~-28.22~-0.79~3558.68~3521.06~3525.50/350877857/526858672970~350877857~52685867~0.82~14.22~~3558.68~3521.06~1.06~391991.96~500621.27~0.00~-1~-1~1.17~0~3539.03~~~~~~52685867.2970~0.0000~0~ ~ZS~1.51~-1.76~~~~3731.69~3174.66~-1.15~-1.83~2.17~~~-6.48"; v_sz399001="51~深证成指~399001~14882.90~14940.05~14984.25~439891607~219945803~219945803~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~~20210708153103~-57.15~-0.38~15033.34~14856.93~14882.90/439891607/670259718552~439891607~67025972~2.25~36.20~~15033.34~14856.93~1.18~285513.82~377561.75~0.00~-1~-1~1.16~0~14945.75~~~~~~67025971.8552~0.0000~0~ ~ZS~2.85~-1.04~~~~16293.09~12702.62~0.66~1.12~7.74~~~-8.21"; v_sz399006="51~创业板指~399006~3432.96~3409.59~3435.31~153752824~76876412~76876412~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~~20210708153103~23.37~0.69~3469.60~3418.70~3432.96/153752824/290177193728~153752824~29017719~4.07~82.31~~3469.60~3418.70~1.49~86678.89~129700.54~0.00~-1~-1~1.18~0~3442.51~~~~~~29017719.3728~0.0000~0~ ~ZS~15.73~-0.65~~~~3500.74~2474.70~4.69~7.02~23.34~~~0.82"; v_sh000688="1~科创50~000688~1610.77~1570.03~1577.50~11734788~5867394~5867394~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~0.00~0~~20210708153059~40.74~2.59~1616.70~1577.41~1610.77/11734788/66145754568~11734788~6614575~2.67~105.67~~1616.70~1577.41~2.50~9357.55~28540.42~0.00~-1~-1~1.15~0~1601.61~~~~~~6614575.4568~0.0000~0~ ~ZS~15.63~1.96~~~~1726.19~1212.34~7.04~12.85~26.69~~~-38.25";
"""