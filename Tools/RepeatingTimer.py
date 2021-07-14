from threading import Timer

class RepeatingTimer(Timer):
    def run(self):
        while not self.finished.is_set(): # 没有收到停止信号则一直循环
            self.function(*self.args, **self.kwargs) # 执行给定的方法
            self.finished.wait(self.interval) # 等待一段时间
