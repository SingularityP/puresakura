#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Infuny'

import asyncio, logging, aiomysql
logging.basicConfig(level=logging.DEBUG) # 设置调试等级

def log(sql, args=()): # 对logging.info的封装，目的是方便输出sql语句
    logging.info('[SQL]: %s' % sql)

# 连接池管理
@asyncio.coroutine
def create_pool(loop, **kw): # 创建连接池
    logging.info('[ORM] Create database connection pool ...') # 记录日志
    global __pool # 声明连接池变量为全局的
    __pool = yield from aiomysql.create_pool( # 异步IO建立连接池
            host=kw.get('host', 'localhost'),
            port=kw.get('port', 3306),
            user=kw['user'],
            password=kw['password'],
            db=kw['database'],
            charset=kw.get('charset', 'utf8'),
            autocommit=kw.get('autocommit', True),
            maxsize=kw.get('maxsize', 10),
            minsize=kw.get('minsize', 1),
            loop=loop
            )
    
@asyncio.coroutine
def close_pool(): # 关闭连接池
    logging.info('[ORM] Close database connection pool ...') # 记录日志
    global __pool
    __pool.close()
    yield from __pool.wait_closed()
    
# 封装数据库操作指令
@asyncio.coroutine
def select(sql, args, size=None): # SELECT语句封装
    log(sql, args) # 记录日志
    global __pool # 声明连接池全局变量
    with (yield from __pool) as conn: # 异步获取一个连接
        cur = yield from conn.cursor(aiomysql.DictCursor) # 获取数据库游标，默认游标返回字典
        yield from cur.execute(sql.replace('?', '%s'), args or ()) # 执行select语句，用参数替换占位符'?'或'%s'
        if size: # 视情况获取定量数据
            rs = yield from cur.fetchmany(size)
        else:
            rs = yield from cur.fetchall()
        yield from cur.close() # 关闭指针
        logging.info('[ORM]     rows return: %s' % len(rs)) # 记录日志
        return rs # 返回数据

@asyncio.coroutine
def execute(sql, args): # INSERT, UPDATE, DELETE语句封装
    log(sql) # 记录日志
    with (yield from __pool) as conn: # 异步获取一个连接
        try:
            cur = yield from conn.cursor() # 获取指针
            yield from cur.execute(sql.replace('?', '%s'), args) # 执行execute语句，用参数替换占位符
            affected = cur.rowcount # 获取结果数
            yield from cur.close() # 关闭指针
            logging.info('[ORM]     rows affected: %s' % affected) # 记录日志
        except BaseException as e: # 处理异常
            logging.error("[ORM] " + str(e))
        return affected # 返回结果数

# orm顶层设计 - 辅助函数
def create_args_string(num): # 创建拥有若干个占位符的字符串
    L = []
    for n in range(num):
        L.append('?')
    return ','.join(L)

# orm顶层设计 - 字段类
class Field(object): # 定义属性类的基类

    def __init__(self, name, column_type, primary_key, default): # 定义构造方法
        self.name = name # 字段名称
        self.column_type = column_type # 字段映射的数据类型
        self.primary_key = primary_key # 字段主键标识
        self.default = default # 字段默认值

    def __str__(self): # 定制print输出功能
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)
    
class StringField(Field): # 定义字符串-字段类
    
    def __init__(self, name=None, primary_key=False, default='', column_type='varchar(100)'): # 定义构造方法
        super().__init__(name, column_type, primary_key, default) # 使用父类构造方法   

class IntegerField(Field): # 定义整型-字段类
    
    def __init__(self, name=None, primary_key=False, default=0, column_type='integer(20)'): # 定义构造方法
        super().__init__(name, column_type, primary_key, default) # 使用父类构造方法
        
class FloatField(Field): # 定义浮点型-字段类
    
    def __init__(self, name=None, primary_key=False, default=0.0, column_type='double(20,10)'):
        super().__init__(name, column_type, primary_key, default)
        
class BooleanField(Field): # 定义布尔型-字段类
    
    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)
        
class TextField(Field): # 定义文本类型-字段类
    
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)

# orm顶层设计 - 模型元类，用于定制表的映射
class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs): # 定制类构造方式
        # 排除Model类本身的情况
        if name=='Model': # cls-当前类对象指针；name-类名称；bases-继承集合；attrs-方法属性集合
            return type.__new__(cls, name, bases, attrs) # 构造并返回实例对象
        # 获取table的名称，若无，使用类名
        tableName = attrs.get('__table__', None) or name
        logging.info('[ORM] Found model: %s (table: %s)' % (name, tableName)) # 记录日志
        # 用于获取所用的 field 和主键名(mappings = fields + primaryKey)
        mappings = dict() # 所有的 属性-列 映射
        fields = [] # 非主键的 属性名 集合
        primaryKey = None # 主键标识，记录当前表是否已经设置了主键
        for k, v in attrs.items(): # 遍历attrs，items返回属性名和数值的键值对，每一个属性是指上面的字段类实例
            if isinstance(v, Field): # 处理属性（列）内容
                logging.info('[ORM]     found mapping: %s ==> %s' % (k,v)) # 记录日志
                mappings[k] = v # 放入mappings中
                if v.primary_key: # 处理主键情况
                    if primaryKey: # 已有主键
                        raise RuntimeError('Duplicate primary key for field: %s' % k) # 抛出多主键异常
                    primaryKey = k # 没有主键，标记当前主键
                else:
                    fields.append(k) # 不是主键，放入到fileds中
        if not primaryKey: # 处理没有主键的情况
            raise RuntimeError('Primary key not found.') # 抛出无主键异常
        # 建立属性-列映射
        for k in mappings.keys(): # 遍历属性集合
            attrs.pop(k) # 删除attrs中的表格相关属性，因为已经添加到 mappings 里面
        escaped_fields = list(map(lambda f:'`%s`' % f, fields)) # 生成新形式的fields，用于规避sql关键字冲突
        attrs['__mappings__'] = mappings # 保存属性和列的映射关系
        attrs['__table__'] = tableName # 保存表名称
        attrs['__primary_key__'] = primaryKey # 保存主键属性名
        attrs['__fields__'] = fields # 保存非主键属性名
        # 构造默认的SELECT, INSERT, UPDATE, DELETE语句（其中的反引号``是为了避免与sql的关键字冲突）
        attrs['__select__'] = 'SELECT `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'INSERT INTO `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields)+1))
        attrs['__update__'] = 'UPDATE `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'DELETE FROM `%s` where `%s`=?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs) # 构造并返回实例对象

# orm顶层设计 - 模型基类，表映射的基类
class Model(dict, metaclass=ModelMetaclass): 
    
    def __init__(self, **kw):   # 定义初始化方法
        super(Model, self).__init__(**kw) # 使用代理对象将方法调用委托给父类或兄弟类类型
        # 以上代码等价于：super().__init__(**kw)

    def __getattr__(self, key): # 定制属性引用默认处理方法
        try:
            return self[key] # 尝试字典方式查找(由于此方法是从dict继承下来的，可以直接以dict的方式应用)
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key) # 抛出属性调用异常

    def __setattr__(self, key, value): # 定制属性赋值默认处理方法
        self[key] = value # 由于此方法是从dict继承下来的，可以直接以dict的方式应用
        
    def getValue(self, key): # 定义带默认值的属性获取方法
        return getattr(self, key, None) # 调用dir辅助函数——getattr()，也会走__getattr__，但指定了默认值，不会抛出错误
    
    def getValueOrDefault(self, key): # 定义可带自定义默认值的属性获取方法
        value = getattr(self, key, None) # 调用dir辅助函数——getattr()
        if value is None: # 处理获取失败的情况
            field = self.__mappings__[key] # 从属性列表中获取该属性的字段类实例
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default # 优先使用调用自定义默认值函数，否则使用自带默认值属性
                logging.debug('[ORM] Using default value for %s: %s' % (key, str(value))) # 记录日志
                setattr(self, key, value) # 添加该属性，使用默认值
        return value # 返回值
    
    @classmethod
    @asyncio.coroutine
    def find(cls, pk): # 定义类方法 - 主键查找
        'find object by primary key.'
        rs = yield from select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs)==0:
            return None
        return cls(**rs[0]) # 建立并返回当前类实例
    
    @classmethod # 类方法装饰器
    @asyncio.coroutine
    def findAll(cls, where=None, args=None, **kw): # 获取表中所有符合的数据
        'find objects by where clause.'
        sql = None
        items = kw.get('items', None)
        if items is None:
            sql = [cls.__select__] # 获取基本的select语句
        else:
            sql = ['SELECT `%s`, %s FROM `%s`' % (cls.__primary_key__, ','.join(list(map(lambda f: '`%s`' % f, items))), cls.__table__)]
        if where: # 处理where条件
            sql.append('WHERE') # 语句
            sql.append(where) # 条件
        if args is None: # 处理空参数的情况
            args=[] # 使用空列表
        orderBy = kw.get('orderBy', None) # 获取排序参数
        if orderBy: # 如果要求排序
            sql.append('ORDER BY') # # 语句
            sql.append(orderBy) # 条件
        limit = kw.get('limit', None) # 获取限制参数
        if limit is not None: # 如果有限制
            sql.append('LIMIT')
            if isinstance(limit, int): # 处理限制参数的整数输入
                sql.append('?') # 语句
                args.append(limit) # 条件
            elif isinstance(limit, tuple) and len(limit) == 2: # 处理限制参数的二元组输入
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invaild limit value: %s' % str(limit))
        rs = yield from select(' '.join(sql), args)
        return [cls(**r) for r in rs] # 建立并返回当前类实例
                
    @classmethod
    @asyncio.coroutine
    def findNumber(cls, selectField, where=None, args=None): # 定制 selection 和 where 进行数字查找，别名为 _num_
        'find number by select and where'
        sql = ['SELECT %s _num_ FROM `%s`' % (selectField, cls.__table__)]
        if where: # 处理where条件
            sql.append('WHERE') # 语句
            sql.append(where) # 条件
        rs = yield from select(' '.join(sql), args, 1)
        if len(rs)==0:
            return None
        return rs[0]['_num_']

    @classmethod
    @asyncio.coroutine
    def count(cls, item_count=[], item_sum=[], args=None): # 统计指定属性
        sql = ['SELECT `%s`, %s FROM `%s`' % (cls.__primary_key__, ','.join(list(map(lambda f: 'COUNT(`%s`)' % f, item_count)) + list(map(lambda g: 'SUM(`%s`)' % g, item_sum))) ,cls.__table__)]
        if args is None:
            args = []
        rs = yield from select(' '.join(sql), args)
        return rs[0]

    @asyncio.coroutine
    def save(self): # 保存实例到数据库
        args = list(map(self.getValueOrDefault, self.__fields__)) # 获取属性列表的值（非主键）
        args.append(self.getValueOrDefault(self.__primary_key__)) # 添加主键的值
        rows = yield from execute(self.__insert__, args) # 将至更新到数据库中
        if rows != 1: # 处理失败的情况
            logging.warn('[ORM] Failed to insert record: affected rows: %s' % rows)
            
    @asyncio.coroutine
    def update(self): # 更新数据库数据
        args = list(map(self.getValue, self.__fields__)) # 获取属性列表的值
        args.append(self.getValue(self.__primary_key__)) # 添加主键的值
        rows = yield from execute(self.__update__, args) # 将至更新到数据库中
        if rows != 1: # 处理失败的情况
            logging.warn('[ORM] Failed to updata by primary key: affected rows: %s' % rows)
    
    @asyncio.coroutine
    def delete(self): # 删除数据
        args = [self.getValue(self.__primary_key__)] # 获取属性列表的值
        rows = yield from execute(self.__delete__, args) # 将至更新到数据库中
        if rows != 1: # 处理失败的情况
            logging.warn('[ORM] Failed to remove by primary key: affected rows: %s' % rows)

'''
# 测试代码         
loop = asyncio.get_event_loop()
loop.run_until_complete(create_pool(host='127.0.0.1', port=3306, user='Infuny', password='asdfgh', datebase='puresakura', loop=loop))
rs = loop.run_until_complete(select('select * from firstSchool', None))
# 获取到了数据库返回的数据
print('heh:%s' % rs)
'''