#!/usr/bin/env python3
"""
This is the handler class file of MCDaemonReloaded.
Written by ChinaNB, GPL 3.0 License.

handler: Handle the output of the server.
And trigger events according to the output.
"""
import threading, re, builtins, json
from event import TRIGGER
from textapi import CC
from logging import getLogger
l = getLogger(__name__)

class Handler:
  def __init__(self, server, event):
    self.server = server
    self.stopped = True
    self.event = event
  def _getInfo(self, line):
    r = {"h": line[1:3], "m": line[4:6], "s": line[7:9], "source": "", "sender": "", "content": ""}
    try:
      r["source"] = re.search(r'^\[(.*?)\]', line[11:]).group()[1:-1]
      player = ''
      if r["source"] == 'Server thread/INFO' and line[33:].startswith('<'):
        player = re.search(r'\<(.*?)\>', line[33:]).group()[1:-1]
      if player != '':
        r["sender"] = player
        r["content"] = line[33:].replace('[' + r["source"] + ']: ', '' , 1).replace('<' + player + '> ', '', 1)
      else:
        r["sender"] = False
        r["content"] = line[11:].replace('[' + r["source"] + ']: ' , '' , 1)
    except:
      l.warning("无法解析控制台输出。原文本为: %s", line)
    return r
  def track(self):
    # Run a tick, means get output from the server and deal with it.
    if self.server.stopped() and not self.stopped:
      l.info("服务器进程已结束。输入 halt 退出 Daemon.")
      self.server.iter.close()
      del self.server.iter
      self.stopped = True
      self.event.trigger(TRIGGER.SERVER_STOPPED, {})
      return "mstop"
    if not self.server.stopped() and self.stopped:
      l.info("服务器进程启动了.")
      self.stopped = False
      self.event.trigger(TRIGGER.SERVER_STARTING, {})
      return "mstart"
  def tick(self, line):
    self.stopped = False
    t = self._getInfo(line.strip("\n"))
    if t["content"].startswith("No player was found"): return
    self.server.debug(CC("控制台文本解析数据 ", "8"), CC(json.dumps(t), "6l"))
    if t["content"].startswith("Done"):
      self.event.trigger(TRIGGER.SERVER_STARTED, t)
    elif t["content"].startswith("Starting minecraft server version"):
      self.event.trigger(TRIGGER.SERVER_STARTING, t)
    elif t["content"].startswith("Stopping server"):
      self.event.trigger(TRIGGER.SERVER_STOPPING, t)
    elif t["content"].startswith("A single server tick"):
      self.event.trigger(TRIGGER.SERVER_HALT, t)
    elif t["source"] == "Server thread/INFO" and re.match(r'[a-zA-Z0-9_-]+ left the game', t["content"]) is not None:
      t["sender"] = re.match(r'([a-zA-Z0-9_-]+) left the game', t["content"]).group(1)
      self.event.trigger(TRIGGER.PLAYER_LEAVE, t)
    elif t["source"] == "Server thread/INFO" and re.match(r'[a-zA-Z0-9_-]+ joined the game', t["content"]) is not None:
      t["sender"] = re.match(r'([a-zA-Z0-9_-]+) joined the game', t["content"]).group(1)
      self.event.trigger(TRIGGER.PLAYER_JOIN, t)
    elif t["source"] == "Server thread/INFO" and re.match(r'Player [a-zA-Z0-9_-]+ \(UUID: .*?\) used command: ', t["content"]) is not None:
      test = re.match(r'Player ([a-zA-Z0-9_-]+) \(UUID: .*?\) used command: (.*)$', t["content"])
      t["content"] = test.group(2)
      t["sender"] = test.group(1)
      if t["sender"].lower() not in self.server.playerlist_lower and self.server.offline_login:
        self.server.debug(CC("玩家试图在未登录状态下执行指令 ", "8"), CC(t["sender"], "6l"))
        self.event.trigger(TRIGGER.PLAYER_COMMAND_ALL, t)
        return
      self.event.trigger(TRIGGER.PLAYER_COMMAND, t)
    elif t["sender"] != False:
      if t["sender"].lower() not in self.server.playerlist_lower and self.server.offline_login:
        self.server.debug(CC("玩家试图在未登录状态下说话 ", "8"), CC(t["sender"], "6l"))
        self.event.trigger(TRIGGER.PLAYER_INFO_ALL, t)
        return
      self.event.trigger(TRIGGER.PLAYER_INFO, t)
    else:
      self.event.trigger(TRIGGER.SERVER_INFO, t)