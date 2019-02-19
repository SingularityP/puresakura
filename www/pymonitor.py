#!/usr/bin/enc python3
# -*- conding: utf-8 -*-

__author__ = 'Infinity'

import os, sys, time, subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def log(s): # 日志记录函数
    print('[Monitor] %s' %s)
    
class MyFileSystemEventHandler(FileSystemEventHandler): # 继承并自定义 文件系统事件监听器
    def __init__(self, fn): # 构造方法初始化
        super(MyFileSystemEventHandler, self).__init__() # 调用父类方法构造
        self.restart = fn # 重启方法
        
    def on_any_event(self, event): # 事件过滤器
        if event.src_path.endswith('.py'): # 若事件由py文件的改动引起
            log('Python source file changed: %s' % event.src_path) # 记录日志
            self.restart() # 调用重启方法
            
command = ['echo', 'ok'] # 启动进程命令
process = None # 进程指针

def kill_process(): # 结束进程
    global process # 获取全局变量 - 进程
    if process: # 有进程就可以杀死
        log('Kill process [%s]...' % process.pid)
        process.kill()
        process.wait()
        log('Process ended with code %s.' % process.returncode)
        process = None # 清空进程变量
        
def start_process(): # 启动进程
    global process, command # 获取全局变量 - 进程，命令
    log('Start process %s...' % ' ' .join(command))
    process = subprocess.Popen(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr) # 重定向输入输出为当前进程的输入输出

def restart_process(): # 重启进程，经上述两个函数整合
    kill_process() # 结束进程
    start_process() # 启动进程

def start_watch(path, callback): # 看门口主调程序
    observer = Observer() # 创建观察者
    observer.schedule(MyFileSystemEventHandler(restart_process), path, recursive=True) # 绑定重启函数、监听路径
    observer.start() # 启动观察者
    log('Watching directory %s...' % path) # 记录日志
    start_process() # 首次启动进程
    try:
        while True: # 循环等待
            time.sleep(0.5) # 推迟执行0.5秒
    except KeyboardInterrupt:
        observer.stop() # 人为停止程序时，此进程也要保证停止
    observer.join() # 加入主线程结束掉
    
if __name__ == '__main__': # 自动调用
    argv = sys.argv[1:]
    if not argv:
        print('Usage: ./pymonitor your-script.py')
        exit(0)
    if argv[0] != 'python':
        argv.insert(0, 'python')
    command = argv
    path = os.path.abspath('.')
    start_watch(path, None)