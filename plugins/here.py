"""
MCDaemonReloaded 玩家位置 插件
用于高亮玩家位置。
"""
from plugins.playerinfo import getPlayerInfo
from event import TRIGGER
from textapi import CC
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
  if ev['content'] == '!!here':
    t = getPlayerInfo(server, ev['sender'], 'Pos')
    t2 = getPlayerInfo(server, ev['sender'], 'Dimension')
    server.say(CC(ev['sender'], 'f'), CC(' 位于 ', 'e'), getpos(int(t[0]),int(t[1]),int(t[2]), int(t2)))
    server.say("[name:{0}, x:{1}, y:{2}, z:{3}, dim:{4}, world:{5}]".format(ev['sender'], int(t[0]),int(t[1]),int(t[2]), int(t2), getdim(int(t2))))
    server.tell(ev['sender'], CC('您将会被高亮 30 秒!', '6'))
    server.execute('effect give ' + ev['sender'] + ' glowing 30 2')
name = 'HerePlugin'
listener = [
  {'type': TRIGGER.PLAYER_INFO, 'func': oninfo}
]
