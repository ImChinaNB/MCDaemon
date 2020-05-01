"""
MCDaemonReloaded Whereis Plugin
用于获取玩家位置。
"""
from plugins.playerinfo import getPlayerInfo
from event import TRIGGER
from textapi import CC
import re
def mixhover(text,x,y,z):
  return {**text, **{'hoverEvent': {'action': 'show_text', 'value': u'§a[' + str(x) + u', ' + str(y) + u', ' + str(z) + u']§r'}}}
def getpos(x,y,z,dim):
  dimtable = {0: '主世界', 1: '末地', -1: '地狱'}
  return mixhover(CC(dimtable[dim] + ' [' + str(x) + ',' + str(y) + ',' + str(z) + ']', '6'), x,y,z)
def getdim(dim):
  if dim == 0: return "overworld"
  elif dim == -1: return "the_nether"
  elif dim == 1: return "the_end"
  else: return ""
def oninfo(ev,server,plugin):
  if ev['content'] == '!!whereis help':
    server.tell(ev['sender'], CC('用法：!!whereis <玩家名>', 'e'))
  elif re.match(r"^!!whereis ([a-zA-Z0-9_]{3,16})$", ev['content']):
    player = re.match(r"^!!whereis ([a-zA-Z0-9_]{3,16})$", ev['content']).group(1)
    if not player.lower() in server.playerlist_lower:
      server.tell(ev['sender'], CC('该玩家不存在', 'c'))
    t = getPlayerInfo(server, player, 'Pos')
    t2 = getPlayerInfo(server, player, 'Dimension')
    server.say(CC(player, 'f'), CC(' 位于 ', 'e'), getpos(int(t[0]),int(t[1]),int(t[2]), int(t2)))
    server.say("[name:{0}, x:{1}, y:{2}, z:{3}, dim:{4}, world:{5}]".format(player, int(t[0]),int(t[1]),int(t[2]), int(t2), getdim(int(t2))))
    server.tell(ev['sender'], CC('该玩家将会被高亮 30 秒!', '6'))
    server.tell(player, CC('有人查询您的位置，您将会被高亮 30 秒!', '6'))
    server.execute('effect give ' + player + ' glowing 30 2')
name = 'WhereisPlugin'
listener = [
  {'type': TRIGGER.PLAYER_INFO, 'func': oninfo}
]
