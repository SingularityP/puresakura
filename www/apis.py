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
from aiohttp import web

import logging
logging.basicConfig(level=logging.DEBUG)

class Page(object):
    '''
    Page object for displaying pages. 该类用于存储分页信息。
    '''
    def __init__(self, item_count, page_index=1, page_size=10):
        self.item_count = item_count # 条目总数
        self.page_size = page_size # 每页容纳的条目数
        self.page_count = item_count // page_size + (1 if item_count % page_size > 0 else 0) # 总页数
        if (item_count == 0) or (page_index > self.page_count): # 处理无条目或当前页数大于总页数的情况
            self.offset = 0 # 当前条目指针（表示指针前的条目总数）
            self.limit = 0 # 当前页条目总数
            self.page_index = 1 # 当前页码，设置为 1
        else:
            self.page_index = page_index # 当前页码
            self.offset = self.page_size *  (self.page_index - 1) # 当前页其实下标
            self.limit = self.page_size # 一页大小限制
        self.has_next = self.page_index < self.page_count # 是否有下一页
        self.has_previous = self.page_index > 1 # 是否有上一页

    def __str__(self):
        return 'item_count: %s, page_count: %s, page_index: %s, page_size %s, offset: %s, limit: %s' % (self.item_count, self.page_count, self.page_index, self.page_index, self.page_size, self.limit)

    __repr__ = __str__

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
        raise web.HTTPBadRequest(reason=field, text=message)
        
class APIResourceNotFoundError(APIError):
    '''
    Indicate the resource was not found. The data specifies the resource name.
    '''
    def __init__(self, field, message=''):
        logging.debug("[APIS] APIResourceNotFoundError.")
        super(APIResourceNotFoundError, self).__init__('value:notfound', field, message)
        raise web.HTTPGone(reason=field, text=message)
        
class APIPermissionError(APIError):
    '''
    Indicate the api has no permission.
    '''
    def __init__(self, field, message=''):
        logging.debug("[APIS] APIPermissionError.")
        super(APIPermissionError, self).__init__('permission:forbidden', 'permission', message)
        raise web.HTTPUnauthorized(reason=field, text=message)