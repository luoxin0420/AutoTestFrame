#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Xuxh'

from numpy import mean, median, max
from scipy.stats import mode
from numpy import ptp, var, std
from numpy import array
from numpy.random import normal, randint
import string


def get_special_value(data_list, data_type):

    data_type = data_type.lower()

    fun = {
    "max": max,
    "mean": mean,  # 矩阵平均值
    "median": median, # 中位数
    "mode": mode,  # 众数,
    "xmax-xmin": ptp,  # 极差
    "variance": var,  # 方差
    "std-deviation": std}# 标准差

    if data_type in fun.keys():
        value = fun[data_type](data_list)
    elif data_type == 'avg':
        value = sum(data_list)/len(data_list)
    elif data_type == 'cv':
        value = std(data_list)/mean(data_list) # 变异
    else:
        value = 0

    return value


def get_special_list(start, end, size, data_type):

    data_type = data_type.lower()

    fun = {
        "normal": normal,  # 正态分布
        "randinit": randint # 均匀分布
    }

    if data_type == 'array':
        result = array(range(start,end))
    else:
        result = fun[data_type](start,end, size=size)

    print result


def handle_performance_data(fname, data_type):

    data = []

    with open(fname,'rb') as rfile:

        for ln in rfile:
            data.append(string.atof(ln.split(',')[1]))

    return get_special_value(data, data_type)


if __name__ == '__main__':

    get_special_list(0,10,10,'normal')