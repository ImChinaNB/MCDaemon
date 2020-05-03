"""
MCDaemonReloaded 自我控制插件
用于挂机
"""
from event import TRIGGER
import json, utils, re
from utils import CC

helpstr = """SelfControl 自我控制插件 帮助
!!self help - 查看此帮助
!!self leftclick <every/once/keep> [ticks] - 以后面指定的方式点左键
!!self rightclick <every/once/keep> [ticks] - 以后面指定的方式点右键
!!self stop - 停止点击
!!self shadow - 创建自己的影分身，将会断开你与服务器的连接，但将会执行点击操作并保持你的原位置不变
例子：
!!self leftclick every 5 - 每 5 tick 点一下左键，即每 0.25s 点击一次
!!self rightclick keep - 按住右键
!!self rightclick once - 按一次右键
!!self stop - 停止点击操作
请注意 ticks 必须大于等于 2。
"""
def doclick(server, sender, typ, cot):
  command = None
  if cot == "once": command = "/player " + sender + " " + typ + " once"
  elif cot == "keep": command = "/player " + sender + " " + typ + " continuous"
  elif cot.startswith("every"): command = "/player " + sender + " " + typ + " interval " + cot[6:]
  if command:
    server.execute(command)
    server.tell(sender, CC("[SELF] ","d"), CC("执行操作 ", "e"), CC(typ, "6"), CC(" "), CC(cot, "6"))
  else:
    server.tell(sender, CC("[SELF] ","d"), CC("无法执行操作 ", "e"), CC(typ, "6"), CC(" "), CC(cot, "6"))
def oninfo(ev,server,plugin):
  if ev["content"] == "!!self":
    for i in helpstr.split("\n"): server.tell(ev["sender"], CC(i, "e"))
    return
  if not ev["content"].startswith("!!self "): return
  if ev["content"] == "!!self help":
    for i in helpstr.split("\n"): server.tell(ev["sender"], CC(i, "e"))
  elif re.match(r"^!!self leftclick (every [0-9]+|once|keep)$", ev["content"]):
    doclick(server, ev["sender"], "attack", re.match(r"^!!self leftclick (every [0-9]+|once|keep)$", ev["content"]).group(1))
  elif re.match(r"^!!self rightclick (every [0-9]+|once|keep)$", ev["content"]):
    doclick(server, ev["sender"], "use", re.match(r"^!!self rightclick (every [0-9]+|once|keep)$", ev["content"]).group(1))
  elif ev["content"] == "!!self shadow":
    server.execute("/player " + ev["sender"] + " shadow")
  elif ev["content"] == "!!self stop":
    server.execute("/player " + ev["sender"] + " stop")
    server.tell(ev["sender"], CC("[SELF] ","d"), CC("停止了操作。", "e"))
  else:
    server.tell(ev["sender"], CC("[SELF] ","d"), CC("不存在该指令。请检查输入！", "c"))

name = "SelfControlPlugin"
listener = [
  {"type": TRIGGER.PLAYER_INFO, 'func': oninfo}
]
