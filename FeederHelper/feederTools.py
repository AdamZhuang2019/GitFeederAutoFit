import json
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep

from Model.SFMAF_T_FeederData import SFMFeederData
from Tools.excelHelper import excelHandel as haha
from Tools.RepeatingTimer import RepeatingTimer
from datetime import  datetime
from Dal.FeederDataDal import FeederDataDal
from Tools.SysLog import  LogHelper
from Tools.Config import ConfigHelper
import uuid
class FeederFun:
    Fdal = None
    def __init__(self):
        self.Fdal = FeederDataDal()
        pass

    def autofitForm(self):
        # 杀死这个chromedriver进程，因为每次启动都会打开，所以需要kill，这里用的chrome浏览器，打开方式时chromedriver.exe。
        # 需要放在代码同一目录下，不明白的可以搜索
        # os.system("taskkill /f /im chromedriver.exe")
        driver = webdriver.Chrome()
        weburl = ConfigHelper.GetConfig("webUrl")
        driver.get(weburl)
        driver.maximize_window()
        # driver.find_element_by_link_text("接口测试课程").click()
        # driver.implicitly_wait(10)  # 隐式等待

        timer = RepeatingTimer(30, self.beginFit, (driver,))  # 1代表1秒后执行
        timer.start()  # 启动定时器
        # self.beginFit(driver)

    def beginFit(self,driver):
        print("timer begin to run ！")
        totalCount = 0
        successCount = 0

        feederDir = ConfigHelper.GetConfig("feederDir")
        print("begin handle all files ")
        for root, dirs, files in os.walk(feederDir):
            for file in files:
                if os.path.splitext(file)[1] == '.xml':
                    feederdatapath = os.path.join(feederDir, file)
                    print('begin load xml file from dir:feederdata ', feederdatapath, ',get some input from data ')
                    handle = haha(feederdatapath)
                    feederdata = handle.ReadFeedData()
                    if feederdata is None:
                        print('parse xml source data fail ')
                        continue
                        # exit(-1)

                    qmno = ConfigHelper.GetConfig("QMNo")
                    # 插入数据到数据库中
                    item = SFMFeederData(uuid.uuid4().__str__(), feederdata.FeederSn, feederdata.MaxToleranceX,
                                         feederdata.MinToleranceX, feederdata.CpkX,
                                         feederdata.MaxToleranceY, feederdata.MinToleranceY, feederdata.CpkY, 0, qmno)
                    inserResult = self.Fdal.Insert(item)
                    if inserResult.Code != 0:
                        if inserResult.Code == -2:
                            print(" feeder data  which load from xml file[{0}],feeder sn:[{1}] was already put into  sfm system ".format(feederdatapath,feederdata.FeederSn))
                            successCount = successCount + 1
                            # 删除文件
                            try:
                                os.remove(feederdatapath)
                            except Exception as e:
                                print(e.__str__())
                            pass
                        else:
                            print(' put feederdata  which load from xml file[{0}] into db fail ,error msg ：[{1}]'.format(feederdatapath,inserResult.Msg))
                            LogHelper.LogError("put the data which load from file [{0}] into db fail ,sn:{1},msg:[{2}]".format(feederdatapath, feederdata.FeederSn,inserResult.Msg))
                        break

                    totalCount = totalCount + 1

                    result = self.doneFit(driver, feederdata)
                    if result is True:
                        #更新状态为1，说明该数据已经成功录入到了系统
                        item.Status = 1
                        updateResult =self.Fdal.update(item)
                        if updateResult.Code != 0:
                            LogHelper.LogError("update feederdata status fail which had put in sfm system ,sn:[{0}],msg:{1}".format(feederdata.FeederSn, updateResult.Msg))

                        successCount = successCount + 1
                        # 删除文件
                        try:
                            os.remove(feederdatapath)
                        except Exception as e:
                            print(e.__str__())


        print("[%s]:Total data to be automatically entered this time：[%d]，success：[%d]" % (datetime.now(),totalCount, successCount))

    def doneFit(self, driver, feederdata):

        print(u'begin entered feeder data')
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element_by_css_selector("button.btn").click()
            except:
                print("can not find gear button！")
                if trytime >20:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element_by_link_text("Preventative Maintenance - New Entry").click()
            except:
                print("can not find [Preventative Maintenance - New Entry] button！")
                if trytime >20:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        sleep(1)
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element_by_id("feeder").send_keys(feederdata.FeederSn)
                driver.find_element_by_id("feeder").send_keys(Keys.ENTER)
            except:
                print("can not find input [feeder] to put in feeder sn！")
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                    LogHelper.LogError("没有找到feeder sn 录入框")
                    self.closeTip(driver)
                    return False
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0
        # 判断SN 是否合法，因为点击enter 键后系统会判断 SN 是否合法
        sleep(1)
        self.closeTip(driver)


        newsn = driver.find_element_by_id("feeder").get_property("value")
        if newsn == '':
            print("SN:", feederdata.FeederSn, 'illegal')
            # 需要找到关闭按钮 点击关闭
            self.closedNewEntry(driver)
            return False

        findSuccess = False
        trytime = 0
        triSel = None
        while (findSuccess is False):
            try:
                triSel = driver.find_element_by_id("trigger")
            except:
                print("没有找到[trigger]下拉框！")
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                    self.closedNewEntry(driver)
                    return False
                trytime=trytime+1
            else:
                findSuccess = True
                trytime = 0

        canTri = triSel.get_property("disabled")
        if canTri is True:
            print("SN:", feederdata.FeederSn, 'illegal')
            # 需要找到关闭按钮 点击关闭
            self.closedNewEntry(driver)
            return False

        trivalue = driver.find_element_by_css_selector("#trigger>a>span>span.ng-scope").text
        if trivalue == "":
            triSel.click()

            print(" select trigger")
            findSuccess = False
            trytime = 0
            while (findSuccess is False):
                try:
                    driver.find_element_by_css_selector(
                        "#trigger>div>ul>li>ul li:nth-child(" + feederdata.Trigger + ")").click()
                except:
                    print("can not find select option of [trigger]!")
                    if trytime > 10:
                        # 需要找到关闭按钮 点击关闭
                        self.closedNewEntry(driver)
                        findSuccess = True
                    else:
                        trytime = trytime+1
                    pass
                else:
                    findSuccess = True
        # 注意孩子节点是从1开始
        # Select(opt).select_by_index(1)
        # Select(opt).select_by_value('03')
        # 填写 Root Cause * trouble
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element_by_id("trouble").click()
            except:
                print("can not find select [trouble]")
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        print("select select option of [trouble]  ")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element_by_css_selector(
                    "#trouble>div>ul>li>ul li:nth-child(" + feederdata.Trouble + ")").click()
            except:
                print("can not find any option of select: [trouble]!")
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element_by_id("cause").click()
            except:
                print("can not find select [cause]!")
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        print("select cause option ")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element_by_css_selector(
                    "#cause>div>ul>li>ul li:nth-child(" + feederdata.Cause + ")").click()
            except:
                print("can not find any option of select [cause]!")
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element_by_css_selector('button[uib-tooltip="Add Trouble/Cause"]').click()
            except:
                print("can not find button[Add Trouble/Cause]")
                if trytime >5:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        # 填写 Action/Solution *  注意孩子节点是从1开始计数
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element_by_id("action").click()
            except:
                print("can not find select [action]!")
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        print("select action option")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element_by_css_selector(
                    "#action>div>ul>li>ul li:nth-child(" + feederdata.Action + ")").click()
            except:
                print("can not find any option of [action] select !")
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element_by_id("detail").click()
            except:
                print("can not find select [detail]!")
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        print("select detail option")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element_by_css_selector(
                    "#detail>div>ul>li>ul li:nth-child(" + feederdata.Detail + ")").click()
            except:
                print("can not find any option of [detail] select ")
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element_by_css_selector('button[uib-tooltip="Add Action/Detail"]').click()
            except:
                print("can not find button[Add Action/Detail]!")
                if trytime >5:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        # 填写optional entries
        sleep(1)
        driver.find_element_by_id("max-x-tolerance").send_keys(feederdata.MaxToleranceX)
        driver.find_element_by_id("min-x-tolerance").send_keys(feederdata.MinToleranceX)
        driver.find_element_by_id("cpk-x-tolerance").send_keys(feederdata.CpkX)
        driver.find_element_by_id("max-y-tolerance").send_keys(feederdata.MaxToleranceY)
        driver.find_element_by_id("min-y-tolerance").send_keys(feederdata.MinToleranceY)
        driver.find_element_by_id("cpk-y-tolerance").send_keys(feederdata.CpkY)

        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element_by_css_selector("button.btn-green")
            except:
                print("can not find button[Save]!")
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        save = driver.find_element_by_css_selector("button.btn-green")
        cansave = save.get_property("disabled")
        if cansave is True:
            print("SN:", feederdata.FeederSn, 'can not save in to sfm system ！')
            LogHelper.Log("sn:[{0}] 无法保存到smf系统，Save 按钮不可用，可能是即将录入的数据有问题","Info")
            sleep(2)
            # 需要找到关闭按钮 点击关闭
            self.closedNewEntry(driver)
            return False

        print("begin save in sfm system ")

        save.click()
        sleep(3)
        self.closedNewEntry(driver)
        return True

    # 关闭新建窗口函数
    def closedNewEntry(self, driver):
        self.closeTip(driver)
        # 需要找到关闭按钮 点击关闭
        findSuccess = False
        trytime =0
        while (findSuccess is False):
            try:
                driver.find_element_by_css_selector(".modal-footer>.btn-default").click()
            except:
                print("can not find button[Close]!")
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
            else:
                findSuccess = True
                trytime = 0

        # 需要关闭弹出框
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                confirmBut=driver.find_element_by_css_selector("#cboxLoadedContent .btn-primary")
                sleep(2)
                confirmBut.click()
                # 需要关闭弹出框
            except:
                print("can not find ok button in confirm form!")
                if trytime > 10:
                    findSuccess = True
                    trytime = 0
                trytime = trytime + 1

            else:
                findSuccess = True
                trytime = 0

    #关闭信息提示框 并取到错误信息 打印出来
    def closeTip(self,driver):
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                tip = driver.find_element_by_css_selector("#toast-container .toast-message").text
                LogHelper.Log(tip, "Info")
                print(tip)
                driver.find_element_by_css_selector("#toast-container .toast-close-button").click()
            except:
                print("can not find close but on tip form !")
                if trytime > 10:
                    findSuccess = True
                    trytime = 0
                trytime = trytime + 1
            else:
                findSuccess = True
                trytime = 0

