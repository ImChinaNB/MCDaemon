from event import TRIGGER
from textapi import CC

lines = """可用指令有（一般的，输入!!<指令> help 可查看对应帮助）:
!!bot
!!debug
!!help
!!here
!!ib
!!loc
!!self
!!whereis
"""

def helpPlugin(ev, server, plugin):
  if ev["content"] != "!!help": return
  for line in lines.split("\n"):
    server.tell(ev["sender"], CC(line, "e"))

listener = [
  {"type": TRIGGER.PLAYER_INFO, "func": helpPlugin}
]
name = "HelpPlugin"
