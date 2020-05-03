#!/usr/bin/env python3
"""
This is the server class file of MCDaemonReloaded.
Written by ChinaNB, GPL 3.0 License.

Server: create a server by passing Working Directory and Starting Command.
e.g s = Server("/home/mc/fabric", "java -jar fabric-server.jar nogui")
"""
from subprocess import Popen, PIPE, STDOUT
import os, select, time, builtins, utils, json, platform, io
from logging import getLogger
l = getLogger(__name__)

class Server:
  def __init__(self, cfg):
    self.cwd = cfg["cwd"]
    self.cfg = cfg
    self.temp = {}
    self.playerlist = []
    self.playerlist_lower = []
    self.offline_login = False
    self.debugtargets = ["ImSingularity", "ImLinDun"]
    self.reloadPlugins = False
    self.debugon = False
    self.command = cfg["command"]
    self.process = ""
  def start(self):
    if not self.stopped(): return False
    l.info("服务器启动中...")
    self.process = Popen(self.command.split(" "), cwd=self.cwd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, bufsize=1)
    if platform.system() != "Windows":
      # use follow direct import statements to mess up PyLint, avoiding fucking errors cuz i'm on windows
      __import__("fcntl").fcntl(self.process.stdout, __import__("fcntl").F_SETFL, __import__("fcntl").fcntl(self.process.stdout, __import__("fcntl").F_GETFL) | __import__("os").O_NONBLOCK)
    l.info("服务器 IO 重定向 ---> 主线程")
    self.iter = io.TextIOWrapper(self.process.stdout, line_buffering=True, encoding="utf-8")
  def stop(self, force=False):
    if force: self.process.kill()
    else: self.execute("stop")
  def stopped(self):
    return self.process == "" or self.process.poll() is not None
  def send(self, data):
    self.process.stdin.write(data.encode("utf-8"))
    self.process.stdin.flush()
  def execute(self, command):
    self.send(command + '\n')
  def say(self, *texts):
    cmd = "/tellraw @a ["
    for text in texts:
      if isinstance(text, dict):
        cmd += json.dumps(text) + ","
      else:
        cmd += json.dumps({"text": text}) + ","
    if cmd[-1:] == ",": cmd = cmd[:-1]
    cmd += "]"
    self.execute(cmd)
  def tell(self, player, *texts):
    if player == False:
      l.info("向控制台的消息: %s", utils.NC(*texts))
      return
    cmd = "/tellraw " + player + " ["
    for text in texts:
      if isinstance(text, dict):
        cmd += json.dumps(text) + ","
      else:
        cmd += json.dumps({"text": text}) + ","
    if cmd[-1:] == ",": cmd = cmd[:-1]
    cmd += "]"
    self.execute(cmd)
  def debug(self, *texts):
    if self.debugon:
      l.debug(utils.NC(*texts))
      f = list(texts)
      f = [utils.CC("[Daemon/Debug] ", "7")] + f
      for target in self.debugtargets:
        if target.lower() in self.playerlist_lower: self.tell(target, *f)