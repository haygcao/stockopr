# -*- coding: utf-8 -*-
from acquisition import quote_db
from indicator import dynamical_system


def dynamical_system_green(quote, period, back_days):
    quote = quote_db.resample_quote(quote, period_type='W')
    quote = dynamical_system.dynamical_system(quote)

    return quote['dyn_sys'][-1] == 1


def dynamical_system_red(quote, period, back_days):
    quote = quote_db.resample_quote(quote, period_type='W')
    quote = dynamical_system.dynamical_system(quote)

    return quote['dyn_sys'][-1] == -1


def dynamical_system_blue(quote, period, back_days):
    quote = quote_db.resample_quote(quote, period_type='W')
    quote = dynamical_system.dynamical_system(quote)

    return quote['dyn_sys'][-1] == 0


def dynamical_system_not_red(quote):
    quote = quote_db.resample_quote(quote, period_type='W')
    quote = dynamical_system.dynamical_system(quote)

    return quote['dyn_sys'][-1] >= 0
