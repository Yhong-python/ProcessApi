#!/usr/bin/env python
# encoding: utf-8
'''
@author: yanghong
@file: readconfig.py
@time: 2019/8/21 10:28
@desc:
'''
# coding=utf-8

import configparser
import os

cur_path = os.path.dirname(os.path.realpath(__file__))
cfg_path = os.path.join(cur_path, 'config.ini')


class Readconfig:
    def __init__(self):
        self.conf = configparser.RawConfigParser()
        self.conf.read(cfg_path, encoding='utf-8')

    def config_get(self, key):
        switch = self.conf.get('environment', 'switch')
        section = None
        if switch == str(0):
            section = 'test'
        elif switch == str(1):
            section = 'pre'
        config_get = self.conf.get(section, key)
        return config_get


if __name__ == "__main__":
    a = Readconfig()
    print(a.config_get('url'))
    print(a.config_get('host'))
    print(a.config_get('port'))
    print(a.config_get('user'))
    print(a.config_get('passwd'))
    print(a.config_get('db_name'))
