#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 08:57:37 2018

@author: Infuny

Default configurations.
"""

__author__ = 'Infuny'

configs = {
        'db' : {
                'host' : '127.0.0.1',
                'port' : 3306,
                'user' : 'admin',
                'password' : 'admin',
                'database' : 'database'
                },
        'session' : {
                'secret' : 'sakura'
                },
        'images' : {
                'base_path' : '/static/images/',
                'blog_path' : '/static/images/blog_images/',
                'user_path' : '/static/images/user_images/',
                'article_path' : '/static/images/article_images/',
                'tool_path' : '/static/images/tool_images/'
                }
        }