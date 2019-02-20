#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construct the web structure of response function.
"""

__author__ = 'Infuny'

import functools, inspect, asyncio, os
from aiohttp import web
from urllib import parse
from apis import APIError

import logging
logging.basicConfig(level=logging.DEBUG) # 设置调试等级

# 设计URL处理装饰器
def Handler_decorator(path, *, method): # url装饰器函数
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__route__ = path # URL的路径信息
        wrapper.__method__ = method # URL的方法类型
        return wrapper
    return decorator
get = functools.partial(Handler_decorator, method='GET') # 偏函数：GET方法
post = functools.partial(Handler_decorator, method='POST') # 偏函数：POST方法

# 视图函数参数解析逻辑
'''
使用inspect模块，检查视图函数的参数

inspect.Parameter.kind 类型：
POSITIONAL_OR_KEYWORD       位置+默认参数
VAR_POSITIONAL              可变参数（*args）
KEYWORD_ONLY                命名关键字参数（位置+默认）
VAR_KEYWORD                 关键字参数（**kw）
'''

def get_required_kw_args(fn): # 获取：位置命名关键字参数
    args = []
    params = inspect.signature(fn).parameters # 检查函数参数，返回关于参数的字典
    for name, param in params.items(): # 遍历参数
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)              #为命名关键字参数                          # 默认值为空
    return tuple(args) # 返回为不可修改的tuple

def get_named_kw_args(fn): # 获取：位置命名关键字参数 + 默认命名关键字参数
    args = []
    params = inspect.signature(fn).parameters # 检查函数参数，返回关于参数的字典
    for name, param in params.items(): # 遍历参数
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)

def has_named_kw_arg(fn): # 判断：位置命名关键字参数/默认命名关键字参数
    params = inspect.signature(fn).parameters # 检查函数参数，返回关于参数的字典
    for name, param in params.items(): # 遍历参数
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True

def has_var_kw_arg(fn): # 判断：关键字参数（**kw）
    params = inspect.signature(fn).parameters # 检查函数参数，返回关于参数的字典
    for name, param in params.items(): # 遍历参数
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True

def has_request_arg(fn): # 判断是否有request参数，且是最后一个命名的位置参数/默认参数
    params = inspect.signature(fn).parameters # 检查函数参数，返回关于参数的字典
    found = False # 寻找标识
    for name, param in params.items(): # 遍历参数
        if name == 'request':
            found = True
            continue # 一直找到最后一个参数
        if found and (
                param.kind != inspect.Parameter.VAR_POSITIONAL and # 可变参数（*args）
                param.kind != inspect.Parameter.KEYWORD_ONLY and # 位置命名关键字参数/默认命名关键字参数
                param.kind != inspect.Parameter.VAR_KEYWORD # 关键字参数（**kw）
                ): # 处理位置参数的情况，此时此参数在request之后，故抛出异常
            raise ValueError('request parameter must be the last named parameter in function: %s%s' % (fn.__name__, str(param)))
    return found

# request对象参数提取逻辑
'''
定义RequestHandler从视图函数中分析其需要接受的参数，从web.Request中获取必要的参数
调用视图函数，然后把结果转换为web.Response对象，符合aiohttp框架要求
'''
class RequestHandler(object):
    def __init__(self, app, fn):
        logging.debug('[COROWEB] Start initializing RequestHandler ...')
        self._app = app # 服务器应用框架
        self._func = fn # 视图函数
        self._required_kw_args = get_required_kw_args(fn) # 获取：命名关键字参数（位置）
        self._named_kw_args = get_named_kw_args(fn) # 获取：命名关键字参数（位置+默认）
        self._has_named_kw_arg = has_named_kw_arg(fn) # 判断：命名关键字参数（位置+默认）
        self._has_var_kw_arg = has_var_kw_arg(fn) # 判断：关键字参数（**kw）
        self._has_request_arg = has_request_arg(fn) # 判断：request参数
        logging.debug('[COROWEB] Finish initialing RequestHandler ...')

    async def __call__(self, request): # 定制函数调用方式
        logging.debug('[COROWEB] Start calling RequestHandler ...')
        kw = None # 用于保存请求中的参数
         # （一）若视图函数有命名关键字参数或关键字参数（表示需要） -> 获取request的请求内容（json/post/query_string）
        if self._has_named_kw_arg or self._has_var_kw_arg:
            # 处理POST方法
            if request.method == 'POST':
                logging.debug('[COROWEB] Request Method is POST.')
                # 根据request参数中的content_type使用不同的解析方法
                if request.content_type == None: # (1) content_type不存在，返回错误400
                    return web.HTTPBadRequest(text='JSON body must be object.')
                ct = request.content_type.lower() # 转换为小写，便于检查
                if ct.startswith('application/json'): # (2) JSON格式数据
                    logging.debug('[COROWEB] Request parameters type is "application/json"')
                    params = await request.json() # 解析：解析body字段的JSON数据。dict-like对象
                    if not isinstance(params, dict): # request.json()返回格式不正确（非字典）
                        return web.HTTPBadRequest(text='JSON body must be object.')
                    kw = params # 保存参数
                    logging.debug("[COROWEB] Requset parameters is" + str(kw))
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'): # (3) form表单请求格式
                    logging.debug('[COROWEB] Request parameters type is "application/x-www-form-urlencoded"')
                    params = await request.post() # 解析：解析post内容数据。dict-like对象
                    kw = dict(**params) # 保存参数，组成dict，统一kw格式
                    logging.debug("[COROWEB] Requset parameters is" + str(kw))
                else: # (4) 无匹配类型
                    return web.HTTPBadRequest(text='Unsupported Content-Type: %s' % request.content_type)
            # 处理GET方法
            if request.method == 'GET':
                logging.debug('[COROWEB] Request Method is GET.')
                qs = request.query_string # 返回URL查询语句（?后的键值）。string形式
                if qs: # 有查询语句处理
                    kw = dict() # 键值对参数形式
                    for k, v in parse.parse_qs(qs, True).items(): # 遍历，构造纯键值对映射（可改进，直接用items()）
                        kw[k] = v[0] # 保存参数
                logging.debug("[COROWEB] Requset parameters is" + str(kw))
        # （二）根据是否提取到参数进行处理
        if kw is None:  # 若没有提取到参数
            kw = dict(**request.match_info) # 将match_info的内容映射给kw，那么问题来了，match_info是什么？？？？？？？？？？？？？？？？？？？？
        else: # 若提取到参数
            if self._has_named_kw_arg and (not self._has_var_kw_arg): # 视图需要命名关键字参数，不需要关键字参数
                copy = dict()
                for name in self._named_kw_args: # 只保留视图函数需要的命名关键字参数
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            for k, v in request.match_info.items(): # 判断match_info与命名关键字参数的内容是否重复，以match_info的值为准
                if k in kw:
                    logging.warn('[COROWEB] Dulicate arg name in named arg and kw args: %s' % k) # 参数重复
                kw[k] = v
        # （三）添加request参数
        if self._has_request_arg: # 若视图函数对request有参数要求
            kw['request'] = request # 添加
        # （四）检查位置命名关键字参数
        logging.debug('[COROWEB] Checking _required_kw_args')
        if self._required_kw_args: # 检查位置命名关键字参数
            for name in self._required_kw_args:
                if not name in kw: # 处理未添加的情况
                    logging.warn('[COROWEB] Missing argument: %s' % name)
                    return web.HTTPBadRequest('Missing argument: %s' % name) # 抛出异常，此时出现表示未赋值；若有值，则在前面的选择中已囊括
        # 至此，kw为视图函数fn真正可调用的参数
        logging.info('[COROWEB] Analysing complete. Call function with args: %s' % str(kw))
        try:
            r = await self._func(**kw) # 调用视图函数构造响应内容
            return r
        except APIError as e: # APIError的使用，自定义异常
            return dict(error=e.error, data=e.data, message=e.message)
        logging.debug('[COROWEB] Finish calling RequestHandler ...')

# 视图函数与静态文件注册逻辑
def add_route(app, fn): # 用于注册一个视图函数（映射一个URL请求）
    method = getattr(fn, '__method__', None) # 获取视图函数的请求类型
    path = getattr(fn, '__route__', None) # 获取视图函数的请求路径
    if method is None or path is None: # 检查是否有method和path参数
        raise ValueError('@get or @post not defined in %s.' % fn.__name__)
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn): # 检查是否为协程类型和生成器类型
        fn = asyncio.coroutine(fn) # 变为协程
    logging.info('[COROWEB] Add route %s %s => %s(%s)' % (method, path, fn.__name__, ','.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn)) # 注册函数
    # path 的形式为 "/a/b/c" 或 "/a/{var}"，后者可以匹配一个变量值，该变量会提取出来存放到 request 的一个同名变量中通过 "request.match_info['var']" 获取

def add_routes(app, module_name): # 从模块内批量注册视图函数
    n = module_name.rfind('.') # 从右侧检索，返回索引。若无，返回-1
    if n == -1:
        mod = __import__(module_name, globals(), locals, [], 0) # 导入指定模块
    else:
        name = module_name[(n+1):]
        mod = getattr(__import__(module_name[:n], globals(), locals, [name], 0), name) # 返回模块操作对象
    for attr in dir(mod): # dir()迭代出mod模块中所有的类，实例及函数等对象，str形式
        if attr.startswith('_'): # 忽略“_”开头的对象
            continue
        fn = getattr(mod, attr) # 获取该对象
        if callable(fn): # 确保是函数
            method = getattr(fn, '__method__', None) # 视图函数的请求类型
            path = getattr(fn, '__route__', None) # 视图函数的请求路径
            if method and path: # 当函数具备上述所有信息时注册
                add_route(app, fn) # 注册当前（一个）函数

def add_static(app): # 用于注册静态文件
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static') # 拼接出static文件目录
    app.router.add_static('/static/', path) # 添加静态文件
    logging.info('[COROWEB] Add static %s => %s' % ('/static/', path)) # 记录日志