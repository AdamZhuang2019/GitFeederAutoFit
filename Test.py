from datetime import datetime,date
from past.builtins import raw_input
from Tools.SysLog import LogHelper
from Tools.RepeatingTimer import RepeatingTimer
from Tools.Config import ConfigHelper
import sys
i = 0
def Hello():
    # type = sys.getfilesystemencoding()
    now = datetime.now()
    # de = date.today()
    str= u"Adam:庄娘胜"
    print(str,now.__str__(),)


if __name__ == '__main__':
    #timer = RepeatingTimer(10, Hello)  # 1代表1秒后执行
    #timer.start()  # 启动定时器

    cfg = ConfigHelper.GetConfig("feederDir")
    print(cfg)
    # xixi = BusResult.Fail()
    # print(xixi.Msg)

    # sqlser = SqlHelper()
    # sql = "select Id,Name,Age from  [dbo].[Student] "
    # result = sqlser.executeSqlQuery(sql)

    # item = SFMFeederData(uuid.uuid4().__str__(),'sn003', 100.00, 50.00, 1.2, 80.00, 50.00, 1.3, 0)
    # fdal = FeederDataDal()
    # result = fdal.Insert(item)
    # result = fdal.QueryById("ff435dbf-3e59-463c-bebd-3dde48c4af5c")
    # if result.Code ==0:
    #    it = result.Data
    #    it.Status =1
    #    re = fdal.update(it)


    # print(result.Code,result.Msg)

    # LogHelper.LogInfo("haha")
    # LogHelper.LogError("E:\我的项目\Feeder自动录入工具\相关文档\KT12B002132_20210705160203.xml")
    #Hello()
    raw_input('按Enter键退出')

