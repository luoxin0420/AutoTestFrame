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

DIAGRAM_DICT = {'MEMORY': {'title': 'Memory Monitoring', 'ylabel': 'Total Memory(KB)', 'xlabel': 'Loop Number'},\
                'CPU': {'title': 'CPU Monitoring','ylabel': 'CPU Percent(%)', 'xlabel': 'Loop Number'}, \
                'LAUNCH TIME': {'title': 'Launch Time (Hard Time/Soft Time)', 'ylabel': 'Launch Time (MS)', 'xlabel':'Loop Number'},\
                'TRAFFIC': {'title': 'Traffic Data', 'ylabel': 'Send/Receive(Bytes)', 'xlabel': 'Loop Number'},\
                'UI FLUENCY': {'title': 'UI Fluency Monitoring', 'ylabel': 'Launch Time (MS)', 'xlabel':'Loop Number'}}


# multial_bars
def draw_bar(labels, data_list, data_desc, width, out_file, dict_flag):
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
    plt.xlabel(DIAGRAM_DICT[dict_flag]['xlabel'])
    plt.ylabel(DIAGRAM_DICT[dict_flag]['ylabel'])
    # # title
    plt.title(DIAGRAM_DICT[dict_flag]['title'], bbox={'facecolor':'0.8', 'pad':5})
    plt.legend()
    plt.grid(True)
    plt.savefig(out_file)
    #plt.show()
    plt.close()


def draw_plot(labels, data_list, data_desc, out_file, dict_flag):

    i = 0
    for dt in data_list:
        plt.plot(labels,dt, "+-",label=data_desc[i])
        i += 1
    plt.xlabel(DIAGRAM_DICT[dict_flag]['xlabel'])
    plt.ylabel(DIAGRAM_DICT[dict_flag]['ylabel'])
    # # title
    plt.title(DIAGRAM_DICT[dict_flag]['title'], bbox={'facecolor':'0.8', 'pad':5})
    plt.legend()
    plt.grid(True)
    plt.savefig(out_file)
    #plt.show()
    plt.close()


if __name__ == '__main__':

    # with open(r'D:\output_traffic.csv', 'r') as rfile:
    #     xticklables = []
    #     bar_list = []
    #     bar1 = []
    #     bar2 = []
    #     reader = csv.reader(rfile)
    #     for ln in reader:
    #         if ln[0] == 'name':
    #             continue
    #         xticklables.append(ln[0])
    #         bar1.append(int(ln[6]))
    #         bar2.append(int(ln[9]))
    #     bar_list.append(bar1)
    #     bar_list.append(bar2)
    #     bar_list.append([3500,4000,4600,5000])
    #     data_description = ['Send_Data', 'Receive_Data', 'Test_Data']
    #     width = 0.4
    # draw_bar(xticklables, bar_list, data_description, width)

    # with open(r'E:\LaunchTimeCollector.csv', 'r') as rfile:
    #     data_description = ['Soft reboot', 'Hard reboot']
    #     soft = []
    #     hard = []
    #     count = 0
    #     plot = []
    #     reader = csv.reader(rfile)
    #     for line in reader:
    #         if count % 2 == 0:
    #
    #             soft.append(line[1])
    #         else:
    #             hard.append(line[1])
    #         count += 1
    #     plot.append(soft)
    #     plot.append(hard)
    #     xtick = range((len(soft) if len(soft) > len(hard) else len(hard)))
    #     outfile = r"e://plot.png"
    #     draw_plot(xtick, plot, data_description, outfile,'MEMORY')

    outfile = r"e://plot2.png"
    draw_plot(range(8), [[79123, 79331, 79000, 82340, 90000, 87000, 93450, 95000]], ['memory'], outfile, 'MEMORY')