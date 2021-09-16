class FeederData:
    FeederSn = ""
    Trigger = 1
    Trouble = 1
    Cause = 1
    Action = 1
    Detail = 1
    MaxToleranceX = 0
    MinToleranceX = 0
    CpkX = 0
    MaxToleranceY = 0
    MinToleranceY = 0
    CpkY = 0

    def __init__(self, sn, trigger, trouble, cause, action, detail, maxToleranceX, minToleranceX, cpkX, maxToleranceY, minToleranceY, cpKY):
        self.FeederSn = sn
        self.Trigger = trigger
        self.Trouble = trouble
        self.Cause = cause
        self.Action = action
        self.Detail = detail
        self.MaxToleranceX = maxToleranceX
        self.MinToleranceX = minToleranceX
        self.CpkX = cpkX
        self.MaxToleranceY = maxToleranceY
        self.MinToleranceY = minToleranceY
        self.CpkY = cpKY

class BusResult:

    Code = -1
    Msg = ''
    Data = None

    def __init__(self,code, msg,data):
        self.Code = code
        self.Msg = msg
        self.Data = data

    @staticmethod
    def Success(data=None):
        item = BusResult.Creat(0,"Success",data)
        return item

    @staticmethod
    def Fail():
        item = BusResult.Creat(-1, "Fail", None)
        return item

    @staticmethod
    def Creat(code, msg,data=None):
        result = BusResult(code,msg,data)
        return result

class FindElementResult:
    Result = False
    Data = None

    def __init__(self, result, data):
        self.Result = result
        self.Data = data

    @staticmethod
    def Success(data=None):
        item = FindElementResult.Creat(True, data)
        return item

    @staticmethod
    def Fail():
        item = FindElementResult.Creat(False, None)
        return item

    @staticmethod
    def Creat(result, data=None):
        result = FindElementResult(result, data)
        return result