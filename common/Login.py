#!/usr/bin/env python
# encoding: utf-8
'''
@author: yanghong
@file: Login.py
@time: 2019/6/20 11:29
@desc:
'''

from common.base2 import Base
from common.logger import Log
from config.readconfig import Readconfig

log = Log().getlog()


def login_admin(base, user='18400000001', pwd='000001'):
    rdconf = Readconfig()
    base.server_ip = rdconf.config_get('url')
    login_api = 'adminApi/admin/sys/login'
    login_data = {'username': user,
                  'password': pwd,
                  'captcha': '1111'}
    try:
        log.info('开始请求后台登录接口,本次测试使用数据%s' % login_data)
        r = base.sendRequest(login_api, 'POST', data=login_data)
        assert r.json()['code'] == 200, '后台登录失败，本次测试无效'
        log.info('后台登录接口请求成功')
    except Exception as e:
        log.error(e)
        raise


if __name__ == "__main__":
    base = Base()
    login_admin(base)
