#!/usr/bin/env python3
"""
This is the plugin class file of MCDaemonReloaded.
Written by ChinaNB, GPL 3.0 License.

plugin: manage all plugins.
Hook their events at startup & rehook when reload. also offer some utils.
"""
import importlib.util, uuid, sys, builtins
from event import TRIGGER
from pathlib import Path
from textapi import CC

class Plugin:
  def __init__(self, server, event):
    self.server = server
    self.event = event
    self.plugs = []
    self.id = 0
  def clearall(self):
    for plug in self.plugs:
      del plug["plugin"]
    del self.plugs
    self.plugs = []
    self.id = 0
    self.event.clearall()
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
      spec = importlib.util.spec_from_file_location('plug_' + str(self.id), pluginPath)
      self.plugs.append({"plugin": importlib.util.module_from_spec(spec)})
      stage = 1
      spec.loader.exec_module(self.plugs[-1]["plugin"])
      self.plugs[-1]["id"] = self.id
      self.plugs[-1]["listener"] = []
      self.plugs[-1]["name"] = self.plugs[-1]["plugin"].name
      self.id += 1
      stage = 2
      self.register(len(self.plugs) - 1)
      self.event.trigger(TRIGGER.PLUGIN_LOADED, {"name": self.plugs[-1]["name"], "plugin": self.plugs[-1]["plugin"]}, False)
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
  def unload(self, pluginId):
    try:
      self.server.debug(CC("卸载插件 "), CC(self.plugs[pluginId]["name"], "el"), CC(" 中，插件 ID 为 "), CC(pluginId, "al"))
      deregister(pluginId)
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
    if plug.is_file() and plug.suffix == '.py' and str(plug) != "plugins/__init__.py":
      print("[Daemon/Info] 初始化插件 " + str(plug))
      plugin.load(str(plug))