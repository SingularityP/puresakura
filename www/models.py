#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Models for user, blog, comment.
"""

__author__ = 'Infuny'

import time, uuid # 导入时间模块和唯一标识模块

from orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField # 导入orm相关类

# 模型设计 - 唯一id函数
def next_id(): # 获取唯一ID
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex) # 制作并返回唯一ID

'''
此处缺省值的设置非常巧妙，在编写orm时，
给一个Field增加一个default参数可以让ORM自己填入缺省值，非常方便。
并且，缺省值可以作为函数对象传入，在调用save()时自动计算。
'''

# 模型设计 - 用户模型
class User(Model): # 定义用户模型
    __table__ =  'users'
    
    id = StringField(primary_key=True, default=next_id, column_type='varchar(50)') # 用户id
    email = StringField(column_type='varchar(50)') # 邮箱地址
    passwd = StringField(column_type='varchar(50)') # 密码
    admin = BooleanField() # 管理员标识
    name = StringField(column_type='varchar(50)') # 用户名称
    created_at = FloatField(default=time.time) # 账号注册时间
   
# 模型设计 - 博客模型
class Blog(Model): # 定义博客模型
    __table__ = 'blogs'
    
    id = StringField(primary_key=True, default=next_id, column_type='varchar(50)') # 博客id
    user_id = StringField(column_type='varchar(50)') # 博客所属的用户id
    user_name = StringField(column_type='varchar(50)') # 博客所属的用户名称
    name = StringField(column_type='varchar(50)') # 博客名称
    summary = StringField(column_type='varchar(200)') # 博客摘要
    content = TextField() # 博客正文
    created_at = FloatField(default=time.time) # 博客创建时间
    readers = IntegerField() # 博客阅读量
    sort = IntegerField() # 博客类别
    
# 模型设计 - 评论模型
class Comment(Model): # 评论模型
    __table__ = 'comments'
    
    id = StringField(primary_key=True, default=next_id, column_type='varchar(50)') # 评论id
    blog_id = StringField(column_type='varchar(50)') # 所属博客id
    user_id = StringField(column_type='varchar(50)') # 所属用户id
    user_name = StringField(column_type='varchar(50)') # 所属用户名称
    content = TextField() # 评论正文
    created_at = FloatField(default=time.time) # 评论创建时间

# 模型设计 - 回复模型
class Reply(Model): # 回复模型
    __table__ = 'replies'
    
    id = StringField(primary_key=True, default=next_id, column_type='varchar(50)') # 回复id
    user_id = StringField(column_type='varchar(50)') # 所属用户id
    user_name = StringField(column_type='varchar(50)') # 所属用户名称
    target_cmid = StringField(column_type='varchar(50)') # 目标评论id
    target_name = StringField(column_type='varchar(50)') # 目标用户名称
    content = TextField() # 回复正文
    created_at = FloatField(default=time.time) # 回复创建时间