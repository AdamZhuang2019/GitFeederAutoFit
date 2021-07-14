from Tools.SysLog import LogHelper
class Converter:
    @staticmethod
    def StrToInt(s):
        try:
            value = Converter.StrToFloat(s)
            return int(value)
        except Exception as e:
            LogHelper.LogError("convert :[{0}] to int error e:[{1}]".format(s,e))
            return 0

    def StrToFloat(s):
        try:
            return float(s)
        except Exception as e:
            LogHelper.LogError("convert :[{0}] to float error e:[{1}]".format(s,e))
            return 0.0