#!/usr/bin/env python3
"""
This is the event class file of MCDaemonReloaded.
Written by ChinaNB, GPL 3.0 License.

event: Event class for plugins.
Can listen to and undo at any time.
"""
from enum import Enum
import threading, builtins
from textapi import CC

count = 14
class TRIGGER(Enum): # triggers enumerations
  SERVER_STOPPED = 0
  SERVER_STARTED = 1
  SERVER_STARTING = 2
  SERVER_STOPPING = 3
  SERVER_HALT = 4
  SERVER_INFO = 5
  PLAYER_INFO = 6
  PLUGIN_LOADED = 7
  PLAYER_JOIN = 8
  PLAYER_LEAVE = 9
  CONSOLE_INFO = 10
  PLAYER_COMMAND = 11
  PLAYER_COMMAND_ALL = 12
  PLAYER_INFO_ALL = 13

class Event:
  def __init__(self):
    self.fs = []
    for i in range(0, count): self.fs.append({})
  def setParm(self, server, plugin):
    self.server = server
    self.plugin = plugin
  def _asyncRun(self, func, args):
    thread = threading.Thread(target=func,args=args)
    thread.setDaemon(True)
    thread.start()
  def bind(self, trigger, func, id):
    if id in self.fs[trigger.value]: return False # already binded
    self.fs[trigger.value][id] = func
    return True
  def unbind(self, trigger, id):
    if id not in self.fs[trigger.value]: return False # not binded
    del self.fs[trigger.value][id]
    return True
  def clearall(self, trigger=False):
    if trigger != False: self.fs[trigger.value].clear()
    else:
      for i in range(0, count):
        self.fs[i].clear()
  def trigger(self, trigger, eventinfo, asyncrun = True):
    self.server.debug(CC("事件 "), CC(str(trigger), "el"), CC(" 被触发！"))
    for func in self.fs[trigger.value].items():
      if asyncrun: self._asyncRun(func[1], (eventinfo, self.server, self.plugin))
      else: func[1](eventinfo, self.server, self.plugin)
    