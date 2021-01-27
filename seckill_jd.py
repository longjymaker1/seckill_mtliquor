# -*- encoding: utf-8 -*-
from config import global_config
import requests
import os
import pickle


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
        from name in os.listdir(self.cookiers_dir_path):
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



