import os
import datetime
from Tools.Config import ConfigHelper
class LogHelper:

    @staticmethod
    def Log(msg, type="Info"):
        logfilepath = os.getcwd() + '\\log.txt'
        try:
            with open(logfilepath, mode='a',encoding="utf-8") as fileWrt:
                logmsg = "[{0}]-{1}:{2}\n".format(datetime.datetime.now().__str__(), type, msg)
                fileWrt.write(logmsg)
        except Exception as e:
            print("write log error ！e:", e)
        else:
            pass

    @staticmethod
    def LogInfo(msg):
        iflog = ConfigHelper.GetConfig("LogInfo", "0")
        if iflog !="1":
            return

        LogHelper.Log(msg,"Info")

    @staticmethod
    def LogWarn(msg):
        iflog = ConfigHelper.GetConfig("LogWarn", "0")
        if iflog != "1":
            return

        LogHelper.Log(msg, "Warn")

    @staticmethod
    def LogError(msg):
        LogHelper.Log(msg, "Error")