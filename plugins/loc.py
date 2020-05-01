"""
MCDaemonReloaded 路标插件
用于存储位置，方便找机器啥的
"""
from event import TRIGGER
import json, config, re
from textapi import CC
from plugins.playerinfo import getPlayerInfo
locs = []

def onload(ev,sender,plugin):
  if ev["name"] == name:
    global locs
    locs = config.loadConfig('location', [])
def onunload(ev,sender,plugin):
  if ev["name"] == name:
    global locs
    config.saveConfig('location', locs)
def printhelp(server):
  for t in """Location 路标插件 帮助
!!loc help - 查看此帮助
!!loc save - 立刻保存所有路标到硬盘
!!loc add <路标名称> <X> <Y> <Z> <世界ID> - 新建一个路标
!!loc add <路标名称> here - 在你所在的位置新建路标
!!loc del <路标名称或 ID> - 删除一个路标
!!loc conv <路标名称或 ID> - 查看一个路标对应的地狱坐标或主世界坐标
!!loc <路标名称或 ID> - 查看一个路标的信息。若该路标不存在，将在所有路标中搜索。
!!loc - 查看所有路标
世界 ID 说明: 0 - 主世界，1 - 末地，-1 - 地狱""".split("\n"): server.say(CC(t,"e"))
def getloc(locn):
  global locs
  for (i,loc) in enumerate(locs):
    if str(i) == locn: return (loc,i)
    if loc["name"].lower() == locn.lower(): return (loc,i)
  return False
def checkname(namee):
  if getloc(namee) != False: return '已经存在该名字的路标'
  try:
    t = int(namee)
  except:
    return False
  else:
    return '路标名不能由纯数字构成，也不能包含空格'
def mixhover(text,loc):
  return {**text, **{'hoverEvent': {'action': 'show_text', 'value': u'§a[' + str(loc['pos']['x']) + u', ' + str(loc['pos']['y']) + u', ' + str(loc['pos']['z']) + u']§r'}}}
def getpos(loc):
  dimtable = {0: '主世界', 1: '末地', -1: '地狱'}
  return mixhover(CC(dimtable[loc['dim']] + ' [' + str(loc['pos']['x']) + ',' + str(loc['pos']['y']) + ',' + str(loc['pos']['z']) + ']', '6'), loc)
def add(server, ev):
  global locs
  args = ev['content'].split(' ')
  t = checkname(args[2])
  if t != False:
    server.tell(ev['sender'], CC('[LOC] ','b'),CC(t,'c'))
    return
  locs.append({
    'name': args[2],
    'pos': {'x': int(args[3]),'y': int(args[4]),'z': int(args[5])},
    'dim': int(args[6])
  })
  server.say(CC('[LOC] ','b'),CC(ev['sender'], 'f'), CC(' 添加了路标 ', 'e'), CC(locs[-1]['name'], '6'), CC(' 位于 ', 'e'),
  getpos(locs[-1]), CC('，ID 为 ', 'e'), CC(str(len(locs) - 1), '6'))
def addHere(server, ev):
  global locs
  args = ev['content'].split(' ')
  t = checkname(args[2])
  if t != False:
    server.tell(ev['sender'], CC('[LOC] ','b'),CC(t,'c'))
    return
  t = getPlayerInfo(server, ev["sender"], "Pos")
  t1 = getPlayerInfo(server, ev["sender"], "Dimension")
  locs.append({'name': args[2], 'pos': {'x': int(t[0]),'y': int(t[1]),'z': int(t[2])},'dim': t1})
  server.say(CC('[LOC] ','b'),CC(ev['sender'], 'f'), CC(' 添加了路标 ', 'e'), CC(locs[-1]['name'], '6'), CC(' 位于 ', 'e'),
  getpos(locs[-1]), CC('，ID 为 ', 'e'), CC(str(len(locs) - 1), '6'))
def convloc(loc):
  if loc['dim'] == -1:
    return {'name': loc['name'], 'pos':{'x': loc['pos']['x']*8, 'y': loc['pos']['y'], 'z': loc['pos']['z']*8}, 'dim': 0}
  elif loc['dim'] == 0:
    return {'name': loc['name'], 'pos':{'x': int(loc['pos']['x']/8), 'y': loc['pos']['y'], 'z': int(loc['pos']['z']/8)}, 'dim': -1}
  else: return None
def delete(server, ev):
  global locs
  args = ev['content'].split(' ')
  t = getloc(args[2])
  if t == False:
    server.tell(ev['sender'], CC('[LOC] ','b'), CC('找不到对应的路标，请检查输入！', 'c'))
  else:
    t = t[0]
    locs.remove(t)
    server.say(CC('[LOC] ','b'),CC(ev['sender'], 'f'), CC(' 删除了路标 ', 'e'), CC(t['name'], '6'),CC(' 位于 ', 'e'),getpos(t))
def showloc(server,player,loc,id):
  server.tell(player, CC('[LOC] ','b'), CC('路标 <', 'e'), CC(loc['name'], '6'), CC('> 位于 ', 'e'), getpos(loc), CC('，ID 为 ','e'), CC(str(id), '6'))
def get(server,ev):
  global locs
  args = ev['content'].split(' ')
  t = getloc(args[1])
  if t == False:
    for (j,i) in enumerate(locs):
      if args[1].lower()  in i['name'].lower():
        showloc(server,ev['sender'],i,j)
        t = True
    if t == False:
      server.tell(ev['sender'], CC('[LOC] ','b'), CC('找不到任何路标，请检查输入！', 'c'))
  else:
    showloc(server,ev['sender'], t[0],t[1])
def conv(server,ev):
  global locs
  args = ev['content'].split(' ')
  t = getloc(args[2])
  if t == False:
    server.tell(ev['sender'], CC('[LOC] ','b'), CC('找不到该路标，请检查输入！', 'c'))
    return
  t1 = convloc(t[0])
  if t1 is None:
    server.tell(ev['sender'], CC('[LOC] ','b'), CC('该路标位于末地！', 'c'))
  showloc(server,ev['sender'],t[0],t[1])
  showloc(server,ev['sender'],t1,t[1])
def getAll(server,ev):
  global locs
  for i,loc in enumerate(locs): showloc(server,ev['sender'], loc,i)
def oninfo(ev,server,plugin):
  if ev["sender"] != False and ev["content"].startswith('!!loc'):
    try:
      if re.match(r"^!!loc help$", ev["content"]):
        printhelp(server)
      elif re.match(r"^!!loc save$", ev["content"]):
        global locs
        config.saveConfig('location', 'locs')
        server.tell(ev["sender"], CC('[LOC] ','b'), CC('保存完毕', 'e'))
      elif re.match(r"^!!loc add \S+ -?\d+ -?\d+ -?\d+ (-1|0|1)$", ev["content"]):
        add(server, ev)
      elif re.match(r"^!!loc add \S+ here$", ev["content"]):
        addHere(server, ev)
      elif re.match(r"^!!loc del \S+$", ev["content"]):
        delete(server, ev)
      elif re.match(r"^!!loc conv \S+$", ev["content"]):
        conv(server, ev)
      elif re.match(r"^!!loc \S+$", ev["content"]):
        get(server, ev)
      elif re.match(r"^!!loc$", ev["content"]):
        getAll(server, ev)
      else:
        server.tell(ev["sender"], CC('[LOC] ','b'), CC('输入无效，使用 !!loc help 查看帮助', 'c'))
    except:
      pass

name = "LocationPlugin"
listener = [
  {"type": TRIGGER.PLUGIN_LOADED, 'func': onload},
  {"type": TRIGGER.PLUGIN_UNLOADING, 'func': onunload},
  {"type": TRIGGER.PLAYER_INFO, 'func': oninfo}
]
