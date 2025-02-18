
"""
JSON数据；当天分时数据
小时分钟时间、价格、均价、成交量
http://img1.money.126.net/data/hs/time/today/1300598.json
JSON数据；前4天分时数据
http://img1.money.126.net/data/hs/time/4days/[股票代码].json

其中，是否复权，不复权为kline，复权为klinederc
http://img1.money.126.net/data/hs/kline/day/history/2021/1300598.json

返回结果：获取日线所有时间节点, 和收盘价。
其中，[是否复权]，不复权为kline，复权为klinederc。
其中，[周期]，day为日数据，week周数据，month月数据。
http://img1.money.126.net/data/hs/kline/day/times/1300598.json

"""
# https://ifzq.gtimg.cn/appstock/app/minute/query?code=sz002739   # 当天的m1数据
# https://web.ifzq.gtimg.cn/appstock/app/minute/query?code=sz002739c  # 当天的m1数据

# https://data.gtimg.cn/flashdata/hushen/minute/sz002739.js  # 只更新到21/10/08
# https://data.gtimg.cn/flashdata/hushen/4day/sz/sz002739.js?maxage=43200&visitDstTime=1  # 只更新到21/05/27
# https://data.gtimg.cn/flashdata/hushen/daily/21/sz002739.js
# http://data.gtimg.cn/flashdata/hushen/latest/daily/sz000002.js?maxage=43201&visitDstTime=1
# https://data.gtimg.cn/flashdata/hushen/weekly/21/sz002739.js

# 06-03 16:09:00 后不再更新数据
tx_latest_day_quote_url = 'http://stock.gtimg.cn/data/get_hs_xls.php?id=ranka&type=1&metric=chr'
# https://ifzq.gtimg.cn/appstock/app/kline/mkline?param=sh000001,m60,,320&_var=m60_today&r=0.21206432970477884
# https://ifzq.gtimg.cn/appstock/app/kline/mkline?param=sz002739,m30,,250
# https://web.ifzq.gtimg.cn/appstock/app/kline/mkline?param=sz002739,m30,,250  # 无法访问
# http://ifzq.gtimg.cn/appstock/app/kline/mkline?param=sz002739,m30,,250  # OK
tx_min_url = 'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={code},{period},,{count}'

# http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param=sz002739,day,,,350,qfq&r=0.7773272375526847
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
"""
5、10、30、60分钟
http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz002095&scale=60&ma=no&datalen=1023

JSON qianfuquan-前复权；houfuquan-后复权 注意，无法获取未复权的数据
http://finance.sina.com.cn/realstock/company/sz300502/qianfuquan.js?d=2021-10-15

XLS文件；股票历史成交明细  服务已下线
http://market.finance.sina.com.cn/downxls.php?date=2021-10-16&symbol=sz300598

HTML文本；指定日期范围内的股票分价表。
查询日期范围过大！请重新选择日期范围。 startdate 是必须参数
http://market.finance.sina.com.cn/pricehis.php?symbol=sz300598&startdate=2011-08-17&enddate=2021-10-16
"""
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
http://app.finance.ifeng.com/list/stock.php?t=hs&f=chg_pct&o=desc&p=1   # 昨收盘  html
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

"""
requests.get(url=) 可获取到结果
返回说明:
url 中参数带了 jQuery112309207099259936209_1634192174602( 时, 返回结果为 "jQuery112309207099259936209_1634192174602( json )"
url 中参数不带 jQuery112309207099259936209_1634192174602( 时, 返回结果为 json, {"version": ..., "result": {"pages":2,"data":[]} }

两融
http://datacenter-web.eastmoney.com/api/data/get?callback=datatable7889269&type=RPTA_WEB_RZRQ_GGMX&sty=ALL&source=WEB&p=2&ps=50&st=RZJME&sr=-1&filter=(date='2021-10-13')&pageNo=2&pageNum=2&pageNumber=2&_=1634188585959
https://datacenter-web.eastmoney.com/api/data/get?type=RPTA_WEB_RZRQ_GGMX&sty=ALL&source=WEB&p=1&ps=50&st=RZJME&sr=-1&filter=(date=%272021-10-13%27)

北向
http://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery1123008784431323063169_1634189178773&sortColumns=ADD_MARKET_CAP&sortTypes=-1&pageSize=50&pageNumber=2&reportName=RPT_MUTUAL_STOCK_NORTHSTA&columns=ALL&source=WEB&client=WEB&filter=(TRADE_DATE='2021-10-12')(INTERVAL_TYPE="1")
https://datacenter-web.eastmoney.com/api/data/v1/get?pageSize=50&pageNumber=2&reportName=RPT_MUTUAL_STOCK_NORTHSTA&columns=ALL&filter=(TRADE_DATE=%272021-10-12%27)(INTERVAL_TYPE=%221%22)

机构调研
http://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery112307016057843016501_1634189562292&sortColumns=NOTICE_DATE&sortTypes=-1&pageSize=50&pageNumber=1&reportName=RPT_ORG_SURVEY&columns=ALL&quoteColumns=f2~01~SECURITY_CODE~CLOSE_PRICE,f3~01~SECURITY_CODE~CHANGE_RATE&source=WEB&client=WEB&filter=(NUMBERNEW="1")(IS_SOURCE="1")(SECURITY_CODE="300598")(RECEIVE_START_DATE>'2018-10-14')

两融-个股
http://datacenter-web.eastmoney.com/api/data/get?callback=datatable3471941&type=RPTA_WEB_RZRQ_GGMX&sty=ALL&source=WEB&st=date&sr=-1&p=2&ps=50&filter=(scode="300598")&pageNo=2&pageNum=2&pageNumber=2&_=1634192022163

北向-个股
http://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery112309207099259936209_1634192174602&sortColumns=TRADE_DATE&sortTypes=-1&pageSize=50&pageNumber=2&reportName=RPT_MUTUAL_HOLDSTOCKNORTH_STA&columns=ALL&source=WEB&client=WEB&filter=(SECURITY_CODE="300598")(TRADE_DATE>='2021-07-14')
"""