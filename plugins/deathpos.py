from event import TRIGGER
from utils import CC

def getdim(dim):
  if dim == 0: return "overworld"
  elif dim == -1: return "the_nether"
  elif dim == 1: return "the_end"
  else: return ""
def oninfo(ev, server, plugin):
  pos = plugin.getplugin("PlayerInfoAPI").getPlayerInfo(server,ev["sender"], "Pos")
  dim = plugin.getplugin("PlayerInfoAPI").getPlayerInfo(server,ev["sender"], "Dimension")
  if pos == None: return
  server.say(CC(ev['sender'],'f'), CC(" 死亡地点位于","e"), CC(" {0} [{1},{2},{3}]".format(["地狱","主世界", "末地"][dim+1], int(pos[0]),int(pos[1]),int(pos[2])), "6"))
  server.say("[name:{0}, x:{1}, y:{2}, z:{3}, dim:{4}, world:{5}]".format(ev["sender"]+"死亡地点", int(pos[0]),int(pos[1]),int(pos[2]), dim, getdim(dim)))

name = "DeathPosPlugin"
listener = [
  {"type": TRIGGER.PLAYER_DEATH, "func": oninfo}
]
