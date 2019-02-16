#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 09:15:07 2018

@author: Infuny
"""

__author__ = 'Infuny'

import config_default

# 重写dict类型，用于支持属性访问模式：x.y
class Dict(dict):
    '''
    Simple dict but support access as x.y sytle.
    '''
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw) # 使用父类构造方法构造Dict
        for k, v in zip(names, values):
            self[k] = v # 将name和values内的必要参数放入字典中
    
    def __getattr__(self, key): # 定制属性引用默认处理方法
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)
            
    def __setattr__(self, key, value): # 定制属性赋值默认处理方法
        self[key] = value

def merge(defaults, override): # 默认配置与覆盖配置的合并方法
    r = {} # 存放需要覆盖的项
    for k, v in defaults.items(): # 遍历默认配置选项
        if k in override: # 如果覆盖配置中存在相同项
            if isinstance(v, dict): # 并且是dict类型
                r[k] = merge(v, override[k]) # 递归调用处理
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r

def toDict(d): # 转换为单层dict字典形式：{ key1:value1, key2:value2, ... }
    D = Dict()
    for k, v in d.items():
        D[k] = toDict(v) if isinstance(v, dict) else v
    return D

configs = config_default.configs # 首先读取默认配置

try:
    import config_override
    configs = merge(configs, config_override.configs) # 将config_override中的重复项覆盖到default中去
except ImportError:
    pass

configs = toDict(configs) # 转换为单层dict形式