# !/usr/bin/env python
# encoding: utf-8
'''
@author: yanghong
@file: wwwprocess.py
@time: 2020/4/22 15:33
@desc:
'''
import json
import time
import warnings

from common.DB import DB_config
from common.Login_Qian import login
from common.base2 import Base

warnings.simplefilter("ignore", ResourceWarning)
base = Base()
db = DB_config()


def test_getAreaByProceId(base, processKey, basePartnerId):
    """获取业务发生地"""
    apiUrl = 'wwwApi/ordOrderTask/getAreaByProceId'
    sql = "SELECT bankId,id FROM ovf_process_info WHERE processKey='%s'" % processKey
    db.excute_otherdb(sql, "qp_itfin2_data_" + str(basePartnerId))
    sqldata = db.get_one()
    bankId, processId = sqldata[0], sqldata[1]
    sendData = {
        'bankId': bankId,
        'processId': processId,
    }
    try:
        r = base.sendRequest(apiUrl, 'post', data=sendData)
    except Exception as e:
        raise
    try:
        if r.json()['code'] == 200:
            return r.json()
        else:
            return None
    except Exception as e:
        raise


def test_addOrder(base, processKey, basePartnerId):
    """ 新建订单,返回orderId"""
    sql = "SELECT id,productType,bankId,version FROM ovf_process_info WHERE processKey='%s'" % processKey
    db.excute_otherdb(sql, "qp_itfin2_data_" + str(basePartnerId))
    sqldata = db.get_one()
    processId, productType, bankId, processVersion = sqldata[0], sqldata[1], sqldata[2], sqldata[3]
    areaName, areaCode = None, None
    try:
        data = json.loads(test_getAreaByProceId(base, processKey, basePartnerId)['list'])[0]
        areaName, areaCode = data['name'], data['code']
    except Exception as e:
        raise
    apiUrl = 'wwwApi/ordOrderTask/add'
    sendData = {
        'productType': int(productType),
        'bankId': int(bankId),
        'processId': int(processId),
        'processVersion': int(processVersion),
        'productFrom': 1,  # 默认取直客
        'areaCode': areaCode,
        'areaName': areaName,
        'spId': '',
        'spName': '',
        'level': '',
        'address': '',
        'shroffAccountNumber': '',
        'shroffAccountName': '',
        'shroffAccountOpBank': ''
    }
    try:
        r = base.sendRequest(apiUrl, 'post', data=sendData)
    except Exception as e:
        raise
    try:
        if r.json()['code'] == 200:
            return r.json()['resultData']['orderId']
            # print('验证通过')
    except Exception as e:
        raise


def test_getOrderPage(base):
    """查询当前用户订单任务"""
    apiUrl = 'wwwApi/ordOrderTask/page'
    sendData = {
        'currentPage': 1,
        'pageSize': 20,
        'sortField': '',
        'orderType': '',
        'bankId': '',
        'likeVal': ''
    }
    try:
        r = base.sendRequest(apiUrl, 'post', data=sendData)
    except Exception as e:
        raise
    try:
        if r.json()['code'] == 200:
            # print('验证通过')
            return r.json()
        else:
            return None
    except Exception as e:
        raise


def test_completeOrder(base, orderid, taskRuntimeId, processTaskId):
    '''执行流程任务提交'''
    apiUrl = 'wwwApi/ordOrderTask/completeOrder'
    sendData = {
        'remark': '通过',
        'orderId': int(orderid),
        'taskRuntimeId': str(taskRuntimeId),
        'processTaskId': int(processTaskId),
        'assignee': ''  # 注意流程中不要指定人
    }
    try:
        r = base.sendRequest(apiUrl, 'post', data=sendData)
    except Exception as e:
        raise
    try:
        if r.json()['code'] == 200:
            return r.json()
    except Exception as e:
        raise


def test_getOrderStatus(base, orderid):
    """查询当前订单状态"""
    apiUrl = 'wwwApi/ordOrderClient/page'
    sendData = {
        'sort': '',
        'order': '',
        'bankId': '',
        'orderStatus': '',
        'createrId': '',
        'partnerId': '',
        'depId': '',
        'currentTask': '',
        'likeVal': '',
        'currentPage': 1,
        'pageSize': 20
    }
    try:
        r = base.sendRequest(apiUrl, 'post', data=sendData)
    except Exception as e:
        raise
    try:
        if r.json()['code'] == 200:
            orderstatusList = r.json()
            for status in orderstatusList['page']['list']:
                if orderid == status['orderId']:
                    return status['orderStatus']
    except Exception as e:
        raise


def test_getTaskDetail(base, orderid):
    """获取任务详情"""
    apiUrl = 'wwwApi/mmbMemberCreditworthiness/taskDetail'
    taskRuntimeId, processTaskId = None, None
    try:
        data = test_getOrderPage(base)['page']['list']
        for i in data:
            if i['orderId'] == orderid:
                taskRuntimeId = i['taskRuntimeId']
                processTaskId = i['processTaskId']
                break
    except Exception as e:
        raise
    sendData = {
        'orderId': orderid,
        'processTaskId': int(processTaskId)
    }
    try:
        r = base.sendRequest(apiUrl, 'post', data=sendData)
    except Exception as e:
        raise
    try:
        if r.json()['code'] == 200:
            # print('验证通过')
            return r.json(), taskRuntimeId
    except Exception as e:
        raise


def test_backOrder(base, orderid, taskRuntimeId, targetTask):
    """退回订单任务,当前订单需要处理可退回节点"""
    apiUrl = 'wwwApi/ordOrderTask/backOrder'
    sendData = {
        'orderId': orderid,
        'remark': '退回',
        'taskRuntimeId': taskRuntimeId,
        'targetTask': targetTask
    }
    try:
        r = base.sendRequest(apiUrl, 'post', data=sendData)
    except Exception as e:
        raise


def test_selectApproval(base, orderId):
    """查询订单流转记录"""
    apiUrl = 'wwwApi/changeLog/selectApproval'
    sendData = {
        "orderId": orderId
    }
    try:
        r = base.sendRequest(apiUrl, 'post', data=sendData)
    except Exception as e:
        raise
    try:
        if r.json()['code'] == 200:
            return r.json()
        else:
            print('返回code校验失败,返回结果: %s ' % r.json())
    except Exception as e:
        raise


def completeOrder(user, pwd, processkey, basePartnerId):
    login(base, user=user, pwd=pwd)
    orderid = test_addOrder(base, processkey, basePartnerId)
    print('订单新建成功：', orderid)
    # orderid = '15888201074186527'
    l = []
    logreturn = []
    orderstatus = test_getOrderStatus(base, orderid)
    while orderstatus == 0:
        r = test_getOrderPage(base)
        for i in r['page']['list']:
            if orderid == i['orderId']:
                l.append(
                    {'taskKey': i['taskKey'], 'taskRuntimeId': i['taskRuntimeId'],
                     'processTaskId': i['processTaskId']})  # 当前任务的信息
                print("当前订单所在场景为：%s" % i['taskName'])
                # 查询当前场景是否存在可退回节点
                backList = []
                for backTaskkey in test_getTaskDetail(base, orderid)[0]['taskDetail']['backList']:
                    backList.append(backTaskkey['taskKey'])  # 可退回节点的taskkey
                # 查询当前可退回节点有没有被退回过
                logList = test_selectApproval(base, orderid)['approvalList']  # 订单日志列表
                for logreturnList in logList:
                    if logreturnList['result'] == 2:
                        logreturn.append(logreturnList['returnTaskKey'])
                # print(logreturn)
                sameList = [x for x in backList if x in set(logreturn)]
                # print(sameList)
                print('当前场景%s的可退回节点为%s' % (i['taskName'], backList))
                # 查询当前场景在订单日志中的所有已退回日志
                alreadyReturnList = []
                for j in logList:
                    if j['step'] == i['taskName'] and j['result'] == 2:
                        alreadyReturnList.append(j['returnTaskKey'])

                if backList != [] or backList != sameList:  # 可退回节点为空或者节点都已经退回过，执行流程提交
                    for back in backList:
                        if back not in alreadyReturnList:
                            # print('%s执行退回' % back)
                            print('当前场景%s执行退回，退回任务至%s' % (i['taskName'], back))
                            test_backOrder(base, orderid, i['taskRuntimeId'], back)
                            break
                        else:
                            print('%s已执行过退回' % back)
                            continue
                    else:  # 循环正常结束，说明当前可退回节点都已经执行过退回，可以执行流程流转了
                        test_completeOrder(base, orderid, i['taskRuntimeId'], i['processTaskId'])
                        print("当前场景流程流转成功")
                else:  # 执行流程流转
                    test_completeOrder(base, orderid, i['taskRuntimeId'], i['processTaskId'])
                    print("当前场景流程流转成功")
                    time.sleep(3)
            break
        orderstatus = test_getOrderStatus(base, orderid)
        # print('执行流转成功的订单状态是', orderstatus)
        # break


if __name__ == "__main__":
    completeOrder(user='16333333333',pwd='333333',processkey='taizong-eshare2',basePartnerId=532)
    # completeOrder(user='18300000030',pwd='000030',processkey='taizong-car',basePartnerId=134)
    # completeOrder(user='18300000010',pwd='000010',processkey='anhuijinfeng-test1',basePartnerId=134)
