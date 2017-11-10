#!/usr/bin/evn python
# -*- coding:utf-8 -*-

__author__ = 'Xuxh'

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import csv
import math

# https://pypi.python.org/pypi/numpy
# https://pypi.python.org/pypi/matplotlib
# http://matplotlib.org/index.html


# multial_bars
def draw_bar(labels, data_list, data_desc, width):
    """

    :param labels: xticklables, this is list
    :param quants: data list [[],[]]
    :param data_desc: this is list to describe data for upper every list
    :return:
    """
    count = len(labels)
    min_ident = math.ceil(width * count)
    x = np.linspace(min_ident, min_ident*count, count)
    data_category = len(data_list)
    total_width = width * data_category
    i = 0
    for dt in data_list:
        plt.bar(x + width*i, dt, width=width, label=data_desc[i])
        i += 1

    plt.xticks(x + total_width/2 - width/2, labels)
    plt.xlabel('API Alias')
    plt.ylabel('Send/Receive(Bytes)')
    # # title
    plt.title('API Traffic Data', bbox={'facecolor':'0.8', 'pad':5})
    plt.legend()
    plt.grid(True)
    plt.savefig(r"E:\bar.png")
    #plt.show()
    plt.close()


def draw_plot(labels, data_list, data_desc, width):

    count = len(labels)
    min_ident = math.ceil(width * count)
    x = np.linspace(min_ident, min_ident*count, count)
    data_category = len(data_list)
    total_width = width * data_category
    i = 0
    for dt in data_list:
        plt.plot(x + width*i, dt, width=width, label=data_desc[i])
        i += 1

    plt.xticks(x + total_width/2 - width/2, labels)
    plt.xlabel('API Alias')
    plt.ylabel('Send/Receive(Bytes)')
    # # title
    plt.title('API Traffic Data', bbox={'facecolor':'0.8', 'pad':5})
    plt.legend()
    plt.grid(True)
    plt.savefig(r"E:\bar.png")
    #plt.show()
    plt.close()


if __name__ == '__main__':

    with open(r'D:\output_traffic.csv', 'r') as rfile:
        xticklables = []
        bar_list = []
        bar1 = []
        bar2 = []
        reader = csv.reader(rfile)
        for ln in reader:
            if ln[0] == 'name':
                continue
            xticklables.append(ln[0])
            bar1.append(int(ln[6]))
            bar2.append(int(ln[9]))
        bar_list.append(bar1)
        bar_list.append(bar2)
        bar_list.append([3500,4000,4600,5000])
        data_description = ['Send_Data', 'Receive_Data', 'Test_Data']
        width = 0.4
    draw_bar(xticklables, bar_list, data_description, width)