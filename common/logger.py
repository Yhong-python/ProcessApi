# coding=utf-8
import logging
import os
import time

# log_path是存放日志的路径
cur_path = os.path.dirname(__file__)
log_path = os.path.join(os.path.dirname(cur_path), 'logs')
# 如果不存在logs文件夹则创建一个
if not os.path.exists(log_path): os.mkdir(log_path)


class Log():
    def __init__(self, logger=None):
        # 文件的命名
        self.logname = os.path.join(log_path, '%s.log' % (time.strftime('%Y%m%d')))  # 全部日志文件名
        self.error_logname = os.path.join(log_path, '%s_error.log' % (time.strftime('%Y%m%d')))  # 错误日志文件名

        self.logger = logging.getLogger(logger)
        self.logger.handlers.clear()
        self.logger.setLevel(level=logging.DEBUG)
        # 日志输出格式
        self.formatter = logging.Formatter(
            fmt='%(asctime)s %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] %(message)s')
        # 创建filehandle，用于写全部日志到文件
        self.filehandle = logging.FileHandler(self.logname, encoding='utf-8')
        self.filehandle.setLevel(level=logging.DEBUG)
        self.filehandle.formatter = self.formatter
        self.logger.addHandler(self.filehandle)

        # 创建filehandle，用于写错误日志到文件
        filehandle_error = logging.FileHandler(self.error_logname, encoding='utf-8')
        filehandle_error.setLevel(level=logging.ERROR)
        filehandle_error.formatter = self.formatter  # 格式与全部日志的相同
        self.logger.addHandler(filehandle_error)
        # 创建一个控制台输出handle
        # self.streamhanlde=logging.StreamHandler()
        # self.streamhanlde.setLevel(level=logging.DEBUG)
        # self.streamhanlde.formatter=self.formatter
        # self.logger.addHandler(self.streamhanlde)

    # 实例化时需要Log().getlog()
    def getlog(self):
        return self.logger
        # def console(self,level,message):
        #     if level == 'info':
        #         self.logger.info(message)
        #     elif level == 'debug':
        #         self.logger.debug(message)
        #     elif level == 'warning':
        #         self.logger.warning(message)
        #     elif level == 'error':
        #         self.logger.error(message,exc_info=True)
        #     # 这两行代码是为了避免日志输出重复问题
        #     self.logger.removeHandler(self.filehandle)
        #     # self.logger.removeHandler(self.streamhanlde)
        # def debug(self,message):
        #     self.console('debug',message)
        # def info(self, message):
        #     self.console('info', message)
        # def warning(self, message):
        #     self.console('warning', message)
        # def error(self,message):
        #     self.console('error',message)


if __name__ == "__main__":
    log = Log().getlog()
    log.info('--测试开始--')
    log.info('操作步骤1,2,3')
    log.warning('----测试结束----')
