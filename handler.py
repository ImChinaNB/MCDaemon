#!/usr/bin/env python3
"""
This is the handler class file of MCDaemonReloaded.
Written by ChinaNB, GPL 3.0 License.

handler: Handle the output of the server.
And trigger events according to the output.
"""
import threading, re, builtins, json
from event import TRIGGER
from utils import CC
from logging import getLogger
l = getLogger(__name__)

death_re = [ "\\w{1,16} blew up",
 "\\w{1,16} burned to death",
 "\\w{1,16} didn't want to live in the same world as .+",
 "\\w{1,16} died",
 "\\w{1,16} died because of .+",
 "\\w{1,16} discovered floor was lava",
 "\\w{1,16} discovered the floor was lava",
 "\\w{1,16} drowned",
 "\\w{1,16} drowned whilst trying to escape .+",
 "\\w{1,16} experienced kinetic energy",
 "\\w{1,16} experienced kinetic energy whilst trying to escape .+",
 "\\w{1,16} fell from a high place",
 "\\w{1,16} fell off a ladder",
 "\\w{1,16} fell off a scaffolding",
 "\\w{1,16} fell off some twisting vines",
 "\\w{1,16} fell off some vines",
 "\\w{1,16} fell off some weeping vines",
 "\\w{1,16} fell out of the water",
 "\\w{1,16} fell out of the world",
 "\\w{1,16} fell too far and was finished by .+",
 "\\w{1,16} fell too far and was finished by .+ using .+",
 "\\w{1,16} fell while climbing",
 "\\w{1,16} hit the ground too hard",
 "\\w{1,16} hit the ground too hard whilst trying to escape .+",
 "\\w{1,16} starved to death",
 "\\w{1,16} starved to death whilst fighting .+",
 "\\w{1,16} suffocated in a wall",
 "\\w{1,16} suffocated in a wall whilst fighting .+",
 "\\w{1,16} tried to swim in lava",
 "\\w{1,16} tried to swim in lava to escape .+",
 "\\w{1,16} walked into a cactus whilst trying to escape .+",
 "\\w{1,16} walked into danger zone due to .+",
 "\\w{1,16} walked into fire whilst fighting .+",
 "\\w{1,16} walked on danger zone due to .+",
 "\\w{1,16} was blown up by .+",
 "\\w{1,16} was blown up by .+ using .+",
 "\\w{1,16} was burnt to a crisp whilst fighting .+",
 "\\w{1,16} was doomed to fall",
 "\\w{1,16} was doomed to fall by .+",
 "\\w{1,16} was doomed to fall by .+ using .+",
 "\\w{1,16} was fireballed by .+",
 "\\w{1,16} was fireballed by .+ using .+",
 "\\w{1,16} was impaled by Trident",
 "\\w{1,16} was impaled by .+",
 "\\w{1,16} was impaled by .+ with .+",
 "\\w{1,16} was killed by [Intentional Game Design]",
 "\\w{1,16} was killed by .+ trying to hurt .+",
 "\\w{1,16} was killed by .+ using .+",
 "\\w{1,16} was killed by .+ using magic",
 "\\w{1,16} was killed by even more magic",
 "\\w{1,16} was killed by magic",
 "\\w{1,16} was killed by magic whilst trying to escape .+",
 "\\w{1,16} was killed trying to hurt .+",
 "\\w{1,16} was poked to death by a sweet berry bush",
 "\\w{1,16} was poked to death by a sweet berry bush whilst trying to escape .+",
 "\\w{1,16} was pricked to death",
 "\\w{1,16} was pummeled by .+",
 "\\w{1,16} was pummeled by .+ using .+",
 "\\w{1,16} was roasted in dragon breath",
 "\\w{1,16} was roasted in dragon breath by .+",
 "\\w{1,16} was shot by Arrow",
 "\\w{1,16} was shot by .+",
 "\\w{1,16} was shot by .+ using .+",
 "\\w{1,16} was slain by Arrow",
 "\\w{1,16} was slain by Small Fireball",
 "\\w{1,16} was slain by Trident",
 "\\w{1,16} was slain by .+ and \\w{1,16} was slain by \\w{1,16}.",
 "\\w{1,16} was slain by .+ using .+ and \\w{1,16} was slain by \\w{1,16} using .+.",
 "\\w{1,16} was slain by .+",
 "\\w{1,16} was slain by .+ using .+",
 "\\w{1,16} was slain by \\w{1,16} using .+",
 "\\w{1,16} was squashed by .+",
 "\\w{1,16} was squashed by a falling anvil",
 "\\w{1,16} was squashed by a falling anvil whilst fighting .+",
 "\\w{1,16} was squashed by a falling block",
 "\\w{1,16} was squashed by a falling block whilst fighting .+",
 "\\w{1,16} was squished too much",
 "\\w{1,16} was struck by lightning",
"\\w{1,16} was struck by lightning whilst fighting .+",
 "\\w{1,16} was stung to death",
 "\\w{1,16} was stung to death by .+",
 "\\w{1,16} went off with a bang",
"\\w{1,16} went off with a bang whilst fighting .+",
 "\\w{1,16} went up in flames",
 "\\w{1,16} withered away",
 "\\w{1,16} withered away whilst fighting .+"]
def isdeath(st):
  for i in death_re:
    if re.match("^" + i + "$", st.strip()) is not None: return True
  return False
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
    elif t["source"] == "Server thread/INFO" and isdeath(t["content"]):
      t["sender"] = t["content"].split(" ")[0]
      self.event.trigger(TRIGGER.PLAYER_DEATH, t)
    elif t["sender"] != False:
      if t["sender"].lower() not in self.server.playerlist_lower and self.server.offline_login:
        self.server.debug(CC("玩家试图在未登录状态下说话 ", "8"), CC(t["sender"], "6l"))
        self.event.trigger(TRIGGER.PLAYER_INFO_ALL, t)
        return
      self.event.trigger(TRIGGER.PLAYER_INFO, t)
    else:
      self.event.trigger(TRIGGER.SERVER_INFO, t)