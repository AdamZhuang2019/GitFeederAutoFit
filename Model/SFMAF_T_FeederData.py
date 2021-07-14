class SFMFeederData:
    Id = ""
    FeederSn = ""
    MaxToleranceX = 0
    MinToleranceX = 0
    CpkX = 0
    MaxToleranceY = 0
    MinToleranceY = 0
    CpkY = 0
    Status = 0
    QMNo = ""

    def __init__(self, Id, sn, maxToleranceX, minToleranceX, cpkX, maxToleranceY, minToleranceY, cpKY,status,qmNo):
        self.FeederSn = sn
        self.MaxToleranceX = maxToleranceX
        self.MinToleranceX = minToleranceX
        self.CpkX = cpkX
        self.MaxToleranceY = maxToleranceY
        self.MinToleranceY = minToleranceY
        self.CpkY = cpKY
        self.Id = Id
        self.Status = status
        self.QMNo = qmNo