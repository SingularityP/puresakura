#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Infuny'

"""
async web application.
"""

import asyncio, os, json, time # 导入异步IO相关模块
from datetime import datetime # 导入时间模块

from aiohttp import web # 导入异步的Web框架
from jinja2 import Environment, FileSystemLoader # 导入jinja2模板引擎

import orm
from coroweb import add_routes, add_static

from handlers import cookie2user, COOKIE_NAME
from config import configs

import logging # 导入日志模块
logging.basicConfig(level=logging.DEBUG) # 设置全局日志等级

# 初始化jinja2模板
def init_jinja2(app, **kw):
    logging.info('init jinja2...') # 记录日志
    # （1）建立Environment类options参数的配置
    options = dict(
            # 自动转译xml/html的特殊字符
            autoescape = kw.get('autoescape', True),
            # 代码块的开始、结束标志
            block_start_string = kw.get('block_start_string', '{%'),
            block_end_string = kw.get('block_end_string', '%}'),
            # 变量的开始、结束标志
            variable_start_string = kw.get('variable_start_string', '{('),
            variable_end_string = kw.get('variable_end_string', ')}'),
            # 自动加载修改后的模板文件
            auto_reload = kw.get('auto_reload', True)
            )
    # （2）建立模板加载器加载模板文件的路径
    # 获取模板文件夹路径
    path = kw.get('path', None)
    if not path: # 处理路径为空的情况
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates') # 构造路径
    # Environment类是jinja2的核心类，用来保存配置、全局对象以及模板文件的路径
    # FileSystemLoader类加载path路径中的模板文件的路径
    env = Environment(loader=FileSystemLoader(path), **options) # 创建核心引擎，使用指定的模板文件路径
    # （3）添加过滤器，完成初始化
    filters = kw.get('filters', None)
    if filters: # 有过滤器的时候
        for name, f in filters.items():
            env.filters[name] = f # filters是Environment类的属性：过滤器字典（过滤器名:过滤器指针）
    # （）最终给app添加上__templateing__字段，该字段表示模板环境
    app['__templating__'] =  env
    logging.info('fini jinja2...')
    
# 编写过滤器
def datetime_filter(t):
    delta = int(time.time()-t)
    if delta < 60:
        return u'1 seconds ago'
    if delta < 3600:
        return u'%s minutes ago' % (delta//60)
    if delta < 86400:
        return u'%s hous ago' % (delta//3600)
    if delta < 604800:
        return u'%s days ago' % (delta//86400)
    dt = datetime.fromtimestamp(t) # 通过timestamp创建datetime对象，默认本地时区
    return u'%s-%s-%s' % (dt.year, dt.month, dt.day) # 返回年月日

# 编写用于输出日志的middleware（前件）
async def logger_factory(app, handler): # handler为视图函数
    async def logger(request):
        logging.info('Request: %s %s' % (request.method, request.path))
        return await handler(request) # 因为是协程，handler处理只有一个，都交回处理
    return logger

# 解析请求的body内容然后用视图函数处理返回（前件）
async def data_factory(app, handler): # handler为视图函数
    async def parse_data(request):
        if request.method == 'POST':
            request.__data__ = await request.json()
        elif request.content_type.startwith('application/x-www-form-urlencode'):
            request.__data__ = await request.post()
        logging.info('request form: %s' % str(request.__data__))
        return (await handler(request))
    return parse_data

# 编写使用cookie解析方法的中间件（前件）
async def auth_factory(app, handler):
    async def auth(request):
        logging.info('check user: %s %s' % (request.method, request.path))
        request.__user__ = None # 默认设置用户名为空（默认不通过，需验证cookie后再判断是否通过）
        cookie_str = request.cookies.get(COOKIE_NAME) # 通过cookie名字获取cookie值
        if cookie_str: # 获取到cookie值
            user = await cookie2user(cookie_str) # 解析cookie
            if user: # 如果解析成功
                logging.info('set current user: %s' % user.email) # 记录日志
                request.__user__ = user # 通过
        if request.path.startswith('/manage/') and (request.__user__ is None or not request.__user__.admin):
            return web.HTTPFound('/signin') # 重新登录
        return (await handler(request))
        logging.debug('end check user')
    return auth

# 编写构造Response对象的middleware（后件）
'''
请求对象request的处理工序：
logger_factory => response_factory => RequsetHandler().__call__ => handler
响应对象response的处理工序：
1.由视图函数处理request后返回数据
2.@get@post装饰器返回对象上附加'__method__'和'__route__'属性，使其附带URL信息
3.response_factory对处理后的对象，经过一系列类型判断，构造出真正的web.Response对象
'''
async def response_factory(app, handler):
    async def response(request):
        logging.info('Response handler...') # 记录日志
        logging.info(request)
        r = await handler(request) # 视图函数返回处理后的数据
        logging.info('Response result = %s' % str(r)) # 记录日志（视图函数响应内容）
        if isinstance(r, web.StreamResponse): # 若返回response对象，StreamResponse是所有Response对象的父类
            logging.debug('Response_factory - None')
            logging.debug(type(r))
            return r # 无需构造，直接返回
        if isinstance(r, bytes): # 若返回bytes串
            logging.debug('Response_factory - bytes')
            resp = web.Response(body=r) # 继承自StreamResponse，接收body参数，构造HTTP响应内容
            resp.content_type = 'application/octet-stream' # 设置响应的content-type
            return resp # 返回响应内容
        if isinstance(r, str):
            logging.debug('Response_factory - str')
            if r.startswith('redirect'): # 若返回重定向字符串
                return web.HTTPFound(r[9:]) # 重定向至目标URL
            resp = web.Response(body=r.encode('utf-8')) # 用字符串的utf-8编码构造HTTP响应
            resp.content_type = 'text/html;charset=utf-8' # 设置content-type属性：utf-8编码的text格式
            return resp # 返回响应内容
        if isinstance(r, dict): # 如果返回dict对象（可能是json，疯狂暗示使用模板文件( • ̀ω•́ )✧）
            logging.debug('Response_factory - dict')
            template = r.get('__template__', None) # 获取__template__信息
            if template is None: # 不带有模板信息，返回json对象
                '''
                ensure_ascii : 默认True，仅能输出ascii格式数据。故设置为False
                default : r对象会先被传入default函数进行处理，然后才被序列化为json对象（对象的序列化需要手动编写）
                __dict__ : 以dict的形式返回对象属性和值的映射
                '''
                resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda obj: obj.__dict__).encode('utf-8')) # 构造序列化json并且使用utf-8编码
                resp.content_type = 'application/json;charset=utf-8' # 设置content-type属性
                return resp
            else: # 表示带有模板信息
                '''
                app['__templating__'] : 获取已初始化的Environment对象，调用get_template()方法返回Template对象
                调用Template对象的render()方法，传入r渲染模板，返回unicode格式字符串，将其用utf-8编码
                '''
                r['__user__'] = request.__user__ # 设置用户名
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r, int) and (600>r>100): # 如果返回响应码
            logging.debug('Response_factory - int')
            resp = web.Response(status=r) # 构造响应码对象的响应
            return resp
        if isinstance(r, tuple) and len(r) == 2: # 如果返回了一组响应代码和原因，如 (200, 'OK') (404, 'Not Found')
            logging.debug('Response_factory - tuple int')
            status_code, message = r
            if isinstance(status_code, int) and (600>status_code>=100):
                resp = web.Response(status=r, text=str(message)) # 根据响应码及原因构造返回对象
        resp = web.Response(body=str(r).encode('utf-8')) # 以上条件均不满足，默认返回操作
        resp.content_type = 'text/plain;charset=utf-8' # utf-8纯文本
        return resp
    return response

# 更新Web App框架
async def init(loop): # 2 生成web框架coroutine
    await orm.create_pool(loop=loop, **configs.db) # 获取orm操作线程
    app = web.Application(loop=loop, middlewares=[logger_factory, auth_factory, response_factory]) # 2.1 建立逻辑框架
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    add_routes(app, 'handlers') # 2.2 映射首页处理请求，这里另设handler文件存放视图函数
    add_static(app)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000) # 2.3 建立服务器（协议工厂）
    logging.info('[APP] Server started at http://127.0.0.1:9000 ...')
    return srv # 2.3 返回服务器对象

loop = asyncio.get_event_loop() # 2 获取事件循环
loop.run_until_complete(init(loop)) # 3 获取协程对象，注册为事件
loop.run_forever() # 4 持续运行