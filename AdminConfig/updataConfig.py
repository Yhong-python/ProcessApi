#!/usr/bin/env python
# encoding: utf-8
'''
@author: yanghong
@file: updataConfig.py
@time: 2019/6/21 17:48
@desc:
'''
import json

from common.DB import DB_config
from common.Login import login_admin
from common.base2 import Base
from common.logger import Log

log = Log().getlog()


class Test_updataProcessConfig(object):
    def __init__(self, processKey, baseParentId):
        self.log = log
        self.db = DB_config()
        self.processKey = processKey
        self.baseParentId = baseParentId
        self.base = Base()
        login_admin(self.base)

    def getProcessId(self):
        sql = "SELECT id,version FROM ovf_process_info WHERE processKey='%s'" % self.processKey
        dbname = "qp_itfin2_data_" + str(self.baseParentId)
        self.db.excute_otherdb(sql, dbname)
        dbdata = self.db.get_one()
        try:
            processId = dbdata[0]
            processVersion = dbdata[1]
            print("获取流程文件getProcessId:%d,version:%d" % (processId, processVersion))
            self.log.info("获取流程文件getProcessId:%d,version:%d" % (processId, processVersion))
        except Exception as e:
            print("获取getProcessId,version错误")
            self.log.info("获取getProcessId,version错误")
            self.log.error(e, exc_info=True)
            raise
        # print(processId)
        return processId, processVersion

    def getProcessScenesList(self):
        # 查询当前流程文件中所有的场景
        selectProcessSceneApi = 'adminApi/scenesConfigMessage/selectProcessScene'
        processData = self.getProcessId()
        send_data = {
            'processId': processData[0],
            'version': processData[1],
            'basePartnerId': self.baseParentId
        }
        r = self.base.sendRequest(selectProcessSceneApi, 'post', data=send_data)
        assert r.json()['code'] == 200, "请求失败"
        print("当前流程文件中所有场景获取成功")
        self.log.info("当前流程文件中所有场景获取成功")
        # print(r.text)

        # 加载每一个场景的场景配置
        for i in r.json()['processScenesList']:
            self.log.info("当前场景为:%s" % i['taskName'])
            taskName = i['taskName']
            loadConfigApi = 'adminApi/scenesConfig/loadConfig'
            # taskId用i['id']表示
            taskId = i['id']
            send_data = {
                'taskId': taskId,
                'taskType': 1,
                'basePartnerId': self.baseParentId
            }
            r = self.base.sendRequest(loadConfigApi, 'post', send_data)
            assert r.json()['code'] == 200, "请求失败"
            print("%s场景配置加载成功" % i['taskName'])
            self.log.info("%sTab页配置加载成功" % i['taskName'])
            # print(r.text)
            oldSceneConfig = r.json()['sceneConfig']
            # 对每个场景进程配置。关闭Tab页，只保留3个Tab页，客户信息、贷款信息表、订单日志
            tabId = []  # 只需要客户信息、贷款信息表的Tab页id
            for j in oldSceneConfig['tabConfig']['tabInfos']:
                if j['tabName'] == '客户信息':
                    j['isShow'] = 1
                    tabId.append(j['id'])
                elif j['tabName'] == '贷款信息表':
                    j['isShow'] = 1
                    tabId.append(j['id'])
                elif j['tabName'] == '订单日志':
                    j['isShow'] = 1
                else:
                    j['isShow'] = 0
            newSceneConfig = {"sceneConfig": oldSceneConfig}
            # print(newSceneConfig)
            updataTabConfigApi = 'adminApi/scenesConfig/updateConfig'
            send_data = {
                'taskId': taskId,
                'taskType': 1,
                'data': json.dumps(newSceneConfig),
                'basePartnerId': self.baseParentId
            }
            self.log.info('本次请求使用数据%s' % send_data)
            r = self.base.sendRequest(updataTabConfigApi, 'post', send_data)
            self.log.info(r.text)
            assert r.json()['code'] == 200, "请求失败"
            # 将客户信息、贷款信息表里的字段设置为非必填项
            for i in tabId:
                getConfigApi = 'adminApi/scenesFieldConfig/loadConfig'
                send_data = {
                    'taskId': taskId,
                    'tabId': i,
                    'taskType': 1,
                    'requestType': 1,
                    'basePartnerId': self.baseParentId
                }
                # 获取Tab页字段配置，并将所有必填项设置为0
                r = self.base.sendRequest(getConfigApi, 'post', send_data)
                self.log.info('本次请求使用数据%s' % send_data)
                assert r.json()['code'] == 200, "请求失败"
                tabConfig = r.json()['tabConfig']['blockConfigs']
                for j in tabConfig:
                    for m in j['fieldConfigs']:
                        m['isFill'] = 0
                        # 子节点配置
                        if m['child'] != None:
                            for x in m['child']:
                                x['isFill'] = 0
                                j['fieldConfigs'].append(x)
                            m['child'] = None

                # 保存当前Tab页的字段配置
                updataFieldConfigsApi = 'adminApi/scenesFieldConfig/updateConfig'
                tabConfig = {
                    "blockConfigs": tabConfig,
                    'taskId': taskId,
                    'tabId': i
                }

                send_data = {
                    'basePartnerId': self.baseParentId,
                    'data': json.dumps(tabConfig)
                }
                # self.log.info('本次请求使用数据%s' % send_data)
                r = self.base.sendRequest(updataFieldConfigsApi, 'post', send_data)
                assert r.json()['code'] == 200, "请求失败"
                # return r
            print("场景:" + taskName + '字段配置成功')
            self.log.info("场景:" + taskName + '字段配置成功')
        print('贷款流程场景配置成功')


if __name__ == "__main__":
    # a=Test_updataProcessConfig(processKey='qizhi-test-document10',baseParentId=532)
    a = Test_updataProcessConfig(processKey='anhuijinfeng-test1', baseParentId=134)
    result = a.getProcessScenesList()
