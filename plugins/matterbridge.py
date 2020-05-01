"""
MCDaemonReloaded 服务器 MatterBridge 插件
提供简单的 MatterBridge 消息同步。
需要 requests 库！
"""
import config, requests, json, sys, time
from event import TRIGGER
from textapi import CC
from logging import getLogger, Logger, WARNING
l = getLogger(__name__)
cfg = config.loadConfig("matterbridge", {"enabled": False, "remote": "", "token": ""})
def stopped(ev,server,plugin):
  sendadmin("服务器停止了。")
def stopping(ev,server,plugin):
  sendadmin("服务器正在停止...")
def starting(ev,server,plugin):
  sendadmin("服务器正在开启...")
def started(ev,server,plugin):
  sendadmin("服务器开启了。")
  server.execute("save-on")
def tracker(server,plugin,header,remote):
  global cfg
  getLogger("requests").setLevel(__import__("logging").WARNING)
  getLogger("urllib3").setLevel(__import__("logging").WARNING)
  getLogger("urllib3.connection").setLevel(__import__("logging").WARNING)
  getLogger("urllib3.connectionpool").setLevel(__import__("logging").WARNING)
  while True:
    try:
      with requests.get(remote + '/api/messages', headers=header, stream=False) as r:
        r.raise_for_status()
        for i in r.json():
          text = i
          if "event" not in text or text["event"] != "": continue
          if text["gateway"] == "discord-minecraft":
            try:
              server.say(CC("[Discord] ", "b"), CC("<" + text["username"] + "> ", "7"), CC(text["text"], "f"))
            except:
              pass
          else:
            try:
              server.say(CC("[DiscordAdmin] ", "c"), CC("<" + text["username"] + "> ", "7"), CC(text["text"], "f"))
            except:
              pass
            if text["text"] == "stop":
              l.info("服务器被远程停止。")
              sendadmin("服务器被远程停止。")
              server.stop()
            elif text["text"] == "start":
              l.info("服务器被远程开启。")
              sendadmin("服务器被远程开启。")
              server.start()
            elif text["text"] == "forcestop":
              l.info("服务器被强制停止。")
              sendadmin("服务器被强制停止。")
              server.stop(True)
            elif text["text"] == "save-all":
              l.info("服务器存档保存。")
              sendadmin("服务器存档保存。")
              server.execute("save-all")
            elif text["text"] == "help":
              sendadmin("  可用指令有：")
              sendadmin("  --  stop,start,forcestop,save-all")
        time.sleep(4)
    except SystemExit:
      return
    except:
      l.error("MatterBridge 无法从服务器获取信息。")
      # __import__("traceback").print_exc(file=sys.stdout)
      time.sleep(30)
def loaded(ev, server, plugin):
  global cfg
  if ev["name"] == name:
    cfg = config.loadConfig("matterbridge", {"enabled": False, "remote": "", "token": ""})
    if cfg["enabled"]:
      pass
      plugin.asyncRun(name, tracker, {'Authorization': 'Bearer ' + cfg["token"]}, cfg["remote"])
def unloading(ev, server, plugin):
  global cfg
  if ev["name"] == name:
    config.saveConfig("matterbridge", cfg)
def message(ev, server, plugin):
  try:
    global cfg
    if cfg["enabled"]:
      headerss = {'Authorization': 'Bearer ' + cfg["token"],'Content-Type': 'application/json'}
      requests.post(**{'url': cfg['remote']+'/api/message', 'headers': headerss, 'data': json.dumps({"text": ev["content"],"username":ev["sender"],"gateway":"discord-minecraft"})})
  except:
    l.error("无法发送服务器消息到 Discord #Server.")

def sendadmin(c):
  try:
    global cfg
    if cfg["enabled"]:
      headerss = {'Authorization': 'Bearer ' + cfg["token"],'Content-Type': 'application/json'}
      requests.post(**{'url': cfg['remote']+'/api/message', 'headers': headerss, 'data': json.dumps({"text": c,"username":"HTS","gateway":"gateway2"})})
  except:
    l.error("无法发送服务器状态到 Discord #Admin.")
listener = [
  {"type": TRIGGER.PLUGIN_LOADED, "func": loaded},
  {"type": TRIGGER.PLUGIN_UNLOADING, "func": unloading},
  {"type": TRIGGER.PLAYER_INFO, "func": message},
  {"type": TRIGGER.SERVER_STOPPED, "func": stopped},
  {"type": TRIGGER.SERVER_STARTED, "func": started},
  {"type": TRIGGER.SERVER_STOPPING, "func": stopping},
  {"type": TRIGGER.SERVER_STARTING, "func": starting}
]
name = "MatterBridgePlugin"
