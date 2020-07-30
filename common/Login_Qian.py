#!/usr/bin/env python
# encoding: utf-8
'''
@author: yanghong
@file: Login_Qian.py
@time: 2019/8/21 14:53
@desc:
'''
from common.base2 import Base
from common.logger import Log
from config.readconfig import Readconfig

rdconf = Readconfig()


def login(base, user=rdconf.config_get('webusername'), pwd=rdconf.config_get('webpasswd')):
    log = Log().getlog()
    login_api = 'wwwApi/admin/sys/login'
    base.server_ip = rdconf.config_get('weburl')
    login_data = {'username': user,
                  'password': pwd,
                  'captcha': '1111'}
    cookies = {'userName': '',
               'userPwd': '',
               'JSESSIONID': '',
               'userSessionId': ''}
    r = None
    try:
        log.info('开始请求前台登录接口,本次测试使用数据%s' % login_data)
        r = base.sendRequest(login_api, 'POST', data=login_data, cookies=cookies)
        assert r.json()['code'] == 200, '前台登录失败，本次测试无效'
        log.info('前台登录接口请求成功')
    except Exception as e:
        log.info(r.text)
        log.error(e, exc_info=True)
        raise


if __name__ == "__main__":
    base = Base()
    login(base, user='18300000001', pwd='000001')
