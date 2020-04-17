#!/usr/bin/env python3
"""
This is the main file of MCDaemonReloaded.
Written by ChinaNB, GPL 3.0 License.
"""
import json, os, sys, threading, config, multiprocessing
"""
import atexit, readline

histfile = os.path.join("cmd_history.txt")
try:
    readline.read_history_file(histfile)
    readline.set_history_length(1000)
except FileNotFoundError:
    pass
atexit.register(readline.write_history_file, histfile)
"""
from server import Server
from handler import Handler
from event import Event, TRIGGER
from plugin import Plugin, loadPlugins
import time

def asyncRun(func, args):
  thread = threading.Thread(target=func,args=args)
  thread.setDaemon(True)
  thread.start()
  return thread
def asyncRunProcess(func, args):
  thread = multiprocessing.Process(target=func,args=args)
  thread.start()
  return thread
def trackstatus(handler,server,plugin):
  global stopserver,mainthread
  while True:
    try:
      t = handler.track()
      if t == "mstop":
        #print("[Daemon/Info] 服务器停止了。停止主进程。")
        #try:
        #  mainthread.terminate()
        #except: pass
        pass
      elif t == "mstart":
        #print("[Daemon/Info] 服务器开启了。启动主进程。")
        #mainthread = asyncRunProcess(tickDaemon, (server,handler, plugin))
        pass
      if stopserver == True:
        server.stop()
      time.sleep(2)
    except:
      print("[Daemon/Error] 获取服务器状态时发生错误。重启监控线程。")
      __import__("traceback").print_exc(file=sys.stdout)
def getInput(server, event, plugin):
  global mainthread
  while True:
    try:
      inp = input()
    except:
      print("[Daemon/Error] 获取控制台输入时发生错误。重启输入线程。")
    if inp == "halt":
      print("[Daemon/Info] Daemon 开始强制停止。")
      if server.stopped() == False:
        print("[Daemon/Warn] 发现服务器进程尚未结束，正在强制停止...")
        server.stop(True)
      print("[Daemon/Info] 服务器停止，卸载插件中。")
      plugin.unloadall()
      plugin.clearall()
      config.saveConfig("daemon", cfg)
      print("[Daemon/Info] 程序停止。")
      os._exit(0)
    elif inp.strip() != '':
      event.trigger(TRIGGER.CONSOLE_INPUT, {"h": "", "m": "", "s": "", "source": "console", "sender": False, "content": inp})
      server.execute(inp)      
def tickDaemon(server,handler,plugin):
  while True:
    try:
      lines = server.iter.readlines()
      for line in lines:
        handler.tick(line)
        if line.rstrip("\n") != "": print(line.rstrip("\n"))
        if server.reloadPlugins == True:
          plugin.unloadall()
          plugin.clearall()
          print("[Daemon/Info] 插件重载被触发！")
          loadPlugins(plugin)
          server.reloadPlugins = False
    except Exception:
      if not server.stopped():
        print("[Daemon/Error] 在 TICK Daemon 时发生了错误！")
        __import__("traceback").print_exc(file=sys.stdout)
        print("[Daemon/Error] 等待 5s ...")
        time.sleep(5)
print("[Daemon/Info] 启动中...")
## read config
cfg = config.loadConfig("daemon", {"cwd": "server", "command": "java -server -jar server.jar", "aswd": "/home/mc/new/server"})

print("[Daemon/Info] 配置文件加载完毕！")

stopserver = False
mainthread = None
server = Server(cfg)
event = Event()
plugin = Plugin(server, event)
event.setParm(server, plugin)
handler = Handler(server, event)
print("[Daemon/Info] 服务器类初始化完毕！")
try:
  print("[Daemon/Info] 输入线程启动中...")
  asyncRun(getInput, (server,event,plugin))
  mainthread = None
  print("[Daemon/Info] 监控线程启动中...")
  asyncRun(trackstatus, (handler,server,plugin))
  print("[Daemon/Info] 开始初始化插件...")
  loadPlugins(plugin)
  print("[Daemon/Info] 后端游戏服务器启动中...")
  server.start()
  print("[Daemon/Info] 主线程启动中...")
  asyncRun(tickDaemon, (server,handler,plugin))
except Exception:
  __import__("traceback").print_exc(file=sys.stdout)
  server.stop()
