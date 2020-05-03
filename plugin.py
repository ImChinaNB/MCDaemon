#!/usr/bin/env python3
"""
This is the plugin class file of MCDaemonReloaded.
Written by ChinaNB, GPL 3.0 License.

plugin: manage all plugins.
Hook their events at startup & rehook when reload. also offer some utils.
"""
import importlib.util
import uuid
import sys
from event import TRIGGER
from pathlib import Path
from utils import CC
import threading
import ctypes, inspect, logging
import time
l = logging.getLogger(__name__)

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

class stoppable_thread(threading.Thread):
  def __init__(self, source,server, plugin, func, *args):
    threading.Thread.__init__(self)
    self.p = [server,plugin,func,args]
    self.source = source
    self.killed = False
  
  def run(self):
    try:
      self.p[2](self.p[0],self.p[1],*self.p[3])
    except SystemExit:
      l.info("Thread from %s has been terminated.", self.source)
    except:
      __import__("traceback").print_exc()
      l.warning("Thread from %s has ended of uncaught exception.", self.source)
  def start(self): 
    self.__run_backup = self.run 
    self.run = self.__run       
    threading.Thread.start(self) 
  
  def __run(self): 
    sys.settrace(self.globaltrace) 
    self.__run_backup() 
    self.run = self.__run_backup 

  def globaltrace(self, frame, event, arg): 
    if event == 'call': 
      return self.localtrace 
    else: 
      return None
  
  def localtrace(self, frame, event, arg): 
    if self.killed: 
      if event == 'line': 
        raise SystemExit() 
    return self.localtrace 
  
  def kill(self): 
    self.killed = True

  def terminate(self): 
    _async_raise(self.ident, SystemExit)

class Plugin:
  def __init__(self, server, event):
    self.server = server
    self.event = event
    self.plugs = []
    self.reloading = False
    self.threads = []
    self.id = 0
  def asyncRun(self, source, func, *args):
    if self.reloading: return False
    l.info("来源 %s 启动线程 %s", source,func)
    t = stoppable_thread(source,self.server,self,func,*args)
    t.start()
    if t.is_alive(): self.threads.append(t)
    return t.is_alive()
  def reloadall(self):
    self.reloading = True
    # terminate all plugin threads
    for thread in self.threads:
      thread.terminate()
      thread.kill()
      # if thread.is_alive(): thread.join()
      if thread.is_alive():
        l.warning("Thread %s is still running, ignoring.", str(thread))
    for thread in self.threads.copy():
      self.threads.remove(thread)
    # first unload all
    self.unloadall()
    # then clear all
    self.clearall()
    self.reloading = False

  def clearall(self):
    try:
      for plug in self.plugs:
        try:
          del plug["plugin"]
        except:
          pass
      del self.plugs
      self.plugs = []
      self.id = 0
      self.event.clearall()
    except:
      pass
  def unloadall(self):
    try:
      for i,j in enumerate(self.plugs):
        if j != {}:
          self.unload(i)
    except:
      pass
  def register(self, id):
    self.server.debug(CC("注册插件事件钩子: "), CC(str(self.plugs[id]["plugin"].listener), "el"))
    for listener in self.plugs[id]["plugin"].listener:
      t = {"id": uuid.uuid4(), "type": listener["type"], "func": listener["func"]}
      if self.event.bind(listener["type"], listener["func"], t["id"]):
        self.plugs[id]["listener"].append(t)
  def deregister(self, id):
    self.server.debug(CC("卸载插件事件钩子: "), CC(str(self.plugs[id]["plugin"].listener), "el"))
    for listener in self.plugs[id]["listener"]:
      if self.event.unbind(listener["type"], listener["id"]):
        self.plugs[id]["listener"].remove(listener)
  def load(self, pluginPath):
    stage = 0
    try:
      self.server.debug(CC("加载插件中: "), CC(pluginPath, "el"))
      spec = importlib.util.spec_from_file_location("p_" + pluginPath.replace("plugins/","").replace(".py","").replace("plugins\\",""), pluginPath)
      self.plugs.append({"plugin": importlib.util.module_from_spec(spec)})
      stage = 1
      spec.loader.exec_module(self.plugs[-1]["plugin"])
      self.plugs[-1]["id"] = self.id
      self.plugs[-1]["listener"] = []
      self.plugs[-1]["name"] = self.plugs[-1]["plugin"].name
      self.id += 1
      stage = 2
      self.register(len(self.plugs) - 1)
      self.server.debug(CC("插件加载完成: "), CC(pluginPath, "el"))
      return self.plugs[-1]["id"]
    except:
      self.server.debug(CC("无法加载插件: "), CC(pluginPath, "el"))
      self.server.debug(CC("错误堆栈详见控制台。", "l"))
      __import__("traceback").print_exc(file=sys.stdout)
      if stage == 2:
        try: self.deregister(len(self.plugs) - 1)
        except: pass
        self.id -= 1
      if stage >= 1: self.plugs.pop()
      return False
  def getplugin(self, pluginName):
    for plug in self.plugs:
      if plug["plugin"] is not None and plug["name"].lower() == pluginName.lower():
        return plug["plugin"]
  def unload(self, pluginId):
    try:
      self.server.debug(CC("卸载插件 "), CC(self.plugs[pluginId]["name"], "el"), CC(" 中，插件 ID 为 "), CC(pluginId, "al"))
      self.event.trigger(TRIGGER.PLUGIN_UNLOADING, {"name": self.plugs[pluginId]["name"], "plugin": self.plugs[pluginId]["plugin"]}, False)
      self.deregister(pluginId)
      del self.plugs[pluginId]["plugin"]
      self.plugs[pluginId] = {}
      return True
    except:
      self.server.debug(CC("无法卸载插件 ID "), CC(pluginId, "al"))
      self.server.debug(CC("错误堆栈详见控制台。", "l"))
      __import__("traceback").print_exc(file=sys.stdout)
      return False

def loadPlugins(plugin):
  for plug in Path('plugins/').iterdir():
    if plug.is_file() and plug.suffix == '.py' and str(plug).find("__init__.py") == -1:
      l.debug("初始化插件 %s", str(plug))
      plugin.load(str(plug))
  for plug in plugin.plugs:
    plugin.event.trigger(TRIGGER.PLUGIN_LOADED, {"name": plug["name"], "plugin": plug["plugin"]}, False)
