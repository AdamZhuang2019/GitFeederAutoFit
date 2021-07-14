import json
import os
class ConfigHelper:

    @staticmethod
    def GetConfig(key, default=""):
        ConfigPath = os.getcwd() + '\\Config.Json'
        print("begin load config file", ConfigPath)
        result = ""
        try:
            with open(ConfigPath, encoding='utf-8') as f:
                cfg = json.load(f)
                if key in cfg:
                    result = cfg[key]
                else:
                    result = default
        except Exception as e:
            print("from config file ",ConfigPath,"load setting option ",key,"error:",e)
            return default
        finally:
            print("from config file get cfg item [{0}] success, value:[{1}]".format(key,result))
            return result
