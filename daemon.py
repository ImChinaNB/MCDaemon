#!/usr/bin/env python3
"""
This is the main file of MCDaemonReloaded.
Written by ChinaNB, GPL 3.0 License.
"""
import json, os, sys, threading, builtins

from server import Server
from handler import Handler
from event import Event, TRIGGER
from plugin import Plugin, loadPlugins
builtins.reload_plugin = False
builtins.debugon = False
builtins.debugtargets = ["ImSingularity", "ImLinDun"]

def asyncRun(func, args):
  thread = threading.Thread(target=func,args=args)
  thread.setDaemon(True)
  thread.start()
def getInput(server, event):
  while True:
    try:
      inp = input()
    except:
      print("[Daemon/Error] 获取控制台输入时发生错误。重启输入线程。")
    if inp.strip() != '':
      event.trigger(TRIGGER.CONSOLE_INFO, {"h": "", "m": "", "s": "", "source": "console", "sender": False, "content": inp})
      server.execute(inp)      

print("[Daemon/Info] 启动中...")
## read config
with open("config.json", "r") as f:
  config = json.loads(f.read())

print("[Daemon/Info] 配置文件加载完毕！")

stopserver = False
server = Server(config["cwd"], config["command"])
event = Event()
plugin = Plugin(server, event)
event.setParm(server, plugin)
handler = Handler(server, event)
print("[Daemon/Info] 服务器类初始化完毕！")
try:
  print("[Daemon/Info] 后端游戏服务器启动中...")
  server.start()
  asyncRun(getInput, (server,event))
  print("[Daemon/Info] 开始初始化插件...")
  loadPlugins(plugin)
except Exception:
  __import__("traceback").print_exc(file=sys.stdout)
  server.stop()
while True:
  try:
    print(handler.tick())
    if reload_plugin == True:
      plugin.clearall()
      print("[Daemon/Info] 插件重载被触发！")
      loadPlugins(plugin)
      builtins.reload_plugin = False
    if server.stopped():
      print("[Daemon/Info] 后端服务器停止了。正在停止 Daemon...")
      break
    if stopserver == True:
      server.stop()
  except Exception:
    print("[Daemon/Error] 在 TICK Daemon 时发生了错误！")
    __import__("traceback").print_exc(file=sys.stdout)

print("[Daemon/Info] Daemon 停止成功。")
if server.stopped() == False:
  print("[Daemon/Warn] 发现服务器进程尚未结束，正在强制停止...")
  server.stop(True)
print("[Daemon/Info] 程序停止。")