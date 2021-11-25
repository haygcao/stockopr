create user stockopr@localhost identified by '111111';
grant all privileges on *.* to 'stockopr'@localhost;
ALTER USER 'stockopr'@'localhost' IDENTIFIED WITH mysql_native_password BY '111111';

-- 如下脚本创建数据库yourdbname，并制定默认的字符集是utf8。
-- CREATE DATABASE IF NOT EXISTS yourdbname DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
-- 如果要创建默认gbk字符集的数据库可以用下面的sql:
-- create database yourdb DEFAULT CHARACTER SET gbk COLLATE gbk_chinese_ci;
-- create database stock default charset utf8;

create database if not exists stock default charset utf8;
use stock;

-- 与股价挂钩的指标，就不记录历史数据了
-- 基本信息，代码，名称，市盈率，市净率，板块，概念，
-- 板块使用id
create table if not exists basic_info(
    code varchar(8) NOT NULL,
    name varchar(16),
    industry_tdx varchar(16),
    industry_zjh varchar(16),
    industry_sw varchar(16),
    price_divisor_date date,
    price_divisor_adj_price decimal(10, 3),
    type varchar(8) default 'A');

-- 板块指数(通达信)
-- type 说明:
-- 2 通达信行业板块 3 地区板块 4 概念板块 5 风格板块 8 证监会行业板块
-- eps: 每股收益   bps: 每股资产
create table if not exists index_info(
    code varchar(8) NOT NULL,
    name varchar(16),
    eps float,
    bps float,
    negotiable_share decimal(20, 6),
    share decimal(20, 6),
    type int,
    major int,
    minor int,
    industry varchar(16),
    update_date date,
    PRIMARY key (code));

CREATE TABLE future_variety (
    code varchar(8),
    name varchar(8),
    type varchar(8),
    prev_dc varchar(8),
    curr_dc varchar(8),
    next_dc varchar(8)
    );

-- 日期 开盘价 最高价 最低价 收盘价 成交量(手) 成交金额(万元)
-- 昨收 涨跌额 涨跌幅(%) 振幅(%) 换手率(%) 量比
-- 总市值 mktcap(万元) 流通市值 nmc(万元)
-- create table if not exists quote (code varchar(8), trade_date date, open float, high float, low float, close float, volume bigint, turnover bigint);
-- xr 即 exit right, 除权
create table if not exists quote (
    code varchar(8) NOT NULL,
    trade_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    close float,
    high float,
    low float,
    open float,
    yest_close float,
    rs_rating float,
    xr tinyint(1) default 0,
    price_change float,
    percent float,
    turnover_ratio float,
    volume bigint,
    amount bigint,
    per float,
    pb float,
    mktcap decimal(20, 6),
    nmc decimal(20, 6),
    quantity_relative_ratio float,
    amplitude float,
    five_minute float
    );

create table if not exists temp_quote (
    code varchar(8),
    trade_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    close float,
    high float,
    low float,
    open float,
    yestclose float,
    updown float,
    percent float,
    hs float,
    volume bigint,
    turnover bigint,
    lb float,
    wb float,
    zf float,
    five_minute float
    );

create table if not exists finance (
	code varchar(8),
	report_date timestamp,
	eps decimal(8, 4),
	bps decimal(8, 4),
	per_capital_reserve decimal(8, 4),
	per_unassign_profit decimal(8, 4),
	per_netcash decimal(8, 4),
	totaloperatereve decimal(16, 2),
	gross_profit decimal(16, 2),
	parentnetprofit  decimal(16, 2),
	dedu_parent_profit decimal(16, 2),
	totaloperatereve_yoy_ratio decimal(12, 2),
	parentnetprofit_yoy_ratio decimal(12, 2),
	dpnp_yoy_ratio decimal(12, 2),
	roe_diluted decimal(12, 2),
	jroa decimal(12, 2),
	net_profit_ratio decimal(12, 2),
	gross_profit_ratio decimal(12, 2),
	eps_std_rank float,
	nmc decimal(20, 6),
	fmv decimal(20, 6),
	fmvp float
);

-- 建仓
create table portfolio(
    code varchar(8),
    added_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status varchar(32),
    class varchar(32),
    `rank` int
    );

create table portfolio_history(
    code varchar(8),
    added_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status varchar(32),
    class varchar(32),
    `rank` int
    );

create unique index portfolio_code_class on portfolio(code, class);
create index portfolio_status on portfolio(status);
create unique index portfolio_history_code_class on portfolio_history(code, class);
create index portfolio_history_status on portfolio_history(status);

-- 交易记录
create table trade_detail (
    code varchar(8),
    trade_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    op varchar(8),
    price float,
    count int,
    account varchar(16)
    );

create table trade_detail_history (
    code varchar(8),
    trade_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    op varchar(8),
    price float,
    count int,
    account varchar(16)
    );

-- 业务逻辑
-- 监控
create table bought (
    code varchar(8),
    date timestamp
    );
-- 平仓
create table cleared (
    code varchar(8),
    date timestamp
    );

-- 账户
-- op: i o s b a(adjust)
create table account_detail (
    code varchar(16),
    trade_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    op varchar(8),
    price float,
    count int
    );

-- 索引
create unique index basic_info_code on basic_info(code);
create index basic_info_industry_tdx on basic_info(industry_tdx);
-- create index basic_info_industry_zjh on basic_info(industry_zjh);
-- create index basic_info_industry_sw on basic_info(industry_sw);


-- create index quote_code on quote(code);
create index quote_trade_date on quote(trade_date);
create unique index quote_code_trade_date on quote(code,trade_date);

-- create index quote_code on quote_myisam(code);
-- create index quote_trade_date on quote_myisam(trade_date);
-- create unique index quote_code_trade_date on quote_myisam(code,trade_date);

-- mysql> insert into history_price (code, trade_day) values("600839","2015-12-25"); --date 可以这样插入
-- ERROR 1062 (23000): Duplicate entry '600839-2015-12-25' for key 'history_price_code_trade_day'

create unique index finance_code_date on finance(code, report_date);

-- current_date() CURRENT_timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, all is ok

create table fund_basic (code varchar(8), name varchar(32), scale decimal(10, 2), `date` date);
create unique index fund_basic_code_date on fund_basic(code, date);

-- 持股数（万股）	持仓市值（万元）
create table fund_stock (
    fund_code varchar(8),
    fund_date date,
    code varchar(8),
    percent decimal(10, 2),
    price decimal(10, 2),
    num decimal(20, 2),
    market_value decimal(20, 2),
    fund_url varchar(256),
    crawl_date date);

create unique index fund_stock_fund_code_date_code on fund_stock(fund_code, fund_date, code);

-- 资金管理
--
create table trade_order (
  id int NOT NULL AUTO_INCREMENT,
  `date` date not null,
  code varchar(8) not null,
  capital_quota decimal(10, 3),
  `position` int not null,
  open_price decimal(5, 2) not null,
  stop_loss decimal(5, 2) not null,
  risk_rate decimal(5, 2),
  risk_rate_total decimal(5, 2),
  stop_profit decimal(5, 2) not null,
  profitability_ratios decimal(6, 3),
  strategy varchar(32),
  status varchar(8),
  account_id varchar(32)
  PRIMARY key (id)
);


-- 按日更新
create table asset(
  `date` date,
  period date,
  origin decimal(10, 3),
  total decimal(10, 3),
  net decimal(10, 3),
  avail decimal(10, 3),
  deposit decimal(10, 3),
  market_value decimal(10, 3),
  position_percent decimal(6, 3),
  total_profit decimal(10, 3),
  total_profit_percent decimal(6, 3),
  today_profit decimal(10, 3),
  account_id varchar(32)
);


-- 按日更新
create table `position` (
  `date` date,
  code varchar(8),
  total int,
  avail int,
  cost_price decimal(10, 3),
  price decimal(10, 3),
  cost decimal(10, 3),
  market_value decimal(10, 3),
  total_profit decimal(10, 3),
  total_profit_percent decimal(6, 3),
  today_profit decimal(10, 3),
  today_profit_percent decimal(6, 3),
  position_percent decimal(6, 3),
  open_date timestamp,
  account_id varchar(32),
  op_type varchar(32)
);

-- 逐次更新
create table operation_detail(
  order_id int NOT NULL AUTO_INCREMENT,
  `time` timestamp,
  code varchar(8),
  operation varchar(16),
  price decimal(10, 3),
  price_trade decimal(10, 3),
  price_limited decimal(10, 3),
  `count` int,
  amount int,
  cost decimal(10, 3),
  position_remain int,
  profit decimal(10, 3),
  account_id varchar(32),
  op_type varchar(32)
);

-- alter table asset drop index asset_date;
create unique index asset_date_account_id on asset(date, account_id);
create unique index trade_order_code_date_account_id on trade_order(code, date, account_id);
create unique index position_code_date_account_id on `position`(code, date, account_id);
create unique index operation_detail_code_date_account_id on operation_detail(code, time, account_id);
create index operation_detail_order_id on operation_detail(order_id);

-- 市场数据
create table market(
  trade_date date,
  count int,
  new_high_y int,
  new_low_y int,
  new_high_h int,
  new_low_h int,
  new_high_s int,
  new_low_s int,
  new_high_m int,
  new_low_m int,
  new_high_w int,
  new_low_w int,
  up int,
  down int,
  up_ema52 int,
  up_ema26 int,
  up_ema13 int,
  PRIMARY key (trade_date)
);

-- 股本
create table equity(
  code varchar(8),
  date date,
  market varchar(8),
  category int,
  liutong_hongli_panqian decimal(20, 9),
  zongguben_peigujia_qian decimal(20, 9),
  zongguben_songgu_qian decimal(20, 9),
  zongguben_peigu_hou decimal(20, 9)
);
create unique index equity_code_date_category on equity(code, date, category);

insert into index_info (code, name) value ('0000001', '上证指数'), ('1399001', '深证成指'), ('1399006', '创业板指'), ('0000688', '科创50)');
commit;