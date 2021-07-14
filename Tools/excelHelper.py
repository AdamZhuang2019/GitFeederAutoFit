import xlrd
from Model.Comm import FeederData
import xml.etree.ElementTree as ET
from Tools.ConvertHelper import Converter
from Tools.Config import ConfigHelper
class excelHandel:
    excelUrl = ""
    def __init__(self,excelPath):
        self.excelUrl = excelPath
        pass

    def ReadFeedData(self):
        try:
            # data = xlrd.open_workbook(self.excelUrl)
            # 通过索引顺序获取
            # table = data.sheets()[0]
            # 通过索引顺序获取
            # table = data.sheet_by_index(0)
            # 通过名称获取u 以 Unicode 格式 进行编码，一般用在中文字符串前面
            # table = data.sheet_by_name(u'Sheet1')
            # sn = table.cell(1, 2).value
            tree = ET.parse(self.excelUrl)
            root = tree.getroot()
            worksheet = root.getchildren()[3]
            table = worksheet.getchildren()[0]

            # xml 第六行是 sn
            snrow = table.getchildren()[5]
            sn = snrow.getchildren()[1].getchildren()[0].text

            maxrow = table.getchildren()[21]
            maxx = Converter.StrToInt(maxrow.getchildren()[1].getchildren()[0].text)
            maxy = Converter.StrToInt(maxrow.getchildren()[2].getchildren()[0].text)

            minrow = table.getchildren()[22]
            minx = Converter.StrToInt(minrow.getchildren()[1].getchildren()[0].text)
            miny = Converter.StrToInt(minrow.getchildren()[2].getchildren()[0].text)

            cpkrow = table.getchildren()[26]
            cpkx = self.FormatElementValue(cpkrow.getchildren()[1].getchildren()[0].text)
            cpky = self.FormatElementValue(cpkrow.getchildren()[2].getchildren()[0].text)

            trigger = ConfigHelper.GetConfig("trigger", "1")
            trouble = ConfigHelper.GetConfig("trouble", "1")
            cause = ConfigHelper.GetConfig("cause", "1")
            action = ConfigHelper.GetConfig("action", "1")
            detail = ConfigHelper.GetConfig("detail", "1")
            item = FeederData(sn, trigger, trouble, cause, action, detail, maxx, minx, cpkx, maxy, miny, cpky)
            return item

        # as 代表实例的意思，即 e 是Exception 类的一个实例，你可以通过e访问其具体的属性和方法
        except Exception as e:
            print('from dir ', self.excelUrl, 'load feeder source data error', repr(e))
            return None
        else:
            print("success")


    def FormatElementValue(self,value):
        if value is None:
            return ""

        return value



