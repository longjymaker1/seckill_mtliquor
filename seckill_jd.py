# -*- encoding: utf-8 -*-
import json
import random
from config import global_config
import requests
import os
import pickle
import time
from lxml import etree
from logger import logger
from timer import Timer
from util import (
    response_status,
    save_image,
    open_image,
    parse_json,
    SKException,
    wait_some_time
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
        cookies_file = "{}{}".format(self.cookiers_dir_path, cookie_file_name)
        directory = os.path.dirname(cookies_file)
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


class JdSeckill:
    """抢购流程, 预约; 抢购"""
    def __init__(self):
        self.spider_session = SpiderSession()
        self.spider_session.load_cookies_from_local()

        self.jdlogin = JdLogin(self.spider_session)  # 登录

        # 初始化信息
        self.sku_id = global_config.getRaw('config', 'sku_id')
        self.seckill_num = 2
        self.seckill_init_info = dict()
        self.seckill_url = dict()
        self.seckill_order_data = dict()
        self.timers = Timer()

        self.session = self.spider_session.get_session()
        self.user_agent = self.spider_session.get_user_agent()
        self.nick_name = None

    def login_by_jdcode(self):
        """扫码登录"""
        if self.jdlogin.is_login:
            logger.info('登录成功')
            return

        self.jdlogin.login_by_jdcode()

        if self.jdlogin.is_login:
            self.nick_name = self.get_username()  # 获取登录用户名
            self.spider_session.save_cookies_to_local(self.nick_name)
        else:
            raise SKException("二维码登录失败")

    def check_login(func):
        """
        用户登录状态装饰器，如果用户没登录，调用扫码登录
        """
        def new_func(self, *args, **kwargs):
            if not self.jdlogin.is_login:
                logger.info("{0} 需登陆后调用，开始扫码登陆".format(func.__name__))
                self.login_by_jdcode()
                # is_effective  # 判断是否有效
            return func(self, *args, **kwargs)
        return new_func

    def get_username(self):
        """获取用户信息"""
        url = 'https://passport.jd.com/user/petName/getUserInfoForMiniJd.action'
        payload = {
            'callback': 'jQuery{}'.format(random.randint(1000000, 9999999)),
            '_': str(int(time.time() * 1000)),
        }
        headers = {
            'User-Agent': self.user_agent,
            'Referer': 'https://order.jd.com/center/list.action',
        }

        resp = self.session.get(url=url, params=payload, headers=headers)

        try_count = 5
        while not resp.text.startswith("jQuery"):
            try_count = try_count - 1
            if try_count > 0:
                resp = self.session.get(url=url, params=payload, headers=headers)
            else:
                break
            wait_some_time()
            # jQuery2381773({"imgUrl":"//storage.360buyimg.com/i.imageUpload/xxx.jpg",
            # "lastLoginTime":"","nickName":"xxx","plusStatus":"0","realName":"xxx","userLevel":x,
            # "userScoreVO":{"accountScore":xx,"activityScore":xx,"consumptionScore":xxxxx,
            # "default":false,"financeScore":xxx,"pin":"xxx","riskScore":x,"totalScore":xxxxx}})
        return parse_json(resp.text).get('nickName')

    def get_sku_title(self):
        """获取商品名称"""
        url = 'https://item.jd.com/{}.html'.format(global_config.getRaw('config', 'sku_id'))
        resp = self.session.get(url).content
        x_data = etree.HTML(resp)
        sku_title = x_data.xpath('/html/head/title/text()')
        return sku_title[0]

    @check_login
    def reserve(self):
        """预约"""
        self._reserve()

    def _reserve(self):
        """预约"""
        while True:
            try:
                self.make_reserve()
                break
            except Exception as e:
                logger.info('预约发生异常！！！', e)
            wait_some_time()

    def make_reserve(self):
        url = 'https://yushou.jd.com/youshouinfo.action?'
        payload = {
            'callback': 'fetchJSON',
            'sku': self.sku_id,
            '_': str(int(time.time() * 1000)),
        }
        headers = {
            'User-Agent': self.user_agent,
            'Referer': 'https://item.jd.com/{}.html'.format(self.sku_id),
        }
        resp = self.session.get(url=url, params=payload, headers=headers)
        resp_json = parse_json(resp.text)
        reserve_url = resp_json.get('url')
        self.timers.start()
        while True:
            try:
                self.session.get(url='https:' + reserve_url)
                logger.info('预约成功, 已经获得抢购资格 / 已经成功预约过了,无需重复预约')
                # success_message = "预约成功，已获得抢购资格 / 您已成功预约过了，无需重复预约"
                # send_wechat(success_message)  # 微信提醒
                break
            except Exception as e:
                logger.error('预约失败, 正在重试... ...')

    @check_login
    def seckill(self):
        """抢购"""
        self._seckill()

    def _seckill(self):
        """抢购"""
        while True:
            try:
                self.request_seckill_url()  # 访问商品链接
                while True:
                    self.request_seckill_checkout_pate()  # 访问抢购订单结算页面
                    self.submit_seckill_order()  # 提交抢购（秒杀）订单
            except Exception as e:
                logger.info('抢购发生异常, 稍后继续执行', e)
            wait_some_time()

    def get_seckill_url(self):
        """
        获取商品的抢购链接
        点击"抢购"按钮后，会有两次302跳转，最后到达订单结算页面
        这里返回第一次跳转后的页面url，作为商品的抢购链接
        :return: 商品的抢购链接
        """
        url = 'https://itemko.jd.com/itemShowBtn'
        payload = {
            'callback': 'jQuery{}'.format(random.randint(1000000, 9999999)),
            'skuId': self.sku_id,
            'from': 'pc',
            '_': str(int(time.time() * 1000)),
        }
        headers = {
            'User-Agent': self.user_agent,
            'Host': 'itemko.jd.com',
            'Referer': 'https://item.jd.com/{}.html'.format(self.sku_id),
        }
        while True:
            resp = self.session.get(url=url, headers=headers, params=payload)
            resp_json = parse_json(resp.text)
            if resp_json.get('url'):
                router_url = 'https:' + resp_json.get('url')
                seckill_url = router_url.replace(
                    'divide', 'marathon'
                ).replace(
                    'user_routing', 'captcha.html'
                )
                logger.info('抢购链接获取成功: %s', seckill_url)
                return seckill_url
            else:
                logger.info('抢购链接获取失败, 稍后重试')
                wait_some_time()

    def request_seckill_url(self):
        """访问商品的抢购链接, 用于设置cookie等"""
        logger.info('用户:{}'.format(self.get_username()))
        logger.info('商品名称:{}'.format(self.get_sku_title()))
        self.timers.start()
        self.seckill_url[self.sku_id] = self.get_seckill_url()
        logger.info('访问商品抢购链接...')
        headers = {
            'User-Agent': self.user_agent,
            'Host': 'marathon.jd.com',
            'Referer': 'https://item.jd.com/{}.html'.format(self.sku_id),
        }
        self.session.get(
            url=self.seckill_url.get(self.sku_id),
            headers=headers,
            allow_redirects=False
        )

    def request_seckill_checkout_pate(self):
        """访问抢购订单结算页面"""
        logger.info('访问抢购订单结算页面...')
        url = 'https://marathon.jd.com/seckill/seckill.action'
        payload = {
            'skuId': self.sku_id,
            'num': self.seckill_num,
            'rid': int(time.time())
        }
        headers = {
            'User-Agent': self.user_agent,
            'Host': 'marathon.jd.com',
            'Referer': 'https://item.jd.com/{}.html'.format(self.sku_id),
        }
        self.session.get(url=url, params=payload, headers=headers, allow_redirects=False)

    def _get_seckill_init_info(self):
        """
        获取秒杀初始化信息, 地址, 发票, token
        :return: 初始化信息组成的dict
        """
        logger.info('获取藐视啊初始化信息...')
        url = 'https://marathon.jd.com/seckillnew/orderService/pc/init.action'
        data = {
            'sku': self.sku_id,
            'num': self.seckill_num,
            'isModifyAddress': 'false',
        }
        headers = {
            'User-Agent': self.user_agent,
            'Host': 'marathon.jd.com',
        }
        resp = self.session.post(url=url, data=data, headers=headers)

        resp_json = None
        try:
            resp_json = parse_json(resp.text)
        except Exception:
            raise SKException('抢购失败，返回信息:{}'.format(resp.text[0: 128]))
        return resp_json

    def _get_seckill_order_data(self):
        """
        生成提交抢购订单锁余姚的请求参数
        :return: 请求体参数组成的dict
        """
        logger.info('生成提交抢购订单所需参数...')
        # 获取用户秒杀初始化信息
        self.seckill_init_info[self.sku_id] = self._get_seckill_init_info()
        init_info = self.seckill_init_info.get(self.sku_id)
        default_address = init_info['addressList'][0]  # 默认地址dict
        invoice_info = init_info.get('invoiceInfo', {})  # 默认发票信息dict, 有可能不返回
        token = init_info['token']
        data = {
            'skuId': self.sku_id,
            'num': self.seckill_num,
            'addressId': default_address['id'],
            'yuShou': 'true',
            'isModifyAddress': 'false',
            'name': default_address['name'],
            'provinceId': default_address['provinceId'],
            'cityId': default_address['cityId'],
            'countyId': default_address['countyId'],
            'townId': default_address['townId'],
            'addressDetail': default_address['addressDetail'],
            'mobile': default_address['mobile'],
            'mobileKey': default_address['mobileKey'],
            'email': default_address.get('email', ''),
            'postCode': '',
            'invoiceTitle': invoice_info.get('invoiceTitle', -1),
            'invoiceCompanyName': '',
            'invoiceContent': invoice_info.get('invoiceContentType', 1),
            'invoiceTaxpayerNO': '',
            'invoiceEmail': '',
            'invoicePhone': invoice_info.get('invoicePhone', ''),
            'invoicePhoneKey': invoice_info.get('invoicePhoneKey', ''),
            'invoice': 'true' if invoice_info else 'false',
            'password': global_config.get('account', 'payment_pwd'),
            'codTimeType': 3,
            'paymentType': 4,
            'areaCode': '',
            'overseas': 0,
            'phone': '',
            'eid': global_config.getRaw('config', 'eid'),
            'fp': global_config.getRaw('config', 'fp'),
            'token': token,
            'pru': ''
        }
        return data

    def submit_seckill_order(self):
        """
        提交抢购（秒杀）订单
        :return: 抢购结果 True/False
        """
        pass


if __name__ == "__main__":
    # unick = jd915268rii
    jds = JdSeckill()
    jds.reserve()
