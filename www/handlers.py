#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 00:05:23 2018

@author: Infuny
"""

from coroweb import get, post
from models import User, Comment, Blog, Reply, next_id
from config import configs
from apis import APIValueError, APIError, APIPermissionError, APIResourceNotFoundError, Page

import re, time, json, hashlib, os
from aiohttp import web
from tools.imgruler.ruler import zoom

import logging
logging.basicConfig(level=logging.DEBUG)
 
# =====================================方法区==================================

# 用来验证管理员身份
def check_admin(request): 
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()
        
# 用来根据页码字符获得页码数字
def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

COOKIE_NAME = 'sakurasession'
_COOKIE_KEY = configs.session.secret

# 用来生成cookie的值（id-expiers-sha1）
def user2cookie(user, max_age):
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    logging.debug('this is cookie to set: %s' % '-'.join(L))
    return '-'.join(L)

# 用来解析cookie的代码
async def cookie2user(cookie_str):
    if not cookie_str: # 如果没有cookie
        return None
    try:
        L = cookie_str.split('-') # 将cookie拆解
        if len(L) != 3: # cookie格式不正确
            logging.warn('cookie format is wrong')
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time(): # 如果寿命时间小于当前时间
            logging.warn('cookie is overdue')
            return None
        user = await User.find(uid) # 获取指定用户
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY) # 制作cookie值
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

def text2html(text):
    lines = map(lambda s:'<p>%s</p>' % s.replace('&', '&amp;').replace('<','&lt;').replace('>','&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)

# 获取图片IO地址
def get_image_path(target):
    IOImage = None
    if target == 'base':
        IOImage = (configs.images['base_path'].split('/'))[1:-1]
    elif target == 'blog':
        IOImage = (configs.images['blog_path'].split('/'))[1:-1]
    elif target == 'user':
        IOImage = (configs.images['user_path'].split('/'))[1:-1]
    elif target == 'article':
        IOImage = (configs.images['article_path'].split('/'))[1:-1]
    path = IOImage[0]
    for item in IOImage[1:]:
        path = os.path.join(path, item)
    logging.debug(IOImage)
    return path

@get('/api/getting/{id}.jpg') # 图片获取api yes
async def getImage(*, id): # 获取图片
    logging.debug('Image start getting ...')
    logging.debug(id)
    path = get_image_path('article')
    file_path = os.path.join(path, str(id)+'.jpg')
    file = None
    try:
        f = open(file_path, 'rb')
        file = f.read()
    except OSError as e:
        logging.info('Image not found, use [empty.png].')
        path = os.path.join(path, 'empty.png')
        with open(path) as f:
            file = f.read()
    finally:
        if f:
            f.close()
    return file
    
@post('/api/setting') # 图片设置api yes
async def setImage(**kw):
    logging.debug('Image start setting ...')
    value = kw.get('editormd-image-file')
    filename = kw.get('image_name')
    if filename == '' or filename == None:
        logging.warn("Counld not get image name, generate new name!")
        filename = next_id()
    filename = filename + '.jpg'
    image_path = kw.get('image_path')
    if image_path == '' or image_path == None:
        image_path = 'base'
    if value.file is None:
        raise APIValueError('imgdata', 'Image data can not be empty.')
    path = get_image_path(image_path)
    path = os.path.join(path, filename) # 合成路径
    f = None
    try:
        f = open(path, 'wb')
        logging.debug('have opened file')
        with value.file:
            for line in value.file:
                f.write(line)
        if image_path == 'blog':
            logging.debug("create small version")
            zoom(get_image_path(image_path), filename, (190.0, 106.875))
    except OSError as e:
        logging.info('Image writing error.')
        return {
                'success': 0,
                'message': repr(e),
                'url': ''
                }
    finally:
        if f:
            f.close()
    return {
            'success': 1,
            'message': 'Image set successful.',
            'url': '/api/getting/' + filename
            }

# ==========================首页与用户相关============================

@get('/') # 首页 yes
async def index(request):
    logging.debug('index starting ...')
    blogs = await Blog.findAll(limit=10, orderBy='created_at desc', items=['name', 'summary', 'user_name', 'created_at', 'readers'])
    sta1 = await Blog.count(item_count=['id'], item_sum=['readers'])
    sta2 = await Comment.count(item_count=['id'])
    return {
            '__template__' : 'index.html', # 'template__'参数指定的模板文件是'test.html'，其他参数是传递给模板的数据
            'blogs' : blogs, # 博客数据
            'images' : configs.images, # 图片数据
            'sta' : {
                'articles' : sta1['COUNT(`id`)'],
                'readers' : sta1['SUM(`readers`)'],
                'comments' : sta2['COUNT(`id`)']
            } # 访问统计数据
        }

@get('/tech')
async def tech(request):
    logging.debug('tech starting ...')
    blogs = await Blog.findAll(where='priority=1', limit=15, orderBy='created_at desc', items=['name', 'summary', 'user_name', 'created_at', 'readers'])
    sta1 = await Blog.count(item_count=['id'], item_sum=['readers'])
    sta2 = await Comment.count(item_count=['id'])
    return {
        '__template__' : 'tech.html',
        'blogs' : blogs, # 博客数据
        'images' : configs.images, # 图片数据
        'sta' : {
            'articles' : sta1['COUNT(`id`)'],
            'readers' : sta1['SUM(`readers`)'],
            'comments' : sta2['COUNT(`id`)']
        } # 访问统计数据
    }

@get('/life')
async def life(request):
    logging.debug('life starting ...')
    blogs = await Blog.findAll(where='priority=2', limit=15, orderBy='created_at desc', items=['name', 'summary', 'user_name', 'created_at', 'readers'])
    sta1 = await Blog.count(item_count=['id'], item_sum=['readers'])
    sta2 = await Comment.count(item_count=['id'])
    return {
        '__template__' : 'life.html',
        'blogs' : blogs, # 博客数据
        'images' : configs.images, # 图片数据
        'sta' : {
            'articles' : sta1['COUNT(`id`)'],
            'readers' : sta1['SUM(`readers`)'],
            'comments' : sta2['COUNT(`id`)']
        } # 访问统计数据
    }

@get('/tool')
async def tool(request):
    logging.debug('life starting ...')
    return {
        '__template__' : 'tool.html',
        'images' : configs.images, # 图片数据
    }

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

@get('/register') # 用户注册页面 yes
async def register(*, backto=''):
    logging.debug('register starting...')
    return {
            '__template__' : 'register.html',
            'images' : configs.images, # 图片数据
            'backto' : backto
            }

@post('/api/users') # 用户注册api yes
async def api_register_user(*, email, name, passwd):
    logging.debug('api_register_user starting...')
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
    sha1_passwd = '%s:%s' % (uid, passwd) # 制作sha1加密口令
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    await user.save() # 保存信息到数据库
    # 制作会话cookie，用于保存用户状态：
    r = web.Response() # 建立web响应
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True) # 设置cookie
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

@get('/signin') # 用户登录页面 yes
async def signin(*, backto=''):
    logging.debug('signin starting ...')
    return {
            '__template__' : 'signin.html',
            'images' : configs.images, # 图片数据
            'backto' : backto
            }

@get('/signout') # 用户登出页面（这里跳转到其他页面） yes
async def signout(request):
    logging.debug('signout starting ...')
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True) # 设置cookie
    logging.info('user signed out.')
    return r

@post('/api/authenticate') # 用户验证api yes
async def authenticate(*, email, passwd):
    logging.debug('authenticate starting ...')
    if not email: # 如果没有邮箱
        raise APIValueError('email', 'Invalid email.') # api值异常
    if not passwd: # 如果没有密码
        raise APIValueError('passwd', 'Invalid passwd.') # api值异常
    users = await User.findAll('email=?', [email]) # 获取指定用户信息
    if len(users) == 0: # 如果没有该用户
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # 检查密码
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8')) # 插入用户id
    sha1.update(b':') # 来一个冒号
    sha1.update(passwd.encode('utf-8')) # 插入用户口令
    if user.passwd != sha1.hexdigest(): # 检查密码
        raise APIValueError('passwd', 'Invalid password.') # api值异常
    # 此时密码验证成功，设置cookie
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True) # 设置cookie
    user.passwd = '******' # 隐藏口令
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

@get('/manage/users') # 用户列表页面 yes
async def manage_users(*, page='1'):
    return {
            '__template__': 'manage_users.html',
            'page_index': get_page_index(page),
            'images' : configs.images # 图片数据
            }

@get('/api/users') # 用户获取api yes
async def api_get_users(*, page='1'):
    page_index = get_page_index(page) # 根据页码字符获取对应的页码数字
    num = await User.findNumber('count(id)') # 获取日志总数
    p = Page(num, page_index)# 根据Page类制作日志列表分页信息
    if num == 0:
        return dict(page=p, user=())
    users = await User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit), itmes=['name', 'admin', 'email', 'created_at'])
    for u in users:
        u.passwd = '******'
    return dict(page=p, users=users)

# ==================================日志相关===================================

@get('/api/blogs') # 日志列表获取api yes
async def api_blogs(*, page='1'):
    page_index = get_page_index(page) # 根据页码字符获取对应的页码数字
    num = await Blog.findNumber('count(id)') # 获取日志总数
    p = Page(num, page_index) # 根据Page类制作日志列表分页信息
    if num == 0: # 处理无条目的情况
        logging.warning('None data! Database is empty!')
        return dict(page=p, blogs=())
    blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit), items=['name','user_name', 'created_at']) # 从数据库中获取所有的博文
    return dict(page=p, blogs=blogs) # 返回数据 # ？？？直接返回如何处理该类型的数据？

@get('/manage/blogs/create') # 日志创建页面 yes
async def manage_create_blog():
    return {
            '__template__': 'manage_blog_edit.html',
            'id': next_id(),
            'new_flag' : '',
            'action': '/api/blogs',
            'images' : configs.images # 图片数据
            }

@get('/blog/{id}') # 日志页 yes
async def get_blog(id):
    blog = await Blog.find(id)
    comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    for comment in comments:
         comment.replies = await Reply.findAll('target_cmid=?', comment.id, orderBy='created_at desc', items=['user_name', 'user_id', 'target_name', 'content', 'created_at'])
    blog.readers += 1
    await blog.update()
    return {
            '__template__': 'blog.html',
            'blog': blog,
            'comments': comments,
            'images' : configs.images # 图片数据
            }

@get('/api/blogs/{id}') # 日志详情页 yes
async def api_get_blog(*, id):
    logging.debug('the blog id to find:' + id)
    blog = await Blog.find(id)
    logging.debug(blog)
    return blog

@post('/api/blogs') # 日志创建api yes
async def api_create_blog(request, *, name, summary, content, new_id, priority):
    check_admin(request) # 判断是否是管理员
    if not name or not name.strip(): # 如果没有名字
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip(): # 如果没有标题
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip(): # 如果没有内容
        raise APIValueError('content', 'content cannot be empty.')
    blog = Blog(id = new_id, user_id=request.__user__.id, user_name=request.__user__.name, name=name.strip(), summary=summary.strip(), content=content.strip(), priority=priority)
    await blog.save()
    return blog

@get('/manage/blogs') # 日志列表页面 yes
async def manage_blogs(*, page='1'):
    logging.debug('start manage_blogs')
    return {
            '__template__': 'manage_blogs.html',
            'page_index': get_page_index(page),
            'images' : configs.images # 图片数据
            }

@get('/manage/blogs/edit') # 日志修改页面 yes
async def manage_edit_blog(*, id):
    return {
            '__template__': 'manage_blog_edit.html',
            'id': id,
            'new_flag' : True,
            'action': '/api/blogs/%s' % id,
            'images' : configs.images # 图片数据
            }

@post('/api/blogs/{id}') # 日志修改api yes
async def api_update_blog(id, request, *, name, summary, content, priority):
    check_admin(request) # 检查是否是管理员
    blog = await Blog.find(id) # 查找要修改的日志数据
    if not name or not name.strip(): # 如果没有名字
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip(): # 如果没有标题
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip(): # 如果没有内容
        raise APIValueError('content', 'content cannot be empty.')
    blog.name = name.strip()
    blog.summary = summary.strip()
    blog.content = content.strip()
    blog.priority = priority
    await blog.update() # 更新数据库
    return blog

@post('/api/blogs/{id}/delete') # 日志删除api yes
async def api_delete_blog(request, *, id):
    check_admin(request) # 检查是否是管理员
    comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    for comment in comments:
        await comment.delete()
    blog = await Blog.find(id) # 查找日志数据
    await blog.delete() # 删除该日志
    path = get_image_path('blog')
    try:
        os.remove(os.path.join(path, blog.id + '.jpg'))
        os.remove(os.path.join(path, 'small_' + blog.id + '.jpg'))
    except OSError as e:
        logging.warn('os.remove() for OSError')
    return dict(id=id) # 返回被删除的日志id

# ==================================评论相关===================================

@get('/manage/comments') # 评论列表页 yes
async def manage_comment(*, page='1'):
    return {
                '__template__': 'manage_comments.html',
                'page_index': get_page_index(page),
                'images' : configs.images # 图片数据
            }
    
@get('/api/comments') # 获取评论api yes
async def api_comments(*, page='1'):
    page_index = get_page_index(page) # 根据页码字符获取对应的页码数字
    num = await Comment.findNumber('count(id)') # 获取评论总数
    p = Page(num, page_index) # 根据Page类制作日志列表分页信息
    if num == 0: # 处理没有评论
        return dict(page=p, comments=()) # 返回空结果
    comments = await Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit)) # 获取所有评论
    logging.debug(type(comments))
    for comment in comments:
        comment.replies = await Reply.findAll('target_cmid=?', comment.id, orderBy="created_at desc", items=['user_name', 'content', 'created_at'])
    return dict(page=p, comments=comments) # 返回结果

@post('/api/blogs/{id}/comments') # 创建评论api yes
async def api_create_commnent(id, request, *, content):
    logging.debug('start setting commnets')
    user = request.__user__ # 获取用户名
    if user is None: # 处理用户名为空的情况 -> 还没有登录
        raise APIPermissionError('Please signin first.')
    if not content or not content.strip(): # 处理没有内容的情况
        raise APIValueError('content')
    blog = await Blog.find(id)
    if blog is None: # 处理没有日志的情况
        raise APIResourceNotFoundError('Blog')
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name, content=text2html(content.strip()))
    await comment.save() # 储存
    logging.debug('end setting comments')
    return comment

@post('/api/comments/{id}/delete') # 删除评论api yes
async def api_delete_comments(id, request):
    check_admin(request) # 检查是否是管理员
    c = await Comment.find(id) # 查找指定评论
    if c is None: # 处理没找到的情况
        raise APIResourceNotFoundError('Comment')
    await c.delete()
    return dict(id=id)

@post('/api/comments/{id}/replies') # 创建回复api yes
async def api_create_replies(id, request, *, content, target_cmid, target_name):
    logging.debug('start setting replies')
    user = request.__user__ # 获取用户名
    logging.debug(request.__user__)
    logging.debug('the user')
    if user is None: # 处理用户名为空的情况 -> 还没有登录
        raise APIPermissionError('Please signin first.')
    if not content or not content.strip(): # 处理没有内容的情况
        raise APIValueError('content')
    comment = await Comment.find(id)
    if comment is None: # 处理没有评论的情况
        raise APIResourceNotFoundError('Comment')
    reply = Reply(user_id=user.id, user_name=user.name, content=text2html(content.strip()), target_cmid=target_cmid, target_name=target_name)
    await reply.save() # 储存
    logging.debug('end setting replies')
    return reply

@post('/api/replies/{id}/delete') # 删除回复api yes
async def api_delete_replies(id, request):
    check_admin(request) # 检查是否是管理员
    r = await Reply.find(id) # 找到指定回复
    if r is None: # 处理没有找到的情况
        raise APIResourceNotFoundError('Reply')
    await r.delete()
    return dict(id=id)