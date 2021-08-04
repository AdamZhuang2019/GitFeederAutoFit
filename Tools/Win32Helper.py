import win32com.client

import psutil
from Tools.SysLog import LogHelper
import os
class Win32ComHelper:

    @staticmethod
    def check_exsit(processname):
        try:
            pl = psutil.pids()
            for pid in pl:
                if psutil.pid_exists(pid) is False:
                    continue

                print(psutil.Process(pid).name())
                if psutil.Process(pid).name() == processname:
                    print(pid)
                    return True
            else:
                print("process:[{0}] not found".format(processname))
                return False

        except Exception as e:
            LogHelper.LogError("判断进程是否存在异常 ex:[{0}]".format(e.__str__()))
            return False

    @staticmethod
    def killProcess(processName):
        try:
            print("begin kill process %s" % processName)
            isexists = Win32ComHelper.check_exsit(processName)
            if isexists is False:
                print(" process :[{0}] not exists".format(processName))
                return

            os.system('taskkill /f /im %s' % processName)
        except Exception as e:
            LogHelper.LogError("杀掉进程:[{0}]异常 ex:[{1}]".format(processName,e.__str__()))

