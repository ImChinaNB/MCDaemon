"""
MCDaemonReloaded 服务器核心插件
用于统计服务器信息。
"""
from event import TRIGGER

def joined(ev, server, plugin):
  if ev["sender"] != False and ev["sender"].lower() not in server.playerlist_lower:
    server.playerlist.append(ev["sender"])
    server.playerlist_lower.append(ev["sender"].lower())
def left(ev, server, plugin):
  if ev["sender"] != False:
    try:
      server.playerlist.remove(ev["sender"])
      server.playerlist_lower.append(ev["sender"].lower())
    except:
      pass

listener = [
  {"type": TRIGGER.PLAYER_JOIN, "func": joined},
  {"type": TRIGGER.PLAYER_LEAVE, "func": left}
]
name = "CoreAPI"
