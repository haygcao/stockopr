
tx_latest_day_quote_url = 'http://stock.gtimg.cn/data/get_hs_xls.php?id=ranka&type=1&metric=chr'
tx_min_url = 'https://web.ifzq.gtimg.cn/appstock/app/kline/mkline?param={code},{period},,{count}'
# tx_day_url = 'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param={code},{period},{start_date},,{count},qfq'  # 2020-7-16,2021-5-7,
tx_day_url = 'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param={code},{period},{start_date},{end_date},{count},qfq'
xl_min_quote_url = 'https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData?symbol={code}&scale={period}&ma=no&datalen={count}'
xl_realtime_quote_url = 'http://hq.sinajs.cn/list={code}'
xl_day_price_url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?num=80&sort=code&asc=0&node=%s&symbol=&_s_r_a=page&page=%s'

fh_day_url = 'http://api.finance.ifeng.com/akdaily/?code=sh600000&type=last'
fh_min_url = 'http://api.finance.ifeng.com/akmin?scode=sh000300&type=30'

fh_page_url = 'http://app.finance.ifeng.com/list/stock.php?t=hs&f=chg_pct&o=desc&p=1'

tx_last_url = 'https://qt.gtimg.cn/q=sh688131,sh688319,sz300502&r=449365993'