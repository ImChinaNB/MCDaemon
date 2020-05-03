"""
MCDaemonReloaded 服务器核心插件
用于统计服务器信息。
"""
from event import TRIGGER
from utils import CC

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
def reloadPlugin(ev, server, plugin):
  if ev["content"] == "@start" and ev["sender"] in [False, "ImSingularity"] and server.stopped():
    server.start()
    return
  if ev["content"] == "@stop" and ev["sender"] in [False, "ImSingularity"] and not server.stopped():
    plugin.getplugin("BotPlugin").kickall_bot(server, ev["sender"], plugin)
    server.stop()
    return
  if ev["content"] != "!!reload": return
  if ev["sender"] not in ["ImSingularity", False]:
    server.tell(ev["sender"], CC("你没有重载插件的权限！", "4"))
    return
  if server.reloadPlugins == True:
    server.tell(ev["sender"], CC("已经在重载插件了，请勿重复执行！", "4"))
    return
  server.reloadPlugins = True
def debugmode(ev, server, plugin):
  if ev["content"] != "!!debug on" and ev["content"] != "!!debug off": return
  if ev["content"] == "!!debug on":
    on = True
  else:
    on = False
  if ev["sender"] not in ["ImSingularity", False, "ImLinDun"]:
    server.tell(ev["sender"], CC("你没有设置调试模式的权限！", "4"))
    return
  if server.debugon == on:
    server.tell(ev["sender"], CC("已经处于该模式！", "4"))
    return
  server.debugon = on

def pi(a,b,c):
  reloadPlugin(a,b,c)
  debugmode(a,b,c)
listener = [
  {"type": TRIGGER.PLAYER_JOIN, "func": joined},
  {"type": TRIGGER.PLAYER_LEAVE, "func": left},
  {"type": TRIGGER.PLAYER_INFO, "func": pi},
  {"type": TRIGGER.CONSOLE_INPUT, "func": pi}
]
name = "CoreAPI"
