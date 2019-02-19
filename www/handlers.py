#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 00:05:23 2018

@author: Infuny
"""
from coroweb import get, post
from models import User, Blog, Comment, Reply, next_id
from config import configs
from apis import APIValueError, APIError, APIPermissionError, APIResourceNotFoundError

from aiohttp import web
import json, time, hashlib, re, logging
logging.basicConfig(level=logging.DEBUG)

# 1 首页相关逻辑
# 1.1 页面请求
# 1.1.1 获取首页 index.html
@get('/')
async def index(request):
    logging.debug('[HANDLER] Handlering index.html ...')

    return {
            '__template__' : 'index.html', # 'template__'参数指定的模板文件是'test.html'，其他参数是传递给模板的数据
            'images' : configs.images, # 图片路径信息
            }

# 1.2 API 请求
# 1.2.1 获取博客列表数据 
@get('/api/blogs')
async def getBlogs():
    logging.debug('[HANDLER] Handlering /api/blogs in index.html ...')
    infos = await Blog.findAll(limit=10, orderBy='created_at desc', items=['name', 'summary', 'user_name', 'created_at', 'readers'])
    return {
            'infos' : infos, # 博客数据，不带有模板，在 app.py 内的 ResponseFactory 内会自动转换为 json
            }

# 2 用户管理相关逻辑
# 2.1 页面请求
# 2.1.1 获取

# 2.2 API 请求
# 2.2.1 用户注册逻辑
COOKIE_NAME = 'sakurasession' # Cookie 名称
_COOKIE_KEY = configs.session.secret # Cookie 盐
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$') # 邮箱正则模式
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$') # SHA1 口令正则模式

def user2cookie(user, max_age): # 生成 Cookie（id-expiers-sha1）
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    logging.debug('[HANDLER] Set cookie: %s' % '-'.join(L))
    return '-'.join(L)

async def cookie2user(cookie_str): # 用来解析 Cookie
    if not cookie_str: # 如果没有cookie
        return None
    try:
        L = cookie_str.split('-') # 将cookie拆解
        if len(L) != 3: # cookie格式不正确
            logging.warn('[HANDLER] Cookie format is wrong.')
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time(): # 如果寿命时间小于当前时间
            logging.warn('[HANDLER] Cookie is overdue.')
            return None
        user = await User.find(uid) # 获取指定用户
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY) # 制作cookie值
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('[HANDLER] Invalid sha1.')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

@post('/api/register') # 用户注册 api
async def api_register_user(*, email, name, passwd):
    logging.debug('[HANDLER] Handlering /api/users in index.html ...')
    if not name or not name.strip(): # 如果没有名字
        raise APIValueError('name') # api值异常
    if not email or not _RE_EMAIL.match(email): # 如果与邮箱re正则不匹配
        raise APIValueError('email') # api值异常
    if not passwd or not _RE_SHA1.match(passwd): # 如果与密码re正则不匹配
        raise APIValueError('passwd') # api值异常
    users = await User.findAll('email=?', [email]) # 获取数据库中指定的用户信息
    if len(users) > 0: # 如果用户中已有数据
        raise APIError('register:failed', 'email', 'Email is already in use.') # api逻辑异常
    uid = next_id() # 分配唯一id
    sha1_passwd = '%s:%s' % (uid, passwd) # 制作 sha1 加密口令
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    await user.save() # 保存信息到数据库
    # 制作会话cookie，用于保存用户状态：
    r = web.Response() # 建立web响应
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True) # 设置 Cookie
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

# 2.2.2 用户登录逻辑
@post('/api/signin') # 用户验证 api
async def authenticate(*, email, passwd):
    logging.debug('[HANDLER] Handlering /api/signin in index.html ...')
    if not email: # 如果没有邮箱
        raise APIValueError('email', 'Invalid email.') # api 值异常
    if not passwd: # 如果没有密码
        raise APIValueError('passwd', 'Invalid passwd.') # api 值异常
    users = await User.findAll('email=?', [email]) # 获取指定用户信息
    if len(users) == 0: # 如果没有该用户
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # 检查密码
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8')) # 插入用户 id
    sha1.update(b':') # 来一个冒号
    sha1.update(passwd.encode('utf-8')) # 插入用户口令
    if user.passwd != sha1.hexdigest(): # 检查密码
        raise APIValueError('passwd', 'Invalid password.') # api值异常
    # 此时密码验证成功，设置cookie
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True) # 设置 Cookie
    user.passwd = '******' # 隐藏口令
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

# 2.2.3 用户登出逻辑
@get('/api/signout') # 用户登出 api（会跳转到其他页面）
async def signout(request):
    logging.debug('[HANDLERS] Handlering /aip/signout in index.html ...')
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True) # 删除 Cookie
    return r