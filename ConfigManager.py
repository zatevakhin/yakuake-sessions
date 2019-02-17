# -*- coding: utf-8 -*-

import json
from copy import copy


class ConfigManager:
    
    def __init__(self, file: str):
        self.__config = {}

        try:
            self.__config = json.load(open(file))
        except Exception as e:
            raise e

    def get(self, param: str, default=None):
        config = copy(self.__config)

        for key in param.split("."):
            config = config.get(key, default)

        return config

    def set(self, param: str, value):
        self.__config[param] = value
