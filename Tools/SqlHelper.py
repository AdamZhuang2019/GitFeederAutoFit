import pymssql
import json
import os
from Model.Comm import BusResult
class SqlHelper:
    sqlser = ""
    sqluser = ""
    sqlpassword = ""
    sqldbname = ""
    connectsql = None

    def __init__(self):
        ConfigPath = os.getcwd() + '\\Config.Json'
        print("begin load config file:", ConfigPath)
        with open(ConfigPath, encoding='utf-8') as f:
            cfg = json.load(f)
            self.sqlser = cfg['sqlser']
            self.sqluser = cfg['sqluser']
            self.sqlpassword = cfg['sqlpassword']
            self.sqldbname = cfg['sqldbname']

    def connOpen(self):
        try:
            connect = pymssql.connect(host=self.sqlser, user=self.sqluser, password=self.sqlpassword, database=self.sqldbname, charset='utf8')
            if connect:
                print('db connect success！')
                self.connectsql= connect
            else:
                print('db connect fail！')
        except Exception as e:
            print('db connect error e:%s' % e)
        else: # 没有异常
            pass

    def executeSqlNoQuery(self,sqlstr,*args):

        print("begin execute sql:[%s]" % sqlstr)
        # 打开数据库连接
        self.connOpen()

        if self.connectsql is None:
            print('sql db is not connect ')
            return BusResult.Creat(-1,'sql db connect is not exists ')
        try:
            cursor = self.connectsql.cursor()
            cursor.execute(sqlstr, args)
            self.connectsql.commit()  # 提交 因为对于影响数据库记录的操作，系统默然是启动事物的，启动事物的话就必须要使用到提交命令
            if cursor.rowcount <1:
                return BusResult.Fail()
        except Exception as e:
            print("execute sql:[%s] error ex:[%s]" % (sqlstr, e))
            self.connectsql.rollback() #异常就要回滚
            return BusResult.Creat(-1, 'operation error')
        else:
            return BusResult.Success()
        finally:
            cursor.close()  # 关闭游标
            self.connectsql.close()  # 关闭连接

    def executeSqlQuery(self,sqlstr,*args):

        print("begin execute sql:[%s]" % sqlstr)
        # 打开数据库连接
        self.connOpen()

        if self.connectsql is None:
            print('sql db is not connect ')
            return BusResult.Creat(-1, 'sql db connect is not exists ')
        try:
            cursor = self.connectsql.cursor()
            cursor.execute(sqlstr, args)
            result = cursor.fetchall()
            self.connectsql.commit()  # 提交
            if cursor.rowcount < 1:
                return BusResult.Fail()
            else:
                return BusResult.Success(result)
        except Exception as e:
            print("execute sql:[%s] error ex:[%s]" % (sqlstr, e))
            return BusResult.Creat(-1, 'operation error')
        finally:
            cursor.close()  # 关闭游标
            self.connectsql.close()  # 关闭连接

    def executeProc(self,proc,parameters):

        print("begin execute proc:[%s]" % proc)
        # 打开数据库连接
        self.connOpen()

        if self.connectsql is None:
            print('sql db is not connect ')
            return BusResult.Creat(-1, 'sql db connect is not exists ')
        try:
            cursor = self.connectsql.cursor()
            cursor.callproc(proc, parameters)
            self.connectsql.commit()  # 提交
        except Exception as e:
            print("proc:[%s] error ex:[s%]" % (proc, e))
            return BusResult.Creat(-1, 'operation error')
        else:
            return BusResult.Success()
        finally:
            cursor.close()  # 关闭游标
            self.connectsql.close()  # 关闭连接





