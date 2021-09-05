# -*- coding: utf-8 -*-
from acquisition import quote_db
from indicator import dynamical_system


def dynamical_system_green(quote, period):
    quote = quote_db.get_price_info_df_db_week(quote, period_type='W')
    quote = dynamical_system.dynamical_system(quote)

    return quote['dyn_sys'][-1] == 1


def dynamical_system_red(quote, period):
    quote = quote_db.get_price_info_df_db_week(quote, period_type='W')
    quote = dynamical_system.dynamical_system(quote)

    return quote['dyn_sys'][-1] == -1


def dynamical_system_blue(quote, period):
    quote = quote_db.get_price_info_df_db_week(quote, period_type='W')
    quote = dynamical_system.dynamical_system(quote)

    return quote['dyn_sys'][-1] == 0


def dynamical_system_not_red(quote):
    quote = quote_db.get_price_info_df_db_week(quote, period_type='W')
    quote = dynamical_system.dynamical_system(quote)

    return quote['dyn_sys'][-1] >= 0
