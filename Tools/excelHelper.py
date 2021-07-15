import xlrd
from Model.Comm import FeederData
import xml.etree.ElementTree as ET
from Tools.ConvertHelper import Converter
from Tools.Config import ConfigHelper
from Tools.SysLog import LogHelper
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
            # 第四和孩子节点是 worksheet
            worksheet = self.GetElementchildren(root, 3)
            if worksheet is None :
                LogHelper.LogError("xml 文件：[{0}] 格式不正确，第四个孩子节点获取失败".format(self.excelUrl))
                return None

            if worksheet.tag.find("Worksheet")<0:
                LogHelper.LogError("xml 文件：[{0}] 格式不正确，第四个孩子节点不是Worksheet 节点".format(self.excelUrl))
                return None

            table = self.GetElementchildren(worksheet, 0)
            if table is None:
                LogHelper.LogError("xml 文件：[{0}] 格式不正确，Worksheet 第1孩子节点获取失败".format(self.excelUrl))
                return None

            if table.tag.find("Table")< 0:
                LogHelper.LogError("xml 文件：[{0}] 格式不正确，Worksheet 第1孩子节不是table 节点".format(self.excelUrl))
                return None

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

            cpkxCel = self.GetElementchildren(cpkrow, 1)
            cpkx = self.GetElementText(self.GetElementchildren(cpkxCel, 0))

            cpkyCel = self.GetElementchildren(cpkrow, 2)
            cpky = self.GetElementText(self.GetElementchildren(cpkyCel, 0))

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


    def FormatElementValue(self,value):
        if value is None:
            return ""

        return value

    def GetElementText(self,element):
        if element is None:
            return ""

        text = element.text
        if text is None:
            return ""

        return text

    def GetElementchildren(self,element,index):
        if element is None:
            return None

        childs = element.getchildren()
        childlen = childs.__len__()
        if childlen < index+1:
            return None

        return childs[index]





