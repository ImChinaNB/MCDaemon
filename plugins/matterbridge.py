"""
MCDaemonReloaded 服务器 MatterBridge 插件
提供简单的 MatterBridge 消息同步。
需要 requests 库！
"""
import config, requests, json, sys
from event import TRIGGER
from textapi import CC
from daemon import asyncRun
from threading import Timer
stoprun = True
cfg = {"enabled": False, "remote": "", "token": ""}

def fetch(server, header, remote):
  try:
    r = requests.get(remote + '/api/messages', headers=header)
    r.raise_for_status()
    j = r.json()
    for text in j:
      server.say(CC("[Discord] ", "b"), CC("<" + text["username"] + "> ", "7"), CC(text["text"], "f"))
  except:
    print("[MatterBridge/Error] 无法获取信息。等待 120s.")
    __import__("traceback").print_exc(file=sys.stdout)
    if not stoprun: Timer(120, fetch, (server, header, remote)).start()
  else:
    if not stoprun: Timer(5, fetch, (server, header, remote)).start()
def loaded(ev, server, plugin):
  if ev["name"] == name:
    cfg = config.loadConfig("matterbridge", {"enabled": False, "remote": "", "token": ""})
    if cfg["enabled"]:
      global stoprun
      stoprun = False
      fetch(server, {'Authorization': 'Bearer ' + cfg["token"]}, cfg["remote"])
def unloading(ev, server, plugin):
  if ev["name"] == name:
    global stoprun
    stoprun = True
    config.saveConfig("matterbridge", cfg)
def message(ev, server, plugin):
  if cfg["enabled"]:
    headerss = {'Authorization': 'Bearer ' + cfg["token"],'Content-Type': 'application/json'}
    Timer(0, requests.post, {'url': cfg['remote']+'/api/message', 'headers': headerss, 'data': json.dumps({"text": ev["content"],"username":ev["sender"],"gateway":"discord-minecraft"})})
listener = [
  {"type": TRIGGER.PLUGIN_LOADED, "func": loaded},
  {"type": TRIGGER.PLUGIN_UNLOADING, "func": unloading},
  {"type": TRIGGER.PLAYER_INFO, "func": message}
]
name = "MatterBridgePlugin"
