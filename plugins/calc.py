from event import TRIGGER
from utils import CC

def calc(exp2):
  whlist = '0123456789 .,+-*/()<>='
  exp = ''
  for e in exp2:
    if e in whlist: exp += e
  if exp.strip() == "": return None
  try:
    return str(eval(exp))
  except Exception as e:
    return str(e)

def oninfo(ev, server, plugin):
  if ev["content"].startswith("=="):
    res = calc(ev["content"][2:])
    if res != None:
      server.say(CC("结果为 ","e"), CC(str(res), "6"))

name = "CalcPlugin"
listener = [
  {"type": TRIGGER.PLAYER_INFO, "func": oninfo}
]
