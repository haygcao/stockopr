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
    code varchar(8),
    name varchar(16),
    price_divisor_date date,
    price_divisor_adj_price decimal(10, 3),
    type varchar(8) default 'A');

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
-- create table if not exists quote (code varchar(8), trade_date date, open float, high float, low float, close float, volume bigint, turnover bigint);

create table if not exists quote (
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

create table if not exists financial_data (
    code varchar(8),
    trade_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    pe float,
    mcap bigint,
    tcap bigint,
    mfsum float,
    mfratio2 bigint,
    mfratio10 bigint
    );

-- 建仓
create table selected(
    code varchar(8),
    added_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    class varchar(32),
    `rank` int
    );

create table selected_history(
    code varchar(8),
    added_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    class varchar(8),
    `rank` int
    );

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

-- create index quote_code on quote(code);
create index quote_trade_date on quote(trade_date);
create unique index quote_code_trade_date on quote(code,trade_date);

-- create index quote_code on quote_myisam(code);
-- create index quote_trade_date on quote_myisam(trade_date);
-- create unique index quote_code_trade_date on quote_myisam(code,trade_date);

-- mysql> insert into history_price (code, trade_day) values("600839","2015-12-25"); --date 可以这样插入
-- ERROR 1062 (23000): Duplicate entry '600839-2015-12-25' for key 'history_price_code_trade_day'



-- current_date() CURRENT_timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, all is ok

create table fund_basic (code varchar(8), name varchar(32), scale decimal(10, 2));
create unique index fund_basic_code on fund_basic(code);

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
  stop_profit decimal(5, 2) not null,
  profitability_ratios decimal(6, 3),
  status varchar(8)
  PRIMARY key (id)
);


-- 按日更新
create table asset(
  `date` timestamp,
  total decimal(10, 3),
  avail decimal(10, 3),
  market_value decimal(10, 3),
  total_profit decimal(10, 3),
  today_profit decimal(10, 3)
);


-- 按日更新
create table `position` (
  `date` timestamp,
  code varchar(8),
  `position` int,
  cost_price decimal(10, 3),
  price decimal(10, 3),
  cost decimal(10, 3),
  market_value decimal(10, 3),
  total_profit decimal(10, 3),
  total_profit_percent decimal(6, 3),
  today_profit decimal(10, 3),
  today_profit_percent decimal(6, 3),
  position_percent decimal(6, 3),
  open_date timestamp
);

-- 逐次更新
create table operation_detail(
  order_id int,
  `time` timestamp,
  code varchar(8),
  operation varchar(16),
  price decimal(10, 3),
  `count` int,
  amount int,
  cost decimal(10, 3),
  position_remain int,
  profit decimal(10, 3)
);

drop table asset;
drop table trade_order;
drop table position;
drop table operation_detail;
create index asset_date on asset(date);
create index trade_order_code_date on trade_order(code, date);
create index position_code_date on `position`(code, date);
create index operation_detail_code_date on operation_detail(code, time);
create index operation_detail_order_id on operation_detail(order_id);