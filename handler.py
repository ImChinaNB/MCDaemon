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

class Handler:
  def __init__(self, server, event):
    self.server = server
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
      print("[Daemon/Error] 无法解析控制台输出。原文本为: ")
      print("[Daemon/Error]", line)
    return r
  def tick(self):
    # Run a tick, means get output from the server and deal with it.
    if self.server.stopped():
      self.event.trigger(TRIGGER.SERVER_STOPPED, {})
      return self.server.recv()
    r = self.server.recv() # get the output
    for line in r.splitlines():
      t = self._getInfo(line)
      if t["content"].startswith("No player was found"): continue
      self.server.debug(CC("控制台文本解析数据 ", "8"), CC(json.dumps(t), "6l"))
      if t["content"].startswith("Done"):
        self.event.trigger(TRIGGER.SERVER_STARTED, t)
      elif t["content"].startswith("Starting minecraft server version"):
        self.event.trigger(TRIGGER.SERVER_STARTING, t)
      elif t["content"].startswith("Stopping server"):
        self.event.trigger(TRIGGER.SERVER_STOPPING, t)
      elif t["content"].startswith("A single server tick"):
        self.event.trigger(TRIGGER.SERVER_HALT, t)
      elif t["source"] == "Server thread/INFO" and re.match(r'[a-zA-Z_-]+ left the game', t["content"]) is not None:
        t["sender"] = re.match(r'([a-zA-Z_-]+) left the game', t["content"]).group(1)
        self.event.trigger(TRIGGER.PLAYER_LEAVE, t)
      elif t["source"] == "Server thread/INFO" and re.match(r'[a-zA-Z_-]+ joined the game', t["content"]) is not None:
        t["sender"] = re.match(r'([a-zA-Z_-]+) joined the game', t["content"]).group(1)
        self.event.trigger(TRIGGER.PLAYER_JOIN, t)
      elif t["source"] == "Server thread/INFO" and re.match(r'Player [a-zA-Z_-]+ \(UUID: .*?\) used command: ', t["content"]) is not None:
        test = re.match(r'Player ([a-zA-Z_-]+) \(UUID: .*?\) used command: (.*)$', t["content"])
        t["content"] = test.group(2)
        t["sender"] = test.group(1)
        if t["sender"].lower() not in server.playerlist_lower and offline_login:
          self.server.debug(CC("玩家试图在未登录状态下执行指令 ", "8"), CC(t["sender"], "6l"))
          self.event.trigger(TRIGGER.PLAYER_COMMAND_ALL, t)
          continue # pass the event
        self.event.trigger(TRIGGER.PLAYER_COMMAND, t)
      elif t["sender"] != False:
        if t["sender"].lower() not in server.playerlist_lower and offline_login:
          self.server.debug(CC("玩家试图在未登录状态下说话 ", "8"), CC(t["sender"], "6l"))
          self.event.trigger(TRIGGER.PLAYER_INFO_ALL, t)
          continue # pass the event
        self.event.trigger(TRIGGER.PLAYER_INFO, t)
      else:
        self.event.trigger(TRIGGER.SERVER_INFO, t)
    return r