#!/usr/bin/env python
# encoding: utf-8
'''
@author: yanghong
@file: RandomUtil.py
@time: 2019/10/12 16:02
@desc:
'''
import random


def GBK2312(num):
    str = ''
    for i in range(num):
        head = random.randint(0xb0, 0xf7)
        body = random.randint(0xa1, 0xf9)  # 在head区号为55的那一块最后5个汉字是乱码,为了方便缩减下范围
        val = '{0:x}{1:x}'.format(head, body)
        str += bytes.fromhex(val).decode('gb2312')
    return str


def strings(num):
    str = ''
    all = '0123456789qwertyuiopasdfghjklzxcvbnm'
    for i in range(num):
        str += random.choice(all)
    return str


def getPhone(forward3='183'):
    tel = forward3
    for i in range(8):
        tel += str(random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 0]))
    return tel
