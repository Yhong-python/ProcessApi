# ProcessApi
流程自动化

1.新增流程或更新流程可以单独执行/AdminConfig/addNewLoanProces.py
  单独执行时，传参PartnerId,baseParentId，需要将流程文件放在bpmn文件夹下
  目前业务类型写死为：接口自动化,可以修改文件中的第72行的typeId，185行的productType，220行的productType来改变业务类型
2.执行流程场景配置可以单独执行/AdminConfig/updataConfig.py
  单独执行时，传参processKey(流程文件名称),baseParentId
3.完整执行新增或修改流程文件，场景配置，前台添加合作银行可以执行/AdminConfig/webAddBank.py
  类实例化时的传参为PartnerId,baseParentId，执行run函数传参为目标机构账号user,pwd
  目前业务类型也已写死为：接口自动化，可以修改文件中的第41行name（业务类型名称）,44行productType（业务类型id）
4.纯接口实现的流程节点自动化可以执行/WwwProcess/wwwprocess.py
  传参user,pwd,processkey,basePartnerId
