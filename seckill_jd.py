# -*- encoding: utf-8 -*-
from config import global_config
import requests


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
