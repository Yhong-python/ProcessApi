#!/usr/bin/env python
# encoding: utf-8
'''
@author: yanghong
@file: base.py
@time: 2019/6/5 15:57
@desc:前台调用的请求基类
'''
import requests

from common.logger import Log
from config.readconfig import Readconfig

log = Log().getlog()
rdconf = Readconfig()


class Base:
    def __init__(self):
        global scheme, host, timeout, cj, server_ip
        self.params = {}
        self.headers = {}
        self.data = {}
        self.url = None
        self.files = {}
        self.state = 0
        self.methord = None
        self.s = requests.session()
        self.server_ip = rdconf.config_get('weburl')

    def set_host(self, host):
        self.host = host

    def get_host(self):
        return self.host

    # 设置http头
    def set_header(self, head=None):
        # if not head is None or head:
        if head:
            self.headers = head
        else:
            self.headers = {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                            "Accept": "application/json, text/plain, */*"}

    def get_header(self):
        return self.headers

    def set_port(self, port):
        """
        设置端口
        :param port:
        :return:
        """
        self.port = port

        # 设置方法

    def set_methord(self, methord):
        """

        :param methord:
        :return:
        """
        self.methord = methord

    def set_params(self, param):
        """
        set params
        :param param:
        :return:
        """
        self.params = param
        # print self.params

    def set_data(self, data):
        """
        set data
        :param data:
        :return:
        """
        self.data = data

    def set_url(self, url):
        """
        set url
        :param: interface url
        :return:
        """
        self.url = self.server_ip + '/' + url
        # print self.url

    def sendRequest(self, Interface, methord, data=None, param=None, files=None, cookies=None, verify=False):
        headers = self.headers
        self.url = self.server_ip + '/' + Interface
        self.methord = methord
        log.info("请求地址:" + self.url)
        req = ''
        try:
            if self.methord.upper() == 'POST':
                # log.info('url = %s' % self.url)
                # log.info("params = %s" % data)
                # log.info("params = %s" % type(data))
                req = self.s.request(method='POST', url=self.url, data=data, params=param, headers=headers, files=files,
                                     cookies=cookies, verify=verify)

            elif self.methord.upper() == 'GET':
                if data is None:
                    req = self.s.request(method='GET', url=self.url, params=param, headers=headers, files=files,
                                         cookies=cookies, verify=verify)
                else:
                    req = self.s.request(method='GET', url=self.url, params=param, data=data, headers=headers,
                                         files=files, cookies=cookies, verify=verify)
            elif self.methord.upper() == 'PUT':
                self.data = self.set_data(data)
                req = self.s.request(method='PUT', url=self.url, data=data, params=param, headers=headers, files=files,
                                     cookies=cookies, verify=verify)

            elif self.methord.upper() == 'DELETE':
                self.data = self.set_data(data)
                req = self.s.request(method='DELETE', url=self.url, data=data, params=param, headers=headers,
                                     files=files, cookies=cookies, verify=verify)

            # assert req.status_code == 200
            # log.info('code = %s' % str(code))
            # log.info('msg = %s' % repr(req.text))
            return req
        except Exception as e:
            log.info("请求失败")
            log.error("error: %s" % e, exc_info=True)
            raise
