#!/usr/bin/env python3
"""
This is the main file of MCDaemonReloaded.
Written by ChinaNB, GPL 3.0 License.
"""
import json, os, sys, threading, logging, logger
from utils import loadConfig
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
import time, re

def asyncRun(func, args):
  thread = threading.Thread(target=func,args=args)
  thread.setDaemon(True)
  thread.start()
  return thread
def asyncRunNoDaemon(func, args):
  thread = threading.Thread(target=func,args=args)
  thread.setDaemon(False)
  thread.start()
  return thread
def trackstatus(handler,server,plugin):
  global stopserver,mainthread
  while True:
    try:
      t = handler.track()
      if t == "mstop":
        pass
      elif t == "mstart":
        pass
      if stopserver == True:
        server.stop()
      time.sleep(2)
    except:
      __import__("traceback").print_exc(file=sys.stdout)
      l.warning("获取服务器状态时发生错误。重启监控线程。")
def getInput(server, event, plugin):
  global mainthread
  while True:
    try:
      inp = input()
      if inp == "halt":
        l.info("程序停止中...")
        if server.stopped() == False:
          l.warning("发现服务器进程尚未结束，正在强制停止...")
          server.stop(True)
        l.info("卸载插件中...")
        plugin.unloadall()
        plugin.clearall()
        l.info("程序停止。")
        os._exit(0)
      elif inp.strip() != '':
        event.trigger(TRIGGER.CONSOLE_INPUT, {"h": "", "m": "", "s": "", "source": "console", "sender": False, "content": inp})
        server.execute(inp) 
    except:
      pass
def isverbose(s):
  return s.find("Fetching packet for removed entity class") != -1 or \
    s.find("Wrong location! (") != -1 or \
    s.find("Mismatch in destroy block pos: class_") != -1 or \
    s.find("Can't keep up! Is the server overloaded") != -1
def tickDaemon(server,handler,plugin):
  while True:
    try:
      if not hasattr(server, "iter") or server.iter is None:
        time.sleep(0.5)
        pass
      lines = server.iter.readlines()
      for line in lines:
        if line.rstrip("\n") != "" and not isverbose(line.rstrip("\n").strip()):
          t = line.rstrip("\n")
          r = re.match(r"^\[\d\d:\d\d:\d\d\] \[.+/.+\]: (.*)$", t)
          if r:
            l.info("SERVER %s", r.group(1))
          else:
            l.info("SERVER %s", t)
        handler.tick(line)
        if server.reloadPlugins == True:
          l.info("插件重载被触发！")
          plugin.reloadall()
          loadPlugins(plugin)
          server.reloadPlugins = False
    except Exception:
      if not server.stopped():
        __import__("traceback").print_exc(file=sys.stdout)
        l.error("在 TICK Daemon 时发生了错误！")
        time.sleep(3)

logging.basicConfig(filename='mcd.log', filemode='a')
l = logging.getLogger("daemon")

if __name__ == "__main__":

  l.info("程序启动。")
  ## read cfg
  cfg = loadConfig("daemon", False)
  if not isinstance(cfg, dict):
    l.critical("无法读取配置文件。")
    os._exit(1)

  l.info("配置文件加载完毕。")

  stopserver = False
  mainthread = None
  server = Server(cfg)
  event = Event()
  plugin = Plugin(server, event)
  event.setParm(server, plugin)
  handler = Handler(server, event)
  l.info("基础类初始化完毕。")
  try:
    l.info("各线程启动中...")
    asyncRun(getInput, (server,event,plugin))
    mainthread = None
    asyncRunNoDaemon(trackstatus, (handler,server,plugin))
    l.info("各线程启动完毕。")
    l.info("插件初始化...")
    loadPlugins(plugin)
    l.info("插件初始化完毕。")
    l.info("启动后台服务器...")
    server.start()
    l.info("启动服务器处理线程...")
    asyncRun(tickDaemon, (server,handler,plugin))
    l.info("MCDR 初始化完毕。")
  except Exception:
    l.error("无法初始化 MCDR。正在尝试停止服务器... 输入 halt 退出程序。")
    try:
      server.stop()
    except: pass
