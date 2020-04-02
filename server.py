#!/usr/bin/env python3
"""
This is the server class file of MCDaemonReloaded.
Written by ChinaNB, GPL 3.0 License.

Server: create a server by passing Working Directory and Starting Command.
e.g s = Server("/home/mc/fabric", "java -jar fabric-server.jar nogui")
"""
from subprocess import Popen, PIPE, STDOUT
import fcntl, os, select, time, builtins, textapi, json

class Server:
  def __init__(self, cwd, command):
    self.cwd = cwd
    self.playerlist = []
    self.playerlist_lower = []
    self.command = command
    self.process = ""
  def start(self):
    if self.process != "" and self.process.poll() is None:
      return False
    self.process = Popen(self.command.split(" "), cwd=self.cwd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, encoding='utf8')
    fcntl.fcntl(self.process.stdout, fcntl.F_SETFL, fcntl.fcntl(self.process.stdout, fcntl.F_GETFL) | os.O_NONBLOCK)
  def stop(self, force=False):
    if force: self.process.kill()
    else: self.execute("stop")
  def stopped(self):
    return not (self.process != "" and self.process.poll() is None)
  def send(self, data):
    self.process.stdin.write(data)
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
    if debugon:
      print("[Daemon/Debug]", textapi.NC(*texts))
      f = list(texts)
      f = [textapi.CC("[Daemon/Debug] ", "7")] + f
      for target in debugtargets:
        if target.lower() in playerlist_lower: self.tell(target, *f)
  def recv(self, delay=0.1):
    r = ''
    pr = self.process.stdout
    while True:
      if not select.select([pr], [], [], delay)[0]:
        time.sleep(delay)
        continue
      r = pr.read()
      return r.rstrip()
    return r.rstrip()