#!/usr/bin/env python
# encoding: utf-8
'''
@author: yanghong
@file: addNewLoanProces.py
@time: 2019/6/20 15:22
@desc:
'''
import json
import os

from common.DB import DB_config
from common.Login import login_admin
from common.base2 import Base
from common.get_bpmn import get_lastest_bpmn
from common.logger import Log

log = Log().getlog()


class Test_addNewLoanProcess(object):
    def __init__(self, PartnerId, baseParentId):
        self.log = log
        self.db = DB_config()
        self.PartnerId = PartnerId
        self.baseParentId = baseParentId
        self.base = Base()
        global bankid, processkey
        login_admin(self.base)

    def addbank(self, bankname):
        # #先查询是否已经存在该合作银行名称，存在则不新建，直接返回id和name
        querybanksql="select id,`name` FROM pms_department WHERE `name`='{}' ORDER BY id DESC".format(bankname)
        self.log.info("执行sql语句：%s" % querybanksql)
        self.db.excute(querybanksql)
        bankList = self.db.get_all()
        if bankList:#已存在时取后添加的银行数据
            print("该流程文件名称的经办行已存在，不需要重复添加")
            self.log.info("该流程文件名称的经办行已存在，不需要重复添加")
            for bankInfo in bankList:
                return bankInfo[0]   #返回银行id
        else: #不存在时需要新建银行
            # sql = "select MAX(id) from pms_department"
            # self.log.info("执行sql语句：%s" % sql)
            # self.db.excute(sql)
            # now_bankid = self.db.get_one()[0]

            self.log.info("该流程文件名称的经办行不已存在，需要进行添加")
            bankname = bankname
            addBankApi = 'adminApi/pmsDepartment/add'
            send_data = {
                'data': json.dumps(
                    {"id": None,
                     "name": bankname,
                     "parentId": -1,
                     "parentSeriesId": "$",
                     "sort": None,
                     "contactPerson": "测试市",
                     "contactTel": "11111111111", "idNo": "111111111111111111", "idCardFrontPic": None,
                     "idCardBackPic": None, "statusFalg": 1, "type": 4})
            }
            r = self.base.sendRequest(addBankApi, 'post', send_data)
            print("合作银行新建接口返回值：{}".format(r.json()))
            self.log.info("合作银行新建接口返回值：{}".format(r.json()))
            assert r.json()['code']==200,"合作银行新建失败"

            #查询最新一条数据
            sql="select id,`name` FROM pms_department WHERE type=4 ORDER BY id DESC"
            self.db.excute(sql)
            self.bankId = self.db.get_one()[0]

            #老的
            # self.bankId = now_bankid + 1

            #用id和name查询是否已经添加成功了
            veriftySql="select id,`name` FROM pms_department WHERE `name`='{}' AND id={}".format(bankname,self.bankId)
            self.log.info("执行sql语句：%s" % veriftySql)
            self.db.excute(veriftySql)
            bankInfo = self.db.get_one()
            if bankInfo:
                print("银行新增成功,id为：%d，name为：%s" % (self.bankId,bankname))
                self.log.info("银行新增成功,id为：%d" % self.bankId)
                return self.bankId
            else:
                raise Exception("合作银行新建后的id和name未对应上数据库中的数据")
    def querybaseparentId(self):
        '''根据组织机构id查询baseparentid'''
        sql = "select basePartnerId from pms_department WHERE id=%s" % self.PartnerId
        self.log.info("执行sql语句：%s" % sql)
        self.db.excute(sql)
        return self.db.get_one()[0]

    def productsetting(self):
        sql = "select enableFlag from odr_product_type_settings WHERE partnerId=%s AND typeId=74" % self.PartnerId
        self.log.info("执行sql语句：%s" % sql)
        self.db.excute(sql)
        try:
            enableFlag = self.db.get_one()[0]
        except Exception as e:
            enableFlag = 0
        if enableFlag == 0:
            print("该组织机构下未开启该业务类型，开始开启")
            self.log.info("该组织机构下未开启该业务类型，开始开启")
            api = 'adminApi/tblBusinessTypeSettings/updateEnableFlag'
            send_data = {
                'typeId': 74,  # 业务类型id
                'partnerId': self.PartnerId,
                'enableFlag': 1
            }
            self.log.info('请求参数%s' % send_data)
            r = self.base.sendRequest(api, 'post', send_data)
            print("请求业务类型开启接口的结果：{}".format(r.json()))
            self.log.info(r.json())
            if r.json()['code']==200:
                self.log.info("业务类型开启成功")
        else:
            print("该组织机构下已开启'接口自动化'业务类型")
            self.log.info("该组织机构下已开启'接口自动化'业务类型")

    def uploadProcessFile(self, processId=''):  # 新建新流程
        '''获取bpmn目录下最新的bpmn文件路径与文件名'''
        bpmn_filepath = get_lastest_bpmn()  # 每次取bpmn目录下最新的一个bpmn文件

        # print(bpmn_filepath)
        bpmn_filename = os.path.split(bpmn_filepath)[-1]
        upload_api = 'adminApi/ovfConfig/uploadProcessFile'
        file = {'file': (bpmn_filename, open(bpmn_filepath, 'rb'))}
        upload_data = {
            'basePartnerId': self.querybaseparentId(),  # 组织机构id，默认都选总公司的
            'processId': processId
        }
        r = self.base.sendRequest(upload_api, 'POST', data=upload_data, files=file)
        print("上传流程文件接口返回值：{}".format(r.json()))
        # self.log.info(r.text)
        self.log.info("上传流程文件接口返回值：{}".format(r.json()))
        try:
            assert r.json()['code'] == 200
            self.log.info('流程文件上传成功')
            print('流程文件上传成功')
        except Exception as e:
            self.log.error('接口请求失败', exc_info=True)
            self.log.error(e, exc_info=True)
            raise
        return r.json()['processkey'], r.json()['uuid']

    # 取机构的名称
    def getBaseCompanyName(self, partnerid):
        sql = "SELECT `name` FROM pms_department WHERE id=%s" % partnerid
        self.db.excute(sql)
        name = self.db.get_one()[0]
        return name

    # 取机构的角色
    def getRoleNameAndId(self, partnerid):
        apiUrl = 'adminApi/pmsRole/list'
        send_data = {
            'departmentId': partnerid,
        }
        r = self.base.sendRequest(apiUrl, 'POST', data=send_data)
        print("获取机构下的角色接口返回值：{}".format(r.json()))
        self.log.info("获取机构下的角色接口返回值：{}".format(r.json()))
        assert r.json()['code']==200
        print("获取机构下的角色接口成功")
        self.log.info("获取机构下的角色接口成功")
        rolelist = r.json()['data']
        for i in range(len(rolelist)):
            return rolelist[0]['rolename'], rolelist[0]['recid']

    def tasklist_to_diclist(self, processkey, uuid):
        '''获取流程文件中的流程任务列表并修改相应的字段'''
        gettasklist_api = 'adminApi/ovfConfig/taskList'
        send_data = {
            'processKey': processkey,
            'basePartnerId': self.querybaseparentId(),  # 组织机构id，默认都选总公司的
            'processId': '',
            'uuid': uuid
        }
        name = self.getBaseCompanyName(self.baseParentId)
        roledata = self.getRoleNameAndId(self.PartnerId)
        roleName, roleId = roledata[0], roledata[1]
        r = self.base.sendRequest(gettasklist_api, 'POST', data=send_data)
        print("获取流程文件中的场景列表接口返回值:{}".format(r.json()))
        self.log.info("获取流程文件中的场景列表接口返回值:{}".format(r.json()))
        assert r.json()['code'] == 200,"获取流程文件中的场景列表接口返回值异常"
        diclist = r.json()['data']
        for i in diclist:
            i['partnerPath'] = [{"name": name, "id": self.PartnerId}, {"name": "", "id": None}]
            i['partnerId'] = self.PartnerId
            i['isCreater'] = 0
            i['actionType'] = '2'
            i['allocateType'] = 0
            i['allocatePartnerPath'] = [{"name": "", "id": None}, {"name": "", "id": None}]
            i['roleId'] = roleId
            i['roleName'] = roleName
            i['partnerName'] = name
            i['selectOkText'] = name
            i['userId'] = ''
            i['allocateRole'] = ''
        # 返回设置流程归属人、任务分配方式、APP/PC后的字典列表
        return diclist

    def addNewProcess(self):
        processkey = get_lastest_bpmn().split("\\")[-1].split('.')[0]
        # 判断当前的processkey在机构中是否存在
        sql = "SELECT processKey,bankId,id FROM ovf_process_info WHERE processKey='%s' AND partnerId=%d" % (
        processkey, self.PartnerId)
        self.log.info("执行sql语句：%s" % sql)
        self.db.excute_otherdb(sql, 'qp_itfin2_data_%d' % self.baseParentId)
        dbData = self.db.get_one()  # ('qizhi-test-document10', 723,53)
        # 查询合作银行名称
        # sql="SELECT id,name FROM pms_department WHERE `name`='%s' AND contactPerson='测试市' ORDER BY id DESC LIMIT 0,1" % processkey
        # 执行下面一句的容错率比较高
        sql = "SELECT pd.id pmsbankid ,opi.processKey,partnerId FROM qp_itfin2_data_%d.ovf_process_info opi LEFT JOIN " \
              "qp_itfin2.pms_department pd on opi.bankId=pd.id WHERE processKey = '%s'" % (
              self.baseParentId, processkey)
        self.log.info("执行sql语句：%s" % sql)
        self.db.excute(sql)
        dbData2 = self.db.get_one()  # (723, 'qizhi-test-document10') #银行信息
        save_url = 'adminApi/ovfConfig/save'
        print(dbData)
        print(dbData2)

        if dbData2[2] != self.PartnerId:
            raise Exception("流程已在该总机构下的其他机构中存在，请修改机构id并注意名称是否符合脚本要求，若不符合请修改流程文件")

        if dbData != None and dbData[0] == processkey and dbData2[0] == dbData[1]:
            print('当前贷款流程已经存在，执行贷款流程更新操作')
            processkey, uuid = self.uploadProcessFile(processId=dbData[2])
            bankid = dbData2[0]
            sava_data = {
                'id': dbData[2],
                'processKey': processkey,
                'uuid': uuid,
                'partnerId': self.PartnerId,  # 组织机构id，默认都选总公司的
                'basePartnerId': self.querybaseparentId(),  # 组织机构id，默认都选总公司的
                'bankId': bankid,  # 银行id，362为杨洪银行2
                'bankPath': '[' + str(bankid) + ']',
                'mainBorrowerAlias': '',
                'copayerAlias': '',
                'guarantorAlias': '',
                'ocrStatus': 7,  # 7为全部开启
                'productType': 74,  # 产品类型ID，74为接口自动化业务
                'taskListJson': json.dumps(self.tasklist_to_diclist(processkey, uuid), ensure_ascii=False)}
            r = None
            self.log.info('传参%s' % sava_data)
            try:
                r = self.base.sendRequest(save_url, 'POST', data=sava_data)
                self.log.info("贷款流程更新接口返回值：{}".format(r.json()))
                print("贷款流程更新接口返回值：{}".format(r.json()))
            except Exception as e:
                print('贷款流程更新失败')
                self.log.info('贷款流程更新失败')
                self.log.error(e, exc_info=True)
                raise
            # 成功则修改bpmn文件名与文件中对应的key
            if r.json()['code'] == 200:
                print("贷款流程更新成功")
                self.log.info("贷款流程更新成功")
                return bankid, processkey
            else:
                print("贷款流程更新失败")
                self.log.info('贷款流程更新失败')
                return None
        else:
            print('当前流程不存在，执行贷款流程新建操作')
            self.log.info('当前流程不存在，执行贷款流程新建操作')
            processkey, uuid = self.uploadProcessFile()
            bankid = self.addbank(processkey)  # 新增经办行，经办行名称以processkey命名
            sava_data = {
                'processKey': processkey,
                'uuid': uuid,
                'partnerId': self.PartnerId,  # 组织机构id，默认都选总公司的
                'basePartnerId': self.querybaseparentId(),  # 组织机构id，默认都选总公司的
                'bankId': bankid,  # 银行id，362为杨洪银行2
                'bankPath': '[' + str(bankid) + ']',
                'mainBorrowerAlias': '',
                'copayerAlias': '',
                'guarantorAlias': '',
                'ocrStatus': 7,  # 7为全部开启
                'productType': 74,  # 产品类型ID，74为接口自动化业务
                'taskListJson': json.dumps(self.tasklist_to_diclist(processkey, uuid), ensure_ascii=False)}
            r = None
            self.log.info('传参%s' % sava_data)
            try:
                r = self.base.sendRequest(save_url, 'POST', data=sava_data)
                self.log.info("贷款流程新建接口返回值：{}".format(r.json()))
                print("贷款流程新建接口返回值：{}".format(r.json()))
            except Exception as e:
                print('贷款流程新建失败')
                self.log.info('贷款流程新建失败')
                self.log.error(e, exc_info=True)
                raise
            if r.json()['code'] == 200:
                print('贷款流程新建成功')
                self.log.info("贷款流程新建成功")
                return bankid, processkey
            else:
                print('贷款流程新建失败')
                self.log.info('贷款流程新建失败')
                return None


if __name__ == '__main__':
    a=Test_addNewLoanProcess(PartnerId=534,baseParentId=532)
    # a = Test_addNewLoanProcess(PartnerId=308, baseParentId=134)
    a.addNewProcess()
    # a.addbank("taizong")