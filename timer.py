# -*- encoding: utf-8 -*-
import time
import requests
import json

from datetime import datetime
from logger import logger
from config import global_config


class Time:
    def __init__(self, sleep_interval=0.5):
        buy_time_everyday = global_config.getRaw('config', 'buy_time')