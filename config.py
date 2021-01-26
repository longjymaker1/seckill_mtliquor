# -*- encoding: utf-8 -*-
import os
import configparser


class GetConfig:
    def __init__(self, configFile='config.ini'):
        self._path = os.path.join(os.getcwd(), configFile)
        if not os.path.exists(self._path):
            raise FileNotFoundError("没有找到文件: config.ini")

        self._config = configparser.ConfigParser()
        self._config.read(self._path, encoding="utf-8-sig")
        
        self._configRaw = configparser.ConfigParser()
        self._configRaw.read(self._path, encoding="utf-8-sig")

    def get(self, section, name):
        return self._config.get(section, name)

    def getRaw(self, section, name):
        return self._config.get(section, name)


global_config = GetConfig()


if __name__ == '__main__':
    GetConfig()
