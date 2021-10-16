# -*- coding: utf-8 -*-

"""
AD_:=SUM(((CLOSE-LOW)-(HIGH-CLOSE))/(HIGH-LOW)*VOL,0);
AD:AD_;
E:MA(AD_, 30);

AD_:=SUM(((CLOSE-LOW)-(HIGH-CLOSE))/(HIGH-LOW)*VOL,0);
EMA3 := EMA(AD_, 3);
EMA10 := EMA(AD_,10);
ADOSC: (EMA3 - EMA10);
ZERO : 0;
"""
from indicator import ma, ema
from indicator.decorator import computed


@computed(column_name='adosc')
def compute_ad(quote):
    _ = ((quote.close - quote.low) - (quote.high - quote.close)) / (quote.high - quote.low) * quote.volume
    ad_ = _.cumsum()

    quote['ad'] = ad_
    quote['ad_ma'] = ma.ma(ad_, 30)
    quote['adosc'] = ema.ema(ad_, 3) - ema.ema(ad_, 10)

    return quote
