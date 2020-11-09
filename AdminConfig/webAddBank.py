#!/usr/bin/env python
# encoding: utf-8
'''
@author: yanghong
@file: webAddBank.py
@time: 2019/10/22 15:46
@desc:
'''
import json

from AdminConfig.addNewLoanProces import Test_addNewLoanProcess
from AdminConfig.updataConfig import Test_updataProcessConfig
from common.DB import DB_config
from common.Login import login_admin
from common.Login_Qian import login
from common.base2 import Base
from common.logger import Log

log = Log().getlog()


class Test_Process(object):
    def __init__(self, PartnerId, baseParentId):
        self.log = log
        self.db = DB_config()
        self.base = Base()
        login_admin(self.base)
        self.PartnerId = PartnerId
        self.baseParentId = baseParentId

    def getProcessId(self):
        sql = "SELECT id FROM ovf_process_info ORDER BY id DESC LIMIT 0,1"
        self.db.excute_otherdb(sql, 'qp_itfin2_data_%s' % self.baseParentId)
        self.log.info("执行sql语句：%s" % sql)
        processId = self.db.get_one()[0]
        return processId

    def addBank(self, bankid, user, pwd):
        login(self.base, user=user, pwd=pwd)
        apiUrl = 'wwwApi/cptPartnerBank/save'
        processId = self.getProcessId()
        bankConfigList = [{"bankId": bankid,
                           "name": "接口自动化",  # 业务名称，执行前注意是否添加的这个业务的流程
                           "id": processId,
                           "partnerId": self.PartnerId,
                           "productType": "74",  # 业务ID，执行前注意是否添加的这个业务的流程
                           "processId": processId,
                           "tabNameId": str(processId),
                           "dayRate": "1",
                           "monthRate": "1",
                           "yearRate": "1",
                           "bizAreaTwo": [{"code": "11", "name": "北京市", "children": [
                               {"code": "1101", "name": "市辖区", "children": [{"code": "110101", "name": "东城区"}]}]}],
                           "bizArea": ["110101"]}]
        sendData = {
            "data": json.dumps({
                "bankId": bankid,
                "linkman": "111111111111111",
                "phone": "11111111111",
                "shroffAccount": "111111111111111111111111",
                "shroffName": "啊",
                "openingBank": "啊啊啊",
                "returnMoneyTime": 1,
                "bankConfigList": bankConfigList})}
        r = None
        self.log.info('本次请求使用数据%s' % sendData)
        try:
            r = self.base.sendRequest(apiUrl, 'POST', data=sendData)
        except Exception as e:
            self.log.info('前台合作银行新建失败')
            self.log.error(e, exc_info=True)
            raise
        if r.json()['code'] == 200:
            self.log.info("前台合作银行新建成功")
        else:
            self.log.info('前台合作银行新建失败，返回结果%s' % r.json())

    def run(self, user, pwd):
        addData = Test_addNewLoanProcess(self.PartnerId, self.baseParentId).addNewProcess()
        bankid, processkey = addData[0], addData[1]
        Test_updataProcessConfig(processkey, self.baseParentId).getProcessScenesList()
        sql = "SELECT * FROM cpt_partner_bank WHERE bankId=%d AND parnterId=%d" % (bankid, self.PartnerId)
        self.db.excute_otherdb(sql, 'qp_itfin2_data_%s' % self.baseParentId)
        dbData = self.db.get_one()
        if dbData == None:  # 不存在时执行前台新建合作银行
            self.addBank(bankid, user=user, pwd=pwd)
            print('前台合作银行新建成功')
        else:
            print('前台合作银行已经新建过了,不需要重复执行')


if __name__ == "__main__":
    a = Test_Process(534, 532)
    a.run(user='16333333333', pwd='333333')
    # a.run(user='19999999999', pwd='999999')
    # a = Test_Process(308, 134)
    # a.run(user='18300000030', pwd='000030')
    # a = Test_Process(134, 134)
    # a.run(user='18300000010', pwd='000010')
