# -*- coding:gb2312 -*-
# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# ������Ҫ����selenium�⣬�����ܹ���������ʶ��ٿ�������Ŀ�
from pip._vendor.distlib.compat import raw_input
# OS�����ǲ���dosϵͳʱ��Ҫ����Ŀ�
# ����һ��python �ļ��е��࣬һ��python�ļ�����һ��ģ��
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
