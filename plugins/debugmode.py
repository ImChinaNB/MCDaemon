"""
MCDaemonReloaded 调试插件
用于开关调试模式。
指令: !!debug [on/off]
"""
from event import TRIGGER
from textapi import CC

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

listener = [
  {"type": TRIGGER.PLAYER_INFO, "func": debugmode},
  {"type": TRIGGER.CONSOLE_INFO, "func": debugmode}
]
name = "DebugModePlugin"
