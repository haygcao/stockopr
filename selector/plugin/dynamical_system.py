# -*- coding: utf-8 -*-
from indicator import dynamical_system


def dynamical_system_green(quote):
    quote = dynamical_system.dynamical_system(quote)

    return True if quote['dyn_sys'][-1] == 1 else False


def dynamical_system_red(quote):
    quote = dynamical_system.dynamical_system(quote)

    return True if quote['dyn_sys'][-1] == -1 else False


def dynamical_system_blue(quote):
    quote = dynamical_system.dynamical_system(quote)

    return True if quote['dyn_sys'][-1] == 0 else False


def dynamical_system_not_red(quote):
    quote = dynamical_system.dynamical_system(quote)

    return True if quote['dyn_sys'][-1] >= 0 else False