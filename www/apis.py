#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 13:59:11 2018

@author: Infinity
"""

__author__ = 'Infuny'

'''
JSON API definition. 用于存储api所用到的类。
'''

import logging
logging.basicConfig(level=logging.DEBUG)

# 自定义异常类
class APIError(Exception): # 继承Exception
    '''
    the base APIError which contains error(required), data(optional) and message(optional).
    '''
    def __init__(self, error, data='', message=''): # 构造方法初始化
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message

class APIValueError(APIError):
    '''
    Indicate the input has error or invalid. The data specifies the error field of input form.
    '''
    def __init__(self, field, message=''):
        logging.debug("[APIS] APIValueError.")
        super(APIValueError, self).__init__('value:invalid', field, message)
        
class APIResourceNotFoundError(APIError):
    '''
    Indicate the resource was not found. The data specifies the resource name.
    '''
    def __init__(self, field, message=''):
        logging.debug("[APIS] APIResourceNotFoundError.")
        super(APIResourceNotFoundError, self).__init__('value:notfound', field, message)
        
class APIPermissionError(APIError):
    '''
    Indicate the api has no permission.
    '''
    def __init__(self, field, message=''):
        logging.debug("[APIS] APIPermissionError.")
        super(APIPermissionError, self).__init__('permission:forbidden', 'permission', message)