#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 00:05:23 2018

@author: Infuny
"""
from coroweb import get, post
from models import User, Blog, Comment, Reply, next_id, Books, Readers, Borrows
from config import configs
from apis import APIValueError, APIError, APIPermissionError, APIResourceNotFoundError, Page
from tools.image_ruler.ruler import zoom

from aiohttp import web
import json, time, hashlib, re, os, logging
logging.basicConfig(level=logging.DEBUG)

# 1 首页相关逻辑
# 1.1 页面请求
# 1.1.1 获取首页 index.html
@get('/')
async def index(request):
    logging.debug('[HANDLER] Handlering index.html ...')
    return {
            '__template__' : 'index.html', # 'template__'参数指定的模板文件是'test.html'，其他参数是传递给模板的数据
            }

# 1.2 API 请求
# 1.2.1 获取博客列表数据 
def get_page_index(page_str): # 将页码字符串转换为整型
    logging.debug('[HANDLER]     Handlering /api/blogs, the page_str(no convert) is: ' + page_str)
    p = 1
    try:
        p = int(page_str)
        logging.debug('[HANDLER]     Handlering /api/blogs, the page_str(have converted) is: ' + str(p))
    except:
        pass
    if p < 1:
        p = 1
    return p
    
@get('/api/blogs/{sort}') # 获取博客的简单列表，可定制
async def getBlogs(*, sort='0', page='1'):
    logging.debug('[HANDLER] Handlering /api/blogs/{sort} in index.html ...')
    where_sql = None
    limit_sql = 10
    items_sql = ['name', 'summary', 'user_name', 'created_at', 'readers']
    if sort != '0': # 全选时
        where_sql="sort=" + sort # 构造类别条件
        page = None # 不用页码对象
    else: # 按类别选取时，构造页码对象，并设置 limit 和 items
        page_index = get_page_index(page)
        logging.debug('[HANDLER]     Handlering /api/blogs/{sort}, the page_index is: ' + str(page_index))
        num = await Blog.findNumber('count(id)') # 获取条目总数
        page = Page(num, page_index, 10)
        if num == 0: # 处理无条目的情况
            logging.warning('[HANDLER]     No data! Database is empty!')
            return dict(page=page, blogs=())
        limit_sql=(page.offset, page.limit)
        items_sql = ['name','user_name', 'created_at', 'readers']
    infos = await Blog.findAll(where=where_sql, limit=limit_sql, orderBy='created_at desc', items=items_sql)
    return {
            'infos': infos, # 博客数据，不带有模板，在 app.py 内的 ResponseFactory 内会自动转换为 json
            'page': page,
            'images': configs.images
            }

# 2 用户管理相关逻辑
# 2.1 页面请求
# 2.1.1 

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

@post('/api/register') # 注册用户
async def api_register_user(*, email, name, passwd):
    logging.debug('[HANDLER] Handlering /api/users in index.html ...')
    if not name or not name.strip(): # 如果没有名字
        raise APIValueError('name', 'Invalid name') # api值异常
    if not email or not _RE_EMAIL.match(email): # 如果与邮箱re正则不匹配
        raise APIValueError('email', 'Invalid email.') # api值异常
    if not passwd or not _RE_SHA1.match(passwd): # 如果与密码re正则不匹配
        raise APIValueError('passwd', 'Invalid passwd.') # api值异常
    users = await User.findAll('email=?', [email]) # 获取数据库中指定的用户信息
    if len(users) > 0: # 如果用户中已有数据
        raise APIValueError('register failed', 'Email is already in use.') # api逻辑异常
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
@post('/api/signin') # 验证用户
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
@get('/api/signout') #（会跳转到其他页面）
async def signout(request):
    logging.debug('[HANDLERS] Handlering /aip/signout in index.html ...')
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True) # 删除 Cookie
    return r

# 3 博客相关逻辑
# 3.1 页面请求
### 3.1.1 获取博客页 blog.html
@get('/blog/{id}')
async def getBlog(id):
    logging.debug('[HANDLER] Handlering blog.html ...')
    blog = await Blog.find(id)
    '''
    comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    for comment in comments:
         comment.replies = await Reply.findAll('target_cmid=?', comment.id, orderBy='created_at desc', items=['user_name', 'user_id', 'target_name', 'content', 'created_at'])
    '''
    blog.readers += 1
    await blog.update()
    return {
            '__template__': 'blog.html',
            'blog_name': blog.name,
            'blog_id': blog.id
            }
    
### 3.1.2 获取博客创建页 manage_blog_edit.html
@get('/manage/blog/new')
async def getBlogNew():
    logging.debug('[HANDLER] Handlering (new) manage_blog_edit.html ...')
    return {
            '__template__': 'manage_blog_edit.html',
            'blog_name': '新建',
            'blog_id': '',
            'images' : configs.images,
            'isNew': True
            }

### 3.1.3 获取博客编辑页 manage_blog_edit.html
@get('/manage/blog/edit/{id}')
async def getBlogEdit(id):
    logging.debug('[HANDLER] Handlering (edit) manage_blog_edit.html ...')
    blog = await Blog.find(id)
    return {
            '__template__': 'manage_blog_edit.html',
            'blog_name': blog.name,
            'blog_id': blog.id,
            'blog': blog,
            'images' : configs.images,
            'isNew': False
            }

# 3.2 API 请求
# 3.2.1 博客数据传输
@get('/api/blog/{id}')
async def getBlogData(id):
    logging.debug('[HANDLERS] Handlering /aip/blog/{id} in index.html ...')
    blog = await Blog.find(id)
    comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    for comment in comments:
         comment.replies = await Reply.findAll('target_cmid=?', comment.id, orderBy='created_at desc', items=['user_name', 'user_id', 'target_name', 'content', 'created_at'])
    return {
            'blog_data': blog,
            'comment_data': comments,
            'images' : configs.images
            }
    
### 3.2.2 新增博客数据
def get_image_path(target): # 图片 IO 位置路径处理（主要是避免不同的系统的路径符问题）
    IOImage = None
    if target == 'base':
        IOImage = (configs.images['base_path'].split('/'))[1:-1]
    elif target == 'blog':
        IOImage = (configs.images['blog_path'].split('/'))[1:-1]
    elif target == 'user':
        IOImage = (configs.images['user_path'].split('/'))[1:-1]
    elif target == 'art':
        IOImage = (configs.images['article_path'].split('/'))[1:-1]
    path = IOImage[0]
    for item in IOImage[1:]:
        path = os.path.join(path, item)
    logging.debug(IOImage)
    return path

async def saveImage(img_name=None, img_data=None, target='base'): # 存储图片
    logging.debug('[HANDLERS]     Saving image ...')
    if img_name == None: # 检查图片名
        logging.info("[HANDLERS]     Counld not get image name, generate new name.")
        img_name = next_id() + '.jpg'
    if img_data is None: # 检查图片数据
        raise APIValueError('imgdata', 'image data can not be empty.')
    img_path = get_image_path(target) # 合成路径
    save_path = os.path.join(img_path, img_name) # 合成路径
    fileWriter = None
    try:
        logging.debug('[HANDLERS]     Opene file ' + save_path)
        fileWriter = open(save_path, 'wb')
        with img_data:
            for line in img_data:
                fileWriter.write(line)
        if target == 'blog':
            logging.debug("[HANDLERS]     Create a small version of the image.")
            zoom(img_path, img_name, (192, 108))
    except OSError as e:
        logging.warn('[HANDLERS]     Image writing error: ' + repr(e))
        return repr(e)
    finally:
        if fileWriter:
            fileWriter.close()
        return True
    
@post('/api/blog/new') # 新增博客，存储数据和图片
async def createBlogData(request, *, name, summary, content, sort, file):
    logging.debug('[HANDLERS] Handlering /aip/blog/new in manage_blog_edit.html ...')
    check_admin(request) # 检查是否是管理员
    if not name or not name.strip(): # 如果没有名字
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip(): # 如果没有标题
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip(): # 如果没有内容
        raise APIValueError('content', 'content cannot be empty.')
    # 创建博客
    blog = Blog(id = next_id(), user_id=request.__user__.id, user_name=request.__user__.name, name=name.strip(), summary=summary.strip(), content=content, sort=sort)
    logging.debug('[HANDLERS]     Update blog before save image.')
    await blog.save()
    # 存储图片
    logging.debug('[HANDLERS]     Type of variable file: ' + str(type(file)))
    if file != '' and file!=None:
        img_name = blog.id + '.jpg'
        img_data = file.file
        await saveImage(img_name, img_data, 'blog')
    return blog

@post('/api/blog/img') ### 存储 markdown 图片数据
async def saveMdImage(**kw):
    logging.debug('[HANDLERS] Handlering /aip/blog/img in manage_blog_edit.html ...')
    img_name = next_id() + '.jpg' # 图片名
    img_data = kw.get('editormd-image-file').file # 图片数据
    if img_data is None:
        raise APIValueError('imgdata', 'Image data can not be empty.')
    status = await saveImage(img_name, img_data, 'art')
    if status == True:
        return {
                'success': 1,
                'message': 'Image set successful.',
                'url': configs.images['article_path'] + img_name
                }
    else:
        return {
                'success': 0,
                'message': status,
                'url': ''
                }
        
# 3.2.3 修改博客数据
@post('/api/blog/edit/{id}')
async def editBlogData(id, request, *, name, summary, content, sort, file):
    logging.debug('[HANDLERS] Handlering /aip/blog/edit/{id} in manage_article.html ...')
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
    blog.sort = sort
    logging.debug('[HANDLERS]     Update blog before save image.')
    await blog.update() # 更新数据库
    # 存储图片
    logging.debug('[HANDLERS]     Type of variable file: ' + str(type(file)))
    if file != '' and file!=None:
        img_name = blog.id + '.jpg'
        img_data = file.file
        await saveImage(img_name, img_data, 'blog')
    return blog

# 3.2.4 删除博客数据
@get('/api/blog/del/{id}')
async def delBlogData(request, *, id):
    logging.debug('[HANDLERS] Handlering /aip/blog/del/{id} in manage_article.html ...')
    check_admin(request) # 检查是否是管理员
    comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    for comment in comments:
        await comment.delete()
    blog = await Blog.find(id) # 查找日志数据
    path = get_image_path('blog') # 删除图片
    try:
        os.remove(os.path.join(path, blog.id + '.jpg'))
        os.remove(os.path.join(path, 'imgS_' + blog.id + '.jpg'))
    except OSError as e:
        logging.warn('[HANDLERS] Handlering /aip/blog/del/{id}, while ' + repr(e))
    await blog.delete() # 删除该日志
    return dict(id=id) # 返回被删除的日志id

# 4 工具相关逻辑
    
## 4.1 基本方法
### 4.1.1 页面获取
@get('/tool') # 工具页面获取
async def tool():
    logging.debug('[HANDLER] Handlering ??.html(now is undefined) ...')
    return {
            'images': configs.images
            }
    
    
    
## 4.2 图书数据库管理系统
### 4.2.1 页面获取
@get('/tool/library') # 报告页 tool_library.report.html
async def tool_libaray_index():
    logging.debug('[HANDLER] Handlering tool_library_index.html ...')
    return {
            '__template__': 'tool_library_index.html' # redirect to index without blogs
            }

@get('/tool/library/index') # 报告页 tool_library.report.html - 请求方式2
async def tool_libaray_index2():
    logging.debug('[HANDLER] Handlering tool_library_index.html ...')
    return {
            '__template__': 'tool_library_index.html' # redirect to index without blogs
            }
    
@get('/tool/library/report') # 报告页 tool_library.report.html
async def tool_libaray_report():
    logging.debug('[HANDLER] Handlering tool_library_report.html ...')
    book_count = await Books.count(item_count=['bid'])
    reader_count= await Readers.count(item_count=['rid'])
    borrow_count = await Borrows.count(item_count=['id'])
    return {
            'book_count': book_count[0]['COUNT(`bid`)'],
            'reader_count': reader_count[0]['COUNT(`rid`)'],
            'borrow_count': borrow_count[0]['COUNT(`id`)'],
            '__template__': 'tool_library_report.html'
            }

    # 图书页面

@get('/tool/library/books') # 图书页 tool_library_books.html
async def tool_library_books():
    logging.debug('[HANDLER] Handlering tool_library_books.html ...')
    return {
            '__template__': 'tool_library_books.html',
            
            }

@get('/manage/tool/book/new') # 获取图书创建页 manage_tool_book_new.html
async def getToolBookNew():
    logging.debug('[HANDLER] Handlering (new) manage_tool_book_edit.html ...')
    return {
            '__template__': 'manage_tool_book_edit.html',
            'book_title': '新建',
            'book_bid': '',
            'isNew': True
            }

@get('/manage/tool/book/edit/{bid}') # 获取图书编辑页 manage_tool_book_edit.html
async def getToolBookEdit(bid):
    logging.debug('[HANDLER] Handlering (edit) manage_tool_book_edit.html ...')
    book = await Books.find(bid)
    return {
            '__template__': 'manage_tool_book_edit.html',
            'book_title': book.btitle,
            'book_bid': book.bid,
            'book': book,
            'isNew': False
            }
    
    # 用户页面
    
@get('/tool/library/readers') # 用户页 tool_library_readers.html
async def tool_library_readers():
    logging.debug('[HANDLER] Handlering tool_library_readers.html ...')
    return {
            '__template__': 'tool_library_readers.html',
            
            }

@get('/manage/tool/reader/new') # 获取用户创建页 manage_tool_reader_new.html
async def getToolReaderNew():
    logging.debug('[HANDLER] Handlering (new) manage_tool_reader_edit.html ...')
    return {
            '__template__': 'manage_tool_reader_edit.html',
            'reader_name': '新建',
            'reader_rid': '',
            'isNew': True
            }

@get('/manage/tool/reader/edit/{rid}') # 获取用户编辑页 manage_tool_reader_edit.html
async def getToolReaderEdit(rid):
    logging.debug('[HANDLER] Handlering (edit) manage_tool_reader_edit.html ...')
    reader = await Readers.find(rid)
    return {
            '__template__': 'manage_tool_reader_edit.html',
            'reader_name': reader.rname,
            'reader_rid': reader.rid,
            'reader': reader,
            'isNew': False
            }
    
    # 借书表页面
    
@get('/tool/library/borrows') # 借书表页 tool_library_borrows.html
async def tool_library_Borrowrs():
    logging.debug('[HANDLER] Handlering tool_library_borrowrs.html ...')
    return {
            '__template__': 'tool_library_borrows.html',
            
            }

@get('/manage/tool/borrow/new') # 获取借书表创建页 manage_tool_borrow_new.html
async def getToolBorrowNew():
    logging.debug('[HANDLER] Handlering (new) manage_tool_borrow_edit.html ...')
    return {
            '__template__': 'manage_tool_borrow_edit.html',
            'borrow_name': '新建',
            'borrow_id': '',
            'isNew': True
            }

@get('/manage/tool/borrow/edit/{id}') # 获取借书表编辑页 manage_tool_borrow_edit.html
async def getToolBorrowEdit(id):
    logging.debug('[HANDLER] Handlering (edit) manage_tool_borrow_edit.html ...')
    borrow = await Borrows.find(id)
    return {
            '__template__': 'manage_tool_borrow_edit.html',
            'borrow_name': '编辑借书记录',
            'borrow_id': borrow.id,
            'borrow': borrow,
            'isNew': False
            }

    # 数据分析页面
    
@get('/tool/library/data_analysis')
async def getToolLibraryData():
    logging.debug('[HANDLER] Handlering tool_library_data_analysis.html ...')
    booksSort = await Books.count(items=[('bsort', 'name')], item_count=[('bid', 'value')], alias=True, groupBy='bsort')
    booksBread_times = await Books.count(items=[('btitle', 'name'), ('bread_times', 'value')], alias=True)
    borrow_time = await Borrows.count(items=[('bborrow_time', 'name')], item_count=[('id', 'value')], alias=True, groupBy='bborrow_time')
    borrow_time = sorted(borrow_time, key=lambda x: x['name'])
    return {
            'booksSort': booksSort,
            'booksRead_times': booksBread_times,
            'borrowsBorrow_time': borrow_time,
            'borrowsBorrow_time1': [x['name'] for x in borrow_time ],
            'borrowsBorrow_time2': [x['value'] for x in borrow_time ],
            '__template__': 'tool_library_data_analysis.html'
            }

### 4.2.2 API 请求
    
    # 图书 API
    
@get('/api/tool/books/{bsort}') # 获取图书列表
async def getBooks(*, key='', value='', orderby='', bsort='0', page='1'):
    logging.debug('[HANDLER] Handlering /api/tool/books/{bsort} in tool_library_books.html ...')
    where_sql = None
    if key != '' and value != '':
        where_sql = key + "='" + value + "'"
    if orderby == '' or orderby == ' ':
        orderby='bpublished_at desc'
    limit_sql = 8
    items_sql = ['btitle', 'bauthor', 'bpublisher', 'bpublished_at', 'bsort', 'bexits', 'bread_times']
    if bsort != '0': # 全选时
        where_sql="bsort=" + bsort # 构造类别条件
        page = None # 不用页码对象
    else: # 按类别选取时，构造页码对象，并设置 limit 和 items
        page_index = get_page_index(page)
        logging.debug('[HANDLER]     Handlering /api/tool/books/{bsort}, the page_index is: ' + str(page_index))
        num = await Books.findNumber('count(bid)') # 获取条目总数
        page = Page(num, page_index, 10)
        if num == 0: # 处理无条目的情况
            logging.warning('[HANDLER]     No data! Database is empty!')
            return dict(page=page, books=())
        limit_sql=(page.offset, page.limit)
    infos = await Books.findAll(where=where_sql, limit=limit_sql, orderBy=orderby, items=items_sql)
    return {
            'infos': infos, # 图书数据，不带有模板，在 app.py 内的 ResponseFactory 内会自动转换为 json
            'page': page
            }
    
@post('/api/tool/book/new') # 新增图书
async def createBookData(request, *, btitle, bauthor, bpublisher, bpublished_at, bsort, bexits, bread_times):
    logging.debug('[HANDLERS] Handlering /aip/tool/book/new in manage_tool_book_edit.html ...')
    check_admin(request) # 检查是否是管理员
    if not btitle or not btitle.strip(): # 如果没有名字
        raise APIValueError('name', 'name cannot be empty.')
    if not bauthor or not bauthor.strip(): # 如果没有标题
        raise APIValueError('summary', 'summary cannot be empty.')
    if not bpublisher or not bpublisher.strip(): # 如果没有内容
        raise APIValueError('content', 'content cannot be empty.')
    # 创建图书
    book = Books(bid = next_id(), btitle=btitle.strip(), bauthor=bauthor.strip(), bpublisher=bpublisher, bpublished_at=bpublished_at, bsort=bsort, bexits=bexits, bread_times=bread_times)
    await book.save()
    return book
    
@post('/api/tool/book/edit/{bid}') # 修改图书数据
async def editBookData(bid, request, *, btitle, bauthor, bpublisher, bpublished_at, bsort, bexits, bread_times):
    logging.debug('[HANDLERS] Handlering /aip/tool/book/edit/{id} in tool_library_books.html ...')
    check_admin(request) # 检查是否是管理员
    book = await Books.find(bid) # 查找要修改的图书数据
    if not btitle or not btitle.strip(): # 如果没有书名
        raise APIValueError('name', 'name cannot be empty.')
    if not bauthor or not bauthor.strip(): # 如果没有作者
        raise APIValueError('summary', 'summary cannot be empty.')
    if not bpublisher or not bpublisher.strip(): # 如果没有出版社
        raise APIValueError('content', 'content cannot be empty.')
    book.btitle = btitle.strip()
    book.bauthor = bauthor.strip()
    book.bpublisher = bpublisher.strip()
    book.bpublished_at = bpublished_at
    book.bsort = bsort
    book.bexits = bexits
    book.bread_times=bread_times
    await book.update() # 更新数据库
    return book

@get('/api/tool/book/del/{bid}') # 删除图书数据
async def delBookData(request, *, bid):
    logging.debug('[HANDLERS] Handlering /api/tool/book/del/{id} in tool_library_books.html ...')
    check_admin(request) # 检查是否是管理员
    book = await Books.find(bid) # 查找图书数据
    await book.delete() # 删除该图书
    return dict(bid=bid) # 返回被删除的图书bid
    
    # 用户 API

@get('/api/tool/readers/{rsort}') # 获取用户列表
async def getReader(*, key='', value='', orderby='', rsort='0', page='1'):
    logging.debug('[HANDLER] Handlering /api/tool/readers/{rsort} in tool_library_readers.html ...')
    where_sql = None
    if key != '' and value != '':
        where_sql = key + "='" + value + "'"
    if orderby == '' or orderby == ' ':
        orderby='radmin desc'
    limit_sql = 8
    items_sql = ['rname', 'rsex', 'remail', 'rrole', 'radmin']
    if rsort != '0': # 全选时
        where_sql="rsort=" + rsort # 构造类别条件
        page = None # 不用页码对象
    else: # 按类别选取时，构造页码对象，并设置 limit 和 items
        page_index = get_page_index(page)
        logging.debug('[HANDLER]     Handlering /api/tool/readers/{rsort}, the page_index is: ' + str(page_index))
        num = await Readers.findNumber('count(rid)') # 获取条目总数
        page = Page(num, page_index, 10)
        if num == 0: # 处理无条目的情况
            logging.warning('[HANDLER]     No data! Database is empty!')
            return dict(page=page, readers=())
        limit_sql=(page.offset, page.limit)
    infos = await Readers.findAll(where=where_sql, limit=limit_sql, orderBy=orderby, items=items_sql)
    return {
            'infos': infos, # 用户数据，不带有模板，在 app.py 内的 ResponseFactory 内会自动转换为 json
            'page': page
            }

@post('/api/tool/reader/new') # 新增用户
async def createReaderData(request, *, rname, rsex, remail, rrole, radmin):
    logging.debug('[HANDLERS] Handlering /aip/tool/reader/new in manage_tool_reader_edit.html ...')
    check_admin(request) # 检查是否是管理员
    if not rname or not rname.strip(): # 如果没有名字
        raise APIValueError('name', 'name cannot be empty.')
    if not rsex or not rsex.strip(): # 如果没有性别
        raise APIValueError('summary', 'summary cannot be empty.')
    if not remail or not remail.strip(): # 如果没有邮箱
        raise APIValueError('content', 'content cannot be empty.')
    # 创建图书
    reader = Readers(rid = next_id(), rname=rname.strip(), rsex=rsex.strip(), remail=remail, rrole=rrole, radmin=radmin)
    await reader.save()
    return reader
    
@post('/api/tool/reader/edit/{rid}') # 修改用户数据
async def editReaderData(rid, request, *, rname, rsex, remail, rrole, radmin):
    logging.debug('[HANDLERS] Handlering /aip/tool/reader/edit/{rid} in tool_library_readers.html ...')
    check_admin(request) # 检查是否是管理员
    reader = await Readers.find(rid) # 查找要修改的用户数据
    if not rname or not rname.strip(): # 如果没有名字
        raise APIValueError('name', 'name cannot be empty.')
    if not rsex or not rsex.strip(): # 如果没有性别
        raise APIValueError('summary', 'summary cannot be empty.')
    if not remail or not remail.strip(): # 如果没有邮箱
        raise APIValueError('content', 'content cannot be empty.')
    reader.rname = rname.strip()
    reader.rsex = rsex.strip()
    reader.remail = remail.strip()
    reader.rrole = rrole
    reader.radmin = radmin
    await reader.update() # 更新数据库
    return reader

@get('/api/tool/reader/del/{rid}') # 删除用户数据
async def delReaderData(request, *, rid):
    logging.debug('[HANDLERS] Handlering /api/tool/reader/del/{rid} in tool_library_readers.html ...')
    check_admin(request) # 检查是否是管理员
    reader = await Readers.find(rid) # 查找用户数据
    await reader.delete() # 删除该用户
    return dict(rid=rid) # 返回被删除的用户rid

    # 借书表 API
    
@get('/api/tool/borrows/{sort}') # 获取借书表列表
async def getBorrow(*, key='', value='', orderby='', sort='0', page='1'):
    logging.debug('[HANDLER] Handlering /api/tool/borrows/{sort} in tool_library_borrows.html ...')
    where_sql = None
    if key != '' and value != '':
        where_sql = key + "='" + value + "'"
    if orderby == '' or orderby == ' ':
        orderby='bborrow_time desc'
    limit_sql = 8
    #items_sql = ['rid', 'bid', 'bborrow_time', 'bdue_time', 'breturn_time', 'bcomment']
    items_sql = None
    if sort != '0': # 全选时
        where_sql="sort=" + sort # 构造类别条件
        page = None # 不用页码对象
    else: # 按类别选取时，构造页码对象，并设置 limit 和 items
        page_index = get_page_index(page)
        logging.debug('[HANDLER]     Handlering /api/tool/borrows/{sort}, the page_index is: ' + str(page_index))
        num = await Borrows.findNumber('count(id)') # 获取条目总数
        page = Page(num, page_index, 10)
        if num == 0: # 处理无条目的情况
            logging.warning('[HANDLER]     No data! Database is empty!')
            return dict(page=page, borrows=())
        limit_sql=(page.offset, page.limit)
    infos = await Borrows.findAllFromView(where=where_sql, view='library_view1', limit=limit_sql, orderBy=orderby, items=items_sql)
    return {
            'infos': infos, # 借书表数据，不带有模板，在 app.py 内的 ResponseFactory 内会自动转换为 json
            'page': page
            }

@post('/api/tool/borrow/new') # 新增借书记录
async def createBorrowData(request, *, rid, bid, bborrow_time, bdue_time, breturn_time, bcomment):
    logging.debug('[HANDLERS] Handlering /aip/tool/borrow/new in manage_tool_borrow_edit.html ...')
    check_admin(request) # 检查是否是管理员
    if not rid or not rid.strip(): # 如果没有名字
        raise APIValueError('name', 'name cannot be empty.')
    if not bid or not bid.strip(): # 如果没有性别
        raise APIValueError('summary', 'summary cannot be empty.')
    if not bborrow_time or not bborrow_time.strip(): # 如果没有邮箱
        raise APIValueError('content', 'content cannot be empty.')
    # 创建图书
    borrow = Borrows(id = next_id(), rid=rid.strip(), bid=bid.strip(), bborrow_time=bborrow_time, bdue_time=bdue_time, breturn_time=breturn_time, bcomment=bcomment.strip())
    await borrow.save()
    return borrow

@post('/api/tool/borrow/edit/{id}') # 修改借书数据
async def editBorrowData(id, request, *, rid, bid, bborrow_time, bdue_time, breturn_time, bcomment):
    logging.debug('[HANDLERS] Handlering /aip/tool/borrow/edit/{id} in manage_tool_borrow_edit.html ...')
    check_admin(request) # 检查是否是管理员
    borrow = await Borrows.find(id) # 查找要修改的用户数据
    if not rid or not rid.strip(): # 如果没有名字
        raise APIValueError('name', 'name cannot be empty.')
    if not bid or not bid.strip(): # 如果没有性别
        raise APIValueError('summary', 'summary cannot be empty.')
    if not bborrow_time or not bborrow_time.strip(): # 如果没有邮箱
        raise APIValueError('content', 'content cannot be empty.')
    borrow.rid=rid.strip()
    borrow.bid=bid.strip()
    borrow.bborrow_time=bborrow_time
    borrow.bdue_time=bdue_time
    borrow.breturn_time, =  breturn_time,
    borrow.bcomment = bcomment
    await borrow.update() # 更新数据库
    return borrow

@get('/api/tool/borrow/del/{id}') # 删除借书数据
async def delBorrowData(request, *, id):
    logging.debug('[HANDLERS] Handlering /api/tool/borrow/del/{id} in tool_library_borrows.html ...')
    check_admin(request) # 检查是否是管理员
    borrow = await Borrows.find(id) # 查找借书数据
    await borrow.delete() # 删除该借书记录
    return dict(id=id) # 返回被删除的借书id


    # 数据分析 API
    


# 5 后台管理相关
## 5.1 页面请求
### 5.1.1 获取后台管理页 manage.html
@get('/manage/article')
async def manage():
    logging.debug('[HANDLER] Handlering manage.html ...')
    return {
            '__template__': 'manage_article.html'
            }
    
## 5.2 API 请求
def check_admin(request):  # 验证管理员身份
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()