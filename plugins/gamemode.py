from event import TRIGGER
import utils
gm = []
def onload(ev,server,plugin):
  if ev["name"] == name:
    global gm
    gm = utils.loadData('gamemode', [])
def onunload(ev,server,plugin):
  if ev["name"] == name:
    utils.saveData('gamemode', gm)
def issep(p):
  for i in gm:
    if i[0].lower()==p.lower(): return i
  return False

def oninfo(ev,server,plugin):
  if ev['sender'] != False and ev['content'] == '!!gm':
    p = ev['sender']
    if issep(p) != False:
      g = issep(p)
      server.execute('gamemode 0 ' + p)
      server.execute('execute in {0} run tp {1} {2} {3} {4}'.format(['the_nether','overworld','the_end'][g[1]+1],g[0],g[2],g[3],g[4]))
      server.tell(p, utils.CC('结束灵魂出窍.', 'e'))
      global gm
      gm.remove(g)
    else:
      server.execute('gamemode 3 ' + p)
      pos = plugin.getplugin("PlayerInfoAPI").getPlayerInfo(server,p, "Pos")
      dim = plugin.getplugin("PlayerInfoAPI").getPlayerInfo(server,p, "Dimension")
      gm.append([p, dim, *pos])
      server.tell(p, utils.CC('开始灵魂出窍.', 'e'))

name = 'GamemodePlugin'
listener = [
  {"type": TRIGGER.PLUGIN_LOADED, 'func': onload},
  {"type": TRIGGER.PLUGIN_UNLOADING, 'func': onunload},
  {"type": TRIGGER.PLAYER_INFO, 'func': oninfo}
]