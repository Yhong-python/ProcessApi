#!/usr/bin/env python
# encoding: utf-8
'''
@author: yanghong
@file: get_bpmn.py
@time: 2019/6/20 16:58
@desc:
'''

import os


def get_lastest_bpmn():
    cur_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    bpmn_path = os.path.join(cur_path, 'bpmn')
    if not os.path.exists(bpmn_path): os.mkdir(bpmn_path)
    file_lists = list(os.listdir(bpmn_path))  # 列表展示bpmn目录下的所有文件
    file_lists.sort(key=lambda x: os.path.getmtime(os.path.join(bpmn_path, x)))  # 按创建时间排序
    try:
        lastest_bpmn = os.path.join(bpmn_path, file_lists[-1])  # 取最新的文件
        return lastest_bpmn
    except Exception as e:
        print('暂无bpmn文件', e)


if __name__ == "__main__":
    print(get_lastest_bpmn())
    print(os.path.split(get_lastest_bpmn()))
