# -*- coding:gb2312 -*-
# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# 这里需要引入selenium库，它是能够帮助我们识别操控浏览器的库
from pip._vendor.distlib.compat import raw_input
# OS是我们操作dos系统时需要引入的库
# 导入一个python 文件中的类，一个python文件就是一个模块
from FeederHelper.feederTools import FeederFun
from Tools.Win32Helper import Win32ComHelper
def run():
    fun = FeederFun()
    fun.autofitForm()
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        # Win32ComHelper.killProcess("main.exe")
        run()
    except Exception as e:
        print(e)
    finally:
        raw_input('Enter key for exist')
