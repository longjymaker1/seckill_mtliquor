# -*- encoding: utf-8 -*-
import time
import requests
import json

from datetime import datetime
from logger import logger
from config import global_config


class Timer:
    def __init__(self, sleep_interval=0.5):
        buy_time_everyday = global_config.getRaw('config', 'buy_time')
        localtime = time.localtime(time.time())
        self.buy_time = datetime.strptime(
            localtime.tm_year.__str__() + '-' + localtime.tm_mon.__str__() + '-' + localtime.tm_mday.__str__()
            + ' ' + buy_time_everyday, "%Y-%m-%d %H:%M:%S.%f"
        )
        # 购买时间转化为毫秒
        self.buy_time_ms = int(time.mktime(self.buy_time.timetuple()) * 1000.0 + self.buy_time.microsecond / 1000)
        self.sleep_interval = sleep_interval

        self.diff_time = self.local_jd_dime_diff()

    @staticmethod
    def jd_time():
        """
        从京东服务器获取时间毫秒
        """
        url = 'https://a.jd.com//ajax/queryServerData.html'
        ret = requests.get(url).text
        js = json.loads(ret)
        return int(js["serverTime"])

    @staticmethod
    def local_time():
        """获取本地时间"""
        return int(round(time.time() * 1000))

    def local_jd_dime_diff(self):
        """计算本地时间与京东服务器时间差"""
        return self.local_time() - self.jd_time()

    def start(self):
        """根据本地时间与京东服务时间等待运行"""
        logger.info("正在等待到达设定时间: {}, 检测本地时间与京东服务器时间误差【{}】毫秒".format(self.buy_time, self.diff_time))
        while True:
            if self.local_time() - self.diff_time >= self.buy_time_ms:
                logger.info("时间到达, 执行开始... ...")
                break
            else:
                time.sleep(self.sleep_interval)


if __name__ == '__main__':
    t0 = Timer()
    print(t0.jd_time())
    print(t0.local_time())
    print(t0.local_jd_dime_diff())
