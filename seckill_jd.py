# -*- encoding: utf-8 -*-
import json
import random
from config import global_config
import requests
import os
import pickle
import time
from logger import logger
from util import (
    response_status,
    save_image,
    open_image,
    parse_json,
    SKException
)


class SpiderSession:
    """
    session相关操作
    """

    def __init__(self):
        self.cookiers_dir_path = "./cookies/"  # 定义cookies路径
        self.user_agent = global_config.getRaw('config', "DEFAULT_USER_AGENT")  # 读取配置文件获取文件头信息
        self.session = self._init_session()

    def _init_session(self):
        """
        添加session
        """
        session = requests.session()
        session.headers = self.get_headers()
        return session

    def get_headers(self):
        """
        添加文件头
        """
        return {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;"
                      "q=0.9,image/webp,image/apng,*/*;"
                      "q=0.8,application/signed-exchange;"
                      "v=b3",
            "Connection": "keep-alive"
        }

    def get_user_agent(self):
        return self.user_agent

    def get_session(self):
        """
        获取当前session
        """
        return self.session

    def get_cookies(self):
        """
        获取当前cookies
        """
        return self.get_session().cookies

    def set_cookies(self, cookies):
        """
        修改cookies
        """
        self.session.cookies.update(cookies)

    def load_cookies_from_local(self):
        """
        从本地加载Cookie
        """
        cookies_file = ''
        if not os.path.exists(self.cookiers_dir_path):
            return False
        for name in os.listdir(self.cookiers_dir_path):
            if name.endswith(".cookies"):
                cookies_file = '{}{}'.format(self.cookiers_dir_path, name)
                break
        if cookies_file == '':
            return False
        with open(cookies_file, 'rb') as f:
            local_cookies = pickle.load(f)
        self.set_cookies(local_cookies)

    def save_cookies_to_local(self, cookie_file_name):
        """
        保存cookie到本地
        :param cookie_file_name: 存放cookie的文件名称
        """
        cookies_file = "{}{}".format(self.cookies_dir_path, cookie_file_name)
        directory = os.path.dirname(cookie_file_name)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(cookies_file, 'wb') as f:
            pickle.dump(self.get_cookies(), f)


class JdLogin:
    """京东扫码打登录"""

    def __init__(self, spider_session: SpiderSession):
        """
        初始化扫码登录:
            1. 访问登录二维码页面, 获取TOKEN
            2. 使用Token获取票据
            3. 校验票据
        """
        self.scan_code_img_file = 'jd_scan_code.png'

        self.spider_session = spider_session
        self.session = self.spider_session.get_session()

        self.is_login = False

    def refresh_login_status(self):
        """
        刷新是否登录状态
        """
        self.is_login = self._validate_cookies()

    def _validate_cookies(self):
        """
        验证cookies是否有效(是否登录)
        通过访问用户订单列表进行判断: 未登录会重定向到登录页面
        :return: cookies是否有效 True/False
        """
        url = 'https://order.jd.com/center/list.action'
        payload = {
            'rid': str(int(time.time()*1000))
        }
        try:
            resp = self.session.get(url=url, params=payload, allow_redirects=False)
            if resp.status_code == requests.codes.OK:
                return True
        except Exception as e:
            logger.error(e)
        return False

    def _get_login_page(self):
        """获取PC登录页面"""
        url = "https://passport.jd.com/new/login.aspx"
        page = self.session.get(url, headers=self.spider_session.get_headers())
        return page

    def _get_jdcode(self):
        """获取京东登录二维码"""
        url = 'https://qr.m.jd.com/show'
        payload = {
            'appid': 133,
            'size': 147,
            't': str(int(time.time() * 1000)),
        }
        headers = {
            'User-Agent': self.spider_session.get_user_agent(),
            'Referer': 'https://passport.jd.com/new/login.aspx',
        }
        resp = self.session.get(url=url, headers=headers, params=payload)
        if not response_status(resp):
            logger.info("获取二维码失败")
            return False

        save_image(resp, self.scan_code_img_file)
        logger.info('二维码获取成功, 使用京东APP扫码')
        open_image(self.scan_code_img_file)
        return True

    def _get_jdcode_ticket(self):
        """
        通过token获取票据
        """
        url = 'https://qr.m.jd.com/check'
        payload = {
            'appid': '133',
            'callback': 'jQuery{}'.format(random.randint(1000000, 9999999)),
            'token': self.session.cookies.get('wlfstk_smdl'),
            '_': str(int(time.time() * 1000)),
        }
        headers = {
            'User-Agent': self.spider_session.get_user_agent(),
            'Referer': 'https://passport.jd.com/new/login.aspx',
        }
        resp = self.session.get(url=url, headers=headers, params=payload)

        if not response_status(resp):
            logger.error('获取二维码扫码结果异常')
            return False

        resp_json = parse_json(resp.text)
        if resp_json['code'] != 200:
            logger.info('Code: %s, Message: %s', resp_json['code'], resp_json['msg'])
            return None
        else:
            logger.info('已经完成手机客户端确认')
            return resp_json['ticket']

    def _validate_jdcode_ticket(self, ticket):
        """
        通过已获取的票据进行校验
        :param ticket: 已获取的票据
        """
        url = 'https://passport.jd.com/uc/qrCodeTicketValidation'
        headers = {
            'User-Agent': self.spider_session.get_user_agent(),
            'Referer': 'https://passport.jd.com/uc/login?ltype=logout',
        }
        resp = self.session.get(url=url, headers=headers, params={'t': ticket})
        if not response_status(resp):
            return False

        resp_json = json.loads(resp.text)
        if resp_json['returnCode'] == 0:
            return True
        else:
            logger.info(resp_json)
            return False

    def login_by_jdcode(self):
        """扫码登录"""
        self._get_login_page()

        # 下载二维码
        if not self._get_jdcode():
            raise SKException('二维码下载失败')

        # 获取ticket
        ticket = None
        retry_time = 85
        for _ in range(retry_time):
            ticket = self._get_jdcode_ticket()
            if ticket:
                break
            time.sleep(2)
        else:
            raise SKException('二维码过期, 重新扫码')

        if not self._validate_jdcode_ticket(ticket):
            raise SKException("二维码信息校验失败")

        self.refresh_login_status()
        logger.info('二维码登录成功')


if __name__ == "__main__":
    spids = SpiderSession()
    sc = JdLogin(spids)
    print(sc.login_by_jdcode())
    # unick = jd915268rii
