from Model.Comm import BusResult
from Tools.SqlHelper import SqlHelper
from Model.SFMAF_T_FeederData import SFMFeederData
import uuid

class FeederDataDal:

    sqlser = None

    def __init__(self):
        self.sqlser = SqlHelper()

    def Insert(self, item):

        queryresult = self.QueryBySn(item)

        if queryresult.Code ==0:
            itexists = queryresult.Data
            if itexists.Status == 1:
                return BusResult.Creat(-2,"feeder data whit sn:[{0}] was already put into sfm system".format(item.FeederSn),itexists)
            else:
                return BusResult.Success()

        sql = """ if not exists ( select 1 from [dbo].[SFMAF_T_FeederData] where SN= '{1}' 
            and [MaxToleranceX]='{2}' and  [MinToleranceX]='{3}' and [CpkX]='{4}' and [MaxToleranceY]='{5}' and [MinToleranceY]='{6}'
            and [CpkY]='{7}' and [QMNo]='{9}')
        begin
            INSERT INTO [dbo].[SFMAF_T_FeederData]
           ([Id]
           ,[SN]
           ,[MaxToleranceX]
           ,[MinToleranceX]
           ,[CpkX]
           ,[MaxToleranceY]
           ,[MinToleranceY]
           ,[CpkY]
           ,[Status],[QMNo])
           values ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')
        end
           """

        result = self.sqlser.executeSqlNoQuery(sql.format(item.Id, item.FeederSn, item.MaxToleranceX,
                                                   item.MinToleranceX, item.CpkX, item.MaxToleranceY,
                                                   item.MinToleranceY, item.CpkY, item.Status, item.QMNo),
                                                   )
        return result

    def update(self, item):
        sql = """update [dbo].[SFMAF_T_FeederData] set [SN]= '{0}' ,[MaxToleranceX]= '{1}' ,[MinToleranceX]= '{2}' ,
        [CpkX]= '{3}' ,[MaxToleranceY]= '{4}' ,[MinToleranceY]= '{5}' ,[CpkY]= '{6}' ,[Status]= '{7}',[QMNo]='{9}'
         where Id = '{8}' """

        result = self.sqlser.executeSqlNoQuery(sql.format(item.FeederSn, item.MaxToleranceX,
                                                   item.MinToleranceX, item.CpkX, item.MaxToleranceY,
                                                   item.MinToleranceY, item.CpkY, item.Status, item.Id,item.QMNo))
        return result

    def QueryById(self,id):
        sql = """select * from [dbo].[SFMAF_T_FeederData] where Id = %s """
        result = self.sqlser.executeSqlQuery(sql, id)
        if result.Code != 0:
            return result

        item = SFMFeederData(result.Data[0][0],result.Data[0][1],result.Data[0][2],result.Data[0][3],result.Data[0][4],result.Data[0][5],
                             result.Data[0][6],result.Data[0][7],result.Data[0][8],result.Data[0][9])

        return BusResult.Success(item)

    def QueryBySn(self,item):
        sql = """select * from [dbo].[SFMAF_T_FeederData] where SN = '{0}' 
                 and [MaxToleranceX]='{1}' and  [MinToleranceX]='{2}'
                 and [CpkX]='{3}' and [MaxToleranceY]='{4}' and [MinToleranceY]='{5}'
                 and [CpkY]='{6}' and QMNo = '{7}'"""

        result = self.sqlser.executeSqlQuery(sql.format(item.FeederSn, item.MaxToleranceX,
                                                   item.MinToleranceX, item.CpkX, item.MaxToleranceY,
                                                   item.MinToleranceY, item.CpkY,item.QMNo))
        if result.Code != 0:
            return result

        item = SFMFeederData(result.Data[0][0], result.Data[0][1], result.Data[0][2], result.Data[0][3],
                             result.Data[0][4], result.Data[0][5],
                             result.Data[0][6], result.Data[0][7], result.Data[0][8], result.Data[0][9])

        return BusResult.Success(item)
