"""
MCDaemonReloaded 重载插件
用于触发重载插件。
指令: !!reload
"""
from event import TRIGGER
from textapi import CC
import builtins

def reloadPlugin(ev, server, plugin):
  if not ev["content"].startswith("!!reload"): return
  if ev["sender"] not in ["ImSingularity", False]:
    server.tell(ev["sender"], CC("你没有重载插件的权限！", "4"))
    return
  if reload_plugin == True:
    server.tell(ev["sender"], CC("已经在重载插件了，请勿重复执行！", "4"))
    return
  builtins.reload_plugin = True

listener = [
  {"type": TRIGGER.PLAYER_INFO, "func": reloadPlugin},
  {"type": TRIGGER.CONSOLE_INFO, "func": reloadPlugin}
]
name = "ReloadPlugin"
