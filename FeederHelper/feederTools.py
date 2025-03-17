import json
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep

from Model.Comm import FindElementResult
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
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable - logging"])
        driver = webdriver.Chrome(options=options)
        weburl = ConfigHelper.GetConfig("webUrl")
        driver.get(weburl)
        driver.maximize_window()
        # driver.find_element_by_link_text("接口测试课程").click()
        # driver.implicitly_wait(10)  # 隐式等待

        timer = RepeatingTimer(30, self.beginFit, (driver,))  # 1代表1秒后执行
        timer.start()  # 启动定时器

        #测试时使用此方法直接调用
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
                    if inserResult.Code != 0: # 这里是测试 需要改回 0
                        if inserResult.Code == -2:
                            print(" feeder data  which load from xml file[{0}],feeder sn:[{1}] was already put into  sfm system ".format(feederdatapath,feederdata.FeederSn))
                            successCount = successCount + 1
                            item.Id=inserResult.Data.Id
                            # 删除文件
                            try:
                                os.remove(feederdatapath)
                            except Exception as e:
                                print(e.__str__())
                            pass
                        else:
                            print(' put feederdata  which load from xml file[{0}] into db fail ,error msg ：[{1}]'.format(feederdatapath,inserResult.Msg))
                            LogHelper.LogError("put the data which load from file [{0}] into db fail ,sn:{1},msg:[{2}]".format(feederdatapath, feederdata.FeederSn,inserResult.Msg))
                        continue

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
        # 尝试判断界面是否隐藏了，如果隐藏了则打开
        opentopmenu= self.find_element_by_css_selector(driver, "#main-content>.open-top-menu")
        if opentopmenu.Result is True:
            classstr=opentopmenu.Data.get_attribute("class")
            if 'ng-hide' in classstr:
                print(u'当前操作界面是展开的')
            else:
                print(u'当前操作界面是影藏的，需要展开')
                opentopmenu.Data.click()
        sleep(1)
        print(u'01-begin entered feeder data,closedNewEntry first!')
        self.closedNewEntry(driver)
        print(u'02-begin entered feeder data,closedNewEntry end!')
        sleep(3)
        result = self.find_element_by_css_selector_Click(driver, "button.btn")
        if result is not True:
            print("03-can not click green button to show menu list ！")
            return False
        sleep(1)
        result = self.find_element_by_link_text_Click(driver, "Preventative Maintenance - New Entry")
        if result is not True:
            print(" 04-can not click Preventative Maintenance - New Entry button！")
            return False

        print(" 05-begin input feeder sn ！")

        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.ID,"feeder").send_keys(feederdata.FeederSn)
                sleep(1)
                driver.find_element(By.ID,"feeder").send_keys(Keys.ENTER)
                sleep(1)
            except:
                print("can not find input [feeder] to put in feeder sn！ try the {0} times later".format(trytime+1))
                sleep(1)
                if trytime >10:
                    LogHelper.LogError("没有找到feeder sn 录入框,并且重试了10次！")
                    print(" 05-01- input feeder sn fail ！")
                    self.closedNewEntry(driver)
                    return False

                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0
        # 判断SN 是否合法，因为点击enter 键后系统会判断 SN 是否合法
        sleep(1)
        self.closeTip(driver)

        print(" 06-get feeder sn ！")
        newsn = driver.find_element(By.ID,"feeder").get_property("value")
        if newsn == '':
            print("SN:", feederdata.FeederSn, 'illegal')
            # 需要找到关闭按钮 点击关闭
            self.closedNewEntry(driver)
            return False

        print(" 07-begin find trigger select ！")

        findSuccess = False
        trytime = 0
        triSel = None
        while (findSuccess is False):
            try:
                triSel = driver.find_element(By.ID,"trigger")
            except:
                print("没有找到[trigger]下拉框！ try the {0} times later".format(trytime+1))
                sleep(1)
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                    print(" 07-01- find  trigger select fail ！")
                    self.closedNewEntry(driver)
                    return False
                trytime=trytime+1
            else:
                findSuccess = True
                trytime = 0

        print(" 08-begin check trigger select is enable！")

        canTri = triSel.get_property("disabled")
        if canTri is True:
            print("08-01-SN:", feederdata.FeederSn, 'illegal')
            # 需要找到关闭按钮 点击关闭
            self.closedNewEntry(driver)
            return False

        print(" 09-begin click trigger to show all options！")

        trivalue = driver.find_element(By.CSS_SELECTOR,"#trigger>a>span>span.ng-scope").text
        if trivalue == "":
            triSel.click()

            print(" 09-01-begin select trigger option")
            findSuccess = False
            trytime = 0
            while (findSuccess is False):
                try:
                    driver.find_element(By.CSS_SELECTOR,
                        "#trigger>div>ul>li>ul li:nth-child(" + feederdata.Trigger + ")").click()
                except:
                    sleep(1)
                    print("can not find select option of [trigger]! try the {0} times later".format(trytime+1))
                    if trytime > 10:
                        # 需要找到关闭按钮 点击关闭
                        print(" 09-02- select trigger option fail ")
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
        print(" 10-begin find trouble select")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.ID,"trouble").click()
            except:
                sleep(1)
                print("can not find select [trouble] try the {0} times later".format(trytime+1))
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        print("10-01-select select option of [trouble]  ")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.CSS_SELECTOR,
                    "#trouble>div>ul>li>ul li:nth-child(" + feederdata.Trouble + ")").click()
            except:
                sleep(1)
                print("can not find any option of select: [trouble]! try the {0} times later".format(trytime+1))
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        print(" 11-begin find cause select")

        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.ID,"cause").click()
            except:
                sleep(1)
                print("can not find select [cause]! try the {0} times later".format(trytime+1))
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        print("11-01-select cause option ")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.CSS_SELECTOR,
                    "#cause>div>ul>li>ul li:nth-child(" + feederdata.Cause + ")").click()
            except:
                sleep(1)
                print("can not find any option of select [cause]! try the {0} times later".format(trytime+1))
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        print(" 12-begin add trouble/cause")

        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.CSS_SELECTOR,'button[uib-tooltip="Add Trouble/Cause"]').click()
            except:
                sleep(1)
                print("can not find button[Add Trouble/Cause] try the {0} times later".format(trytime+1))
                if trytime >5:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        # 填写 Action/Solution *  注意孩子节点是从1开始计数
        print(" 13-begin find action select ")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.ID,"action").click()
            except:
                sleep(1)
                print("can not find select [action]!")
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        print("13-01-select action option")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.CSS_SELECTOR,
                    "#action>div>ul>li>ul li:nth-child(" + feederdata.Action + ")").click()
            except:
                sleep(1)
                print("can not find any option of [action] select ! try the {0} times later".format(trytime+1))
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        print(" 14-begin find detail select ")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.ID, "detail").click()
            except:
                sleep(1)
                print("can not find select [detail]! try the {0} times later".format(trytime+1))
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        print("14-01-select detail option")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.CSS_SELECTOR,
                    "#detail>div>ul>li>ul li:nth-child(" + feederdata.Detail + ")").click()
            except:
                sleep(1)
                print("can not find any option of [detail] select!  try the {0} times later".format(trytime+1))
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        print(" 15-begin add Action/Detail")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                # driver.find_element_by_css_selector('button[uib-tooltip="Add Action/Detail"]').click()
                driver.find_element(By.CSS_SELECTOR, 'button[uib-tooltip="Add Action/Detail"]').click()
            except:
                sleep(1)
                print("can not find button[Add Action/Detail]! try the {0} times later".format(trytime+1))
                if trytime >5:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0

        # 填写optional entries
        print(" 16- fill max-x-tolerance")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.ID,"max-x-tolerance").send_keys(feederdata.MaxToleranceX)
            except:
                sleep(1)
                print("can not set input [max-x-tolerance] value !  try the {0} times later".format(trytime+1))
                if trytime > 10:
                    findSuccess = True
                    trytime = 0
                trytime = trytime + 1
                pass
            else:
                findSuccess = True
                trytime = 0

        print(" 17- fill min-x-tolerance")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.ID,"min-x-tolerance").send_keys(feederdata.MinToleranceX)
            except:
                sleep(1)
                print("can not set input [min-x-tolerance] value ! try the {0} times later".format(trytime+1))
                if trytime > 10:
                    findSuccess = True
                    trytime = 0
                trytime = trytime + 1
                pass
            else:
                findSuccess = True
                trytime = 0

        print(" 18- fill cpk-x-tolerance")

        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.ID,"cpk-x-tolerance").send_keys(feederdata.CpkX)
            except:
                print("can not set input [cpk-x-tolerance] value ! try the {0} times later".format(trytime+1))
                sleep(1)
                if trytime > 10:
                    findSuccess = True
                    trytime = 0
                trytime = trytime + 1
                pass
            else:
                findSuccess = True
                trytime = 0

        print(" 19- fill max-y-tolerance")

        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.ID,"max-y-tolerance").send_keys(feederdata.MaxToleranceY)
            except:
                print("can not set input [max-y-tolerance] value ! try the {0} times later".format(trytime+1))
                sleep(1)
                if trytime > 10:
                    findSuccess = True
                    trytime = 0
                trytime = trytime + 1
                pass
            else:
                findSuccess = True
                trytime = 0

        print(" 20- fill min-y-tolerance")

        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.ID, "min-y-tolerance").send_keys(feederdata.MinToleranceY)
            except:
                print("can not set input [min-y-tolerance] value ! try the {0} times later".format(trytime+1))
                sleep(1)
                if trytime > 10:
                    findSuccess = True
                    trytime = 0
                trytime = trytime + 1
                pass
            else:
                findSuccess = True
                trytime = 0

        print(" 21- fill cpk-y-tolerance")

        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.ID,"cpk-y-tolerance").send_keys(feederdata.CpkY)
            except:
                print("can not set input [cpk-y-tolerance] value ! try the {0} times later".format(trytime+1))
                sleep(1)
                if trytime > 10:
                    findSuccess = True
                    trytime = 0
                trytime = trytime + 1
                pass
            else:
                findSuccess = True
                trytime = 0

        print(" 22- begin NewEntry save ")
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                driver.find_element(By.CSS_SELECTOR,"button.btn-green")
            except:
                print("can not find button[Save]! try the {0} times later".format(trytime+1))
                sleep(1)
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
                pass
            else:
                findSuccess = True
                trytime = 0
        # 获取保存按钮
        # result = self.find_element_by_css_selector(driver, "button.btn-green")
        result = self.find_element_by_css_selector(driver, "button.btn-green")
        if result.Result is False:
            print("can not find button[Save]!")
            self.closedNewEntry(driver)
            return False

        save = result.Data

        cansave = save.get_property("disabled")
        if cansave is True:
            print("SN:", feederdata.FeederSn, 'can not save in to sfm system ！')
            LogHelper.Log("sn:[{0}] 无法保存到smf系统，Save 按钮不可用，可能是即将录入的数据有问题","Info")
            sleep(2)
            # 需要找到关闭按钮 点击关闭
            self.closedNewEntry(driver)
            return False

        print("23-real save into sfm system ")

        save.click()
        sleep(1)
        self.closedNewEntry(driver)
        print("24- end NewEntry save ")
        return True

    # 关闭新建窗口函数
    def closedNewEntry(self, driver):
        self.closeTip(driver)
        # 需要找到关闭按钮 点击关闭
        findSuccess = False
        trytime =0
        while (findSuccess is False):
            try:
                driver.find_element(By.CSS_SELECTOR, ".modal-footer>.btn-default").click()
            except:
                print("can not find button[Close] to begin close  New Entry Dialog,try again!")
                if trytime >10:
                    findSuccess= True
                    trytime = 0
                trytime=trytime+1
            else:
                findSuccess = True
                trytime = 0
                print("finish click  button[Close] to begin close New Entry Dialog!")
                LogHelper.Log("finish click  button[Close] to begin close New Entry Dialog!", "Info")

        # 需要关闭弹出框
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                # confirmBut=driver.find_element_by_css_selector("#cboxLoadedContent .btn-primary")
                confirmBut=driver.find_element(By.CSS_SELECTOR, "#cboxLoadedContent .btn-primary")
                sleep(2)
                confirmBut.click()
                # 需要关闭弹出框
            except:
                print("can not find ok button in confirm form,to  real close New Entry Dialog,try again !")
                if trytime > 10:
                    findSuccess = True
                    trytime = 0
                trytime = trytime + 1

            else:
                findSuccess = True
                trytime = 0
                print("finish click  ok button in confirm form,to  real close New Entry Dialog!")
                LogHelper.Log("finish click  ok button in confirm form,to  real close New Entry Dialog!", "Info")

    #关闭信息提示框 并取到错误信息 打印出来
    def closeTip(self,driver):
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
            try:
                # tip = driver.find_element_by_css_selector("#toast-container .toast-message").text
                tip = driver.find_element(By.CSS_SELECTOR, "#toast-container .toast-message").text
                LogHelper.Log(tip, "Info")
                print(tip)
                driver.find_element(By.CSS_SELECTOR, "#toast-container .toast-close-button").click()
            except:
                print("close tip form fail, try again!")
                if trytime > 10:
                    findSuccess = True
                    trytime = 0
                trytime = trytime + 1
            else:
                findSuccess = True
                trytime = 0
                LogHelper.Log("finish close tip form !", "Info")
                print("finish close tip form !")
    #使用ID查找元素
    def find_element_by_id(self,driver,elementId):
        findSuccess = False
        trytime = 0

        while (findSuccess is False):
            try:
                obj = driver.find_element(By.ID, elementId)
                return FindElementResult.Success(obj)
            except:
                print("can not find element [{0}] by id ! try the {1} times later".format(elementId, trytime + 1))
                sleep(1)
                if trytime > 10:
                    return FindElementResult.Fail()
                trytime = trytime + 1
                pass

    # 使用CSS查找元素
    def find_element_by_css_selector(self, driver, cssSelector):
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
           try:
                obj = driver.find_element(By.CSS_SELECTOR, cssSelector)
                return FindElementResult.Success(obj)
           except:
                print("can not find element [{0}] by css  ! try the {1} times later".format(cssSelector, trytime + 1))
                sleep(1)
                if trytime > 10:
                    return FindElementResult.Fail()
                trytime = trytime + 1
                pass

    def find_element_by_link_text(self, driver, linkText):
        findSuccess = False
        trytime = 0
        while (findSuccess is False):
           try:
                obj = driver.find_element(By.LINK_TEXT,linkText)
                return FindElementResult.Success(obj)
           except:
                print("can not find element by text [{0}] ! try the {1} times later".format(linkText, trytime + 1))
                sleep(1)
                if trytime > 10:
                    return FindElementResult.Fail()
                trytime = trytime + 1
                pass

    def find_element_by_id_Click(self, driver, elementId):
        findSuccess = False
        trytime = 0

        result = self.find_element_by_id(driver, elementId)
        if result.Result is False:
            return False

        while (findSuccess is False):
            try:
                result.Data.click()
                findSuccess = True
                return True
            except:
                print("element [{0}] click fail ! try the {1} times later".format(elementId, trytime + 1))
                sleep(1)
                if trytime > 10:
                    return False
                trytime = trytime + 1

    def find_element_by_css_selector_Click(self, driver, cssSelector):
        findSuccess = False
        trytime = 0

        result = self.find_element_by_css_selector(driver, cssSelector)
        if result.Result is False:
            return False

        while (findSuccess is False):
            try:
                result.Data.click()
                findSuccess = True
                break
            except:
                print("element [{0}] click fail ! try the {1} times later".format(cssSelector, trytime + 1))
                sleep(1)
                if trytime > 10:
                    break
                trytime = trytime + 1

        return findSuccess

    def find_element_by_link_text_Click(self, driver, linkText):
        findSuccess = False
        trytime = 0

        result = self.find_element_by_link_text(driver, linkText)
        if result.Result is False:
            return False

        while (findSuccess is False):
            try:
                result.Data.click()
                findSuccess = True
                return True
            except:
                print("element [{0}] click fail ! try the {1} times later".format(linkText, trytime + 1))
                sleep(1)
                if trytime > 10:
                    return False
                trytime = trytime + 1