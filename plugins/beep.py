# PlayerMention plugin
from event import TRIGGER
from utils import CC
import re

def oninfo(ev, server, plugin):
  if ev["sender"] != False and ev["content"].find("@ ") != -1:
    nl = re.findall(r'(?<=@ )\S+', ev["content"])
    if nl:
      for name in nl:
        if name == 'all':
          server.execute('execute at @a run playsound minecraft:entity.arrow.hit_player player @a')
        else:
          server.execute('execute at ' + name + ' run playsound minecraft:entity.arrow.hit_player player ' + name)

name = "BeepPlugin"
listener = [
  {"type": TRIGGER.PLAYER_INFO, "func": oninfo}
]
