"""
MCDaemonReloaded 玩家信息 APi
用于获取玩家信息（如位置）。
"""
import re, threading, json, yaml
from event import TRIGGER

def oninit(ev,server,plugin):
  if ev["name"] == name:
    server.temp["pi"] = None
    server.temp["picb"] = None
def oninfo(ev, server, plugin):
  if ("following entity data" in ev["content"]) and server.temp["pi"] == False:
    try:
      print("PlayerInfoAPI 获取到了数据。正在进行处理...")
      process_str = re.sub(r'^.*? has the following entity data: ', '', ev["content"])
      print("PlayerInfoAPI 处理阶段 1/3")
      black_list = ['minecraft:']
      for str in black_list: process_str = process_str.replace(str,'')
      process_str = re.sub(r"(?<=\d)[a-zA-Z]", '', process_str)
      print("PlayerInfoAPI 处理阶段 2/3")
      player_info = yaml.load("["+process_str+"]")[0]
      print("PlayerInfoAPI 处理阶段 3/3")
      print("PlayerInfoAPI 发送了数据")
      server.temp["pi"] = True
      server.temp["picb"] = player_info
    except:
      server.temp["pi"] = None
      server.temp["picb"] = None

def getPlayerInfo(server, name, nbt):
  if name.lower() not in server.playerlist_lower: return {}
  while server.temp["pi"] is not None:
    pass
  server.temp["pi"] = False
  server.temp["picb"] = None
  server.execute("data get entity " + name + " " + nbt)
  while server.temp["pi"] == False:
    pass
  T = server.temp["picb"]
  server.temp["pi"] = server.temp["picb"] = None
  return T

name = "PlayerInfoAPI"
listener = [
  {"type": TRIGGER.SERVER_INFO, "func": oninfo},
  {"type": TRIGGER.PLUGIN_LOADED, "func": oninit}
]