"""
MCDaemonReloaded 机器人插件
召唤并控制 carpet 假人
"""
from event import TRIGGER
import json, config, re, datetime
from textapi import CC

botlist=[]
trylist=[]
botlog=[]
loclist={}
helpstr = """Bot 机器人插件 帮助
!!bot help - 查看此帮助
!!bot view：列出所有 bot
!!bot add [-notp] <name> <注释>
 - 召唤一个名为 name 的机器人，若指定了 -notp，将不会将机器人传送至你而是最后的位置
!!bot kick <name> - 踢出名为 name 的机器人
!!bot kickall - 踢出所有bot。调试或服务器卡的时候用
!!bot save <name> - 保存名为 name 的机器人的位置
!!bot tp <name> - 让名为 name 的机器人传送至你
!!bot gm <name> c/s/sp - 切换名为 name 的机器人的游戏模式，c为创造，s为生存，sp为旁观 
!!bot tppos <name> <X> <Y> <Z> <dim>
 - 让名为 name 的机器人传送至该位置
 - 其中 dim 是 overworld, the_nether, the_end 中的一个，若没有指定，则默认为 overworld
!!bot action <name> <action> - 执行 bot 动作，参数列表可输入 !!bot actionlist 查看
!!bot log - 查看 bot 日志
"""
actionstr = """动作列表
attack/swapHands/use/jump every N/once/keep: 攻击/交换主副手/使用/跳跃 每 N ticks/仅此一次/一直
drop/dropStack all/mainhand/offhand/every N/once/keep: 扔出物品/扔出一组物品 扔出所有/扔出主手/扔出副手/每 N ticks 扔出主手/仅此一次扔出主手/一直扔出主手
sprint/sneak/unsneak/unsprint/stop/mount/dismount: 疾跑/潜行/取消疾跑/取消潜行/停止机器人所有操作/骑乘/取消骑乘
look east/west/south/north/up/down: 让机器人看对应方向
turn back/left/right: 让机器人转头
简单的例子：让一个机器人到凋零骷髅塔挂机：
首先 !!bot add Bot1 凋零骷髅塔
然后 !!bot tp Bot1 并扔给他牛排，输入 !!bot swapHands
然后扔给他一把掠夺3钻剑，并用不可堆叠物品塞满他的背包
然后你到对应的位置，把他tp过来，输入 !!bot attack every 20 让他每秒挥一次剑
输入 !!bot use keep 让他按住右键，饿了吃牛排
好了，现在你有一个一直挂机的机器人了，是不是很简单呢？
"""
def onload(ev,server,plugin):
  if ev["name"] == name:
    global botlist,loclist,botlog
    botlist = config.loadConfig("bot", [])
    if isinstance(botlist,dict):
      loclist = botlist["loc"]
      if "log" in botlist: botlog = botlist["log"]
      botlist = botlist["bot"]
    if botlist == {}: botlist = []
    rem = []
    if len(botlog) > 0 and len(botlog[0]) != 4: botlog = []
    for i in botlist:
      if i[1].lower() not in server.playerlist_lower:
        rem.append(i)
      if len(i) >= 4: i = i[:4]
    for i in rem: botlist.remove(i)
def onunload(ev,server,plugin):
  if ev["name"] == name:
    config.saveConfig("bot", {"bot":botlist,"loc":loclist,"log":botlog})
def storepos(server, bot, plugin):
  pos = plugin.getplugin("PlayerInfoAPI").getPlayerInfo(server,bot[1], "Pos")
  dim = plugin.getplugin("PlayerInfoAPI").getPlayerInfo(server,bot[1], "Dimension")
  rot = plugin.getplugin("PlayerInfoAPI").getPlayerInfo(server,bot[1], "Rotation")
  locc = [pos[0],pos[1],pos[2],dim,rot[0],rot[1]]
  global loclist
  loclist[bot[1]] = locc
def onjoin(ev,server,plugin):
  global botlist,trylist
  rem = []
  for bot in trylist:
    if ev["sender"].lower()==bot[1].lower():
      global botlog
      botlog.append([1, bot[0], bot[1], datetime.datetime.now().timestamp()])
      server.say(CC("[BOT] ", "d"), CC(bot[0], "f"), CC(" 召唤了机器人 ", "e"), CC(bot[1], "6"), CC(" 注释 ", "e"), CC(bot[2], "6"))
      rem.append(bot)
      botlist.append(bot)
      server.execute("gamemode 0 " + bot[1])
      if bot[3]: server.execute("tp " + bot[1] + " " + bot[0])
      elif bot[1] in loclist:
        lc = loclist[bot[1]]
        server.execute("execute in {0} run tp {1} {2} {3} {4} {5} {6}".format(["the_nether","overworld","the_end"][lc[3]+1],bot[1],lc[0],lc[1],lc[2],lc[4],lc[5]))
  for bot in rem: trylist.remove(bot)

def onleave(ev,server,plugin):
  global botlist
  rem = []
  for bot in botlist:
    if ev["sender"].lower()==bot[1].lower():
      server.say(CC("[BOT] ", "d"), CC("机器人 ", "e"), CC(bot[1], "6"), CC(" 离开了。","e"))
      rem.append(bot)
  for bot in rem: botlist.remove(bot)
def load_whitelist(server):
  filename = server.cfg["asd"] + "/whitelist.json"
  ret = []
  with open(filename,"r") as f:
    t = json.load(f)
    for i in t: ret.append(i["name"].lower())
  return ret
def checkname(server,name):
  t = load_whitelist(server)
  if name.lower() in t: return False
  global botlist, trylist
  for bot in botlist:
    if bot[1].lower() == name.lower(): return False
  for bot in trylist:
    if bot[1].lower() == name.lower(): return False
  return True
def add_bot(server, sender, name, lint, tp_here = True):
  if not checkname(server, name):
    server.tell(sender, CC("[BOT] ", "d"), CC("非法的用户名", "c"))
  else:
    server.tell(sender, CC("[BOT] ", "d"), CC("尝试召唤了机器人。如果10秒后没有加入游戏，说明不存在该正版id", "e"))
    server.execute("/player " + name + " spawn")
    global trylist
    trylist.append([sender, name, lint, tp_here])
def kick_bot(server, sender, name,plugin):
  global botlist
  for bot in botlist:
    if bot[1].lower()==name.lower():
      if bot[0].lower() != sender.lower() and sender not in ["ImSingularity", "ImLinDun", "Herbst_Q", "2233Cheers"]:
        server.tell(sender, CC("[BOT] ", "d"), CC("你不是这个 bot 的主人！", "e"))
        return
      server.tell(sender, CC("[BOT] ", "d"), CC("已发出 kick 申请", "e"))
      storepos(server,bot,plugin)
      global botlog
      botlog.append([0, sender, bot[1], datetime.datetime.now().timestamp()])
      server.execute("/player "+bot[1]+" kill")
      return
  server.tell(sender, CC("[BOT] ", "d"), CC("不存在该bot！", "c"))
def save_bot(server, sender, name,plugin):
  global botlist
  for bot in botlist:
    if bot[1].lower()==name.lower():
      if bot[0].lower() != sender.lower() and sender not in ["ImSingularity", "ImLinDun", "Herbst_Q", "2233Cheers"]:
        server.tell(sender, CC("[BOT] ", "d"), CC("你不是这个 bot 的主人！", "e"))
        return
      server.tell(sender, CC("[BOT] ", "d"), CC("已发出 save 申请", "e"))
      storepos(server,bot,plugin)
      return
  server.tell(sender, CC("[BOT] ", "d"), CC("不存在该bot！", "c"))
def gm_bot(server, sender, name,gm, plugin):
  global botlist
  for bot in botlist:
    if bot[1].lower()==name.lower():
      if bot[0].lower() != sender.lower() and sender not in ["ImSingularity", "ImLinDun", "Herbst_Q", "2233Cheers"]:
        server.tell(sender, CC("[BOT] ", "d"), CC("你不是这个 bot 的主人！", "e"))
        return
      server.tell(sender, CC("[BOT] ", "d"), CC("已发出 gamemode 申请", "e"))
      if gm=="c": bot[3] = False
      else: bot[3] = True
      server.execute("/gm{0} {1}".format(gm, bot[1]))
      return
  server.tell(sender, CC("[BOT] ", "d"), CC("不存在该bot！", "c"))

def kickall_bot(server, sender,plugin):
  if sender not in ["ImSingularity", "ImLinDun", "2233Cheers", "Herbst_Q", False]:
    server.tell(sender, CC("[BOT] ", "d"), CC("你没有 kickall 的权限", "e"))
    return
  global botlist
  for bot in botlist:
    server.tell(sender, CC("[BOT] ", "d"), CC("已发出 kick " ,"e"),CC(bot[1],"6"),CC(" 申请", "e"))
    storepos(server,bot,plugin)
    global botlog
    botlog.append([0, sender, bot[1], datetime.datetime.now().timestamp()])
    server.execute("/player "+bot[1]+" kill")
def tp_bot(server,sender,name):
  global botlist
  for bot in botlist:
    if bot[1].lower()==name.lower():
      if bot[0].lower() != sender.lower():
        server.tell(sender, CC("[BOT] ", "d"), CC("你不是这个 bot 的主人！", "c"))
        return
      server.tell(sender, CC("[BOT] ", "d"), CC("已发出 tp 申请", "e"))
      server.execute("/tp "+bot[1]+" "+sender)
      return
  server.tell(sender, CC("[BOT] ", "d"), CC("不存在该bot！", "c"))
def tppos_bot(server,sender,name,x,y,z,dim):
  global botlist
  for bot in botlist:
    if bot[1].lower()==name.lower():
      if bot[0].lower() != sender.lower():
        server.tell(sender, CC("[BOT] ", "d"), CC("你不是这个 bot 的主人！", "c"))
        return
      server.tell(sender, CC("[BOT] ", "d"), CC("已发出 tp [{0},{1},{2} {3}] 申请".format(x,y,z,dim), "e"))
      server.execute("/execute in {0} run tp {1} {2} {3} {4}".format(dim,bot[1],x,y,z))
      return
  server.tell(sender, CC("[BOT] ", "d"), CC("不存在该bot！", "c"))
def check_bot(server, sender, name):
  global botlist
  for bot in botlist:
    if bot[1].lower()==name.lower():
      if bot[0].lower() != sender.lower():
        server.tell(sender, CC("[BOT] ", "d"), CC("你不是这个 bot 的主人！", "e"))
        return False
      if bot[3] == False:
        server.tell(sender, CC("[BOT] ", "d"), CC("该 bot 处于创造模式！", "e"))
        return False
        
      return True
  server.tell(sender, CC("[BOT] ", "d"), CC("不存在该bot！", "c"))
  return False
def view_bot(server, sender):
  global botlist
  for bot in botlist:
    server.tell(sender, CC("[BOT] ", "d"), CC(bot[1], "6"), CC(" 召唤者 ","e"), CC(bot[0], "f"), CC(" 说明: ", "e"), CC(bot[2], "f"))
def log_bot(server, sender):
  global botlog
  for log in botlog:
    server.tell(sender, CC("[BOT] ", "d"), CC("{0}  玩家 ".format(datetime.datetime.fromtimestamp(log[3]).strftime("%m-%d %H:%M:%S %p")), "e"), CC("console" if log[1] == False else log[1], "f"), CC(" 召唤 " if log[0] == 1 else " 踢出 ","e"), CC(log[2], "6"))
def act_bot(server,sender,name,act,cot):
  server.execute("/player " + name + " " + act + " " + cot.replace("every", "interval").replace("keep", "continuous"))
  server.tell(sender, CC("已发出 ","e"), CC(act+ " " + cot,"6"), CC(" 动作申请","e"))
def act2_bot(server,sender,name,act):
  server.execute("/player " + name + " " + act)
  server.tell(sender, CC("已发出 ","e"), CC(act,"6"), CC(" 动作申请","e"))
def oninfo(ev,server,plugin):
  if ev["content"] == "!!bot":
    for i in helpstr.split("\n"): server.tell(ev["sender"], CC(i, "e"))
    return
  if not ev["content"].startswith("!!bot "): return
  if ev["content"] == "!!bot help":
    for i in helpstr.split("\n"): server.tell(ev["sender"], CC(i, "e"))
  else:

    if re.match(r"^!!bot add (-notp |)([0-9A-Za-z_]{3,16}) (\S+)$", ev["content"]):
      m = re.match(r"^!!bot add (-notp |)([0-9A-Za-z_]{3,16}) (\S+)$", ev["content"])
      if m.group(1) != "": add_bot(server, ev["sender"], m.group(2), m.group(3), False)
      else: add_bot(server, ev["sender"], m.group(2), m.group(3))
    elif re.match(r"^!!bot save ([0-9A-Za-z_]{3,16})$", ev["content"]):
      save_bot(server, ev["sender"], re.match(r"^!!bot save ([0-9A-Za-z_]{3,16})$", ev["content"]).group(1),plugin)
    elif re.match(r"^!!bot gm ([0-9A-Za-z_]{3,16}) (c|s|sp)$", ev["content"]):
      r = re.match(r"^!!bot gm ([0-9A-Za-z_]{3,16}) (c|s|sp)$", ev["content"])
      gm_bot(server, ev["sender"], r.group(1), r.group(2), plugin)
    elif re.match(r"^!!bot kick ([0-9A-Za-z_]{3,16})$", ev["content"]):
      kick_bot(server, ev["sender"], re.match(r"^!!bot kick ([0-9A-Za-z_]{3,16})$", ev["content"]).group(1),plugin)
    elif re.match(r"^!!bot kickall$", ev["content"]):
      kickall_bot(server, ev["sender"],plugin)
    elif re.match(r"^!!bot tp ([0-9A-Za-z_]{3,16})$", ev["content"]):
      tp_bot(server, ev["sender"], re.match(r"^!!bot tp ([0-9A-Za-z_]{3,16})$", ev["content"]).group(1))
    elif re.match(r"^!!bot tppos ([0-9A-Za-z_]{3,16}) ((?:-?[0-9](?:\.[0-9]+)?)+) ((?:-?[0-9](?:\.[0-9]+)?)+) ((?:-?[0-9](?:\.[0-9]+)?)+) (|overworld|the_end|the_nether)$", ev["content"]):
      m = re.match(r"^!!bot tppos ([0-9A-Za-z_]{3,16}) ((?:-?[0-9](?:\.[0-9]+)?)+) ((?:-?[0-9](?:\.[0-9]+)?)+) ((?:-?[0-9](?:\.[0-9]+)?)+) (|overworld|the_end|the_nether)$", ev["content"])
      tppos_bot(server, ev["sender"], m.group(1), m.group(2),m.group(3),m.group(4),m.group(5) if m.group(5)!="" else "overworld")
    elif re.match(r"^!!bot actionlist$", ev["content"]):
      for i in actionstr.split("\n"): server.tell(ev["sender"], CC(i, "e"))
    elif re.match(r"^!!bot view$", ev["content"]):
      view_bot(server,ev["sender"])
    elif re.match(r"^!!bot log$", ev["content"]):
      log_bot(server,ev["sender"])
    elif re.match(r"^!!bot action ([0-9A-Za-z_]{3,16}) (attack|swapHands|use|jump) (every [0-9]+|once|keep)$", ev["content"]):
      m = re.match(r"^!!bot action ([0-9A-Za-z_]{3,16}) (attack|swapHands|use|jump) (every [0-9]+|once|keep)$", ev["content"])
      if check_bot(server, ev["sender"], m.group(1)): act_bot(server, ev["sender"], m.group(1), m.group(2), m.group(3))
    elif re.match(r"^!!bot action ([0-9A-Za-z_]{3,16}) (drop|dropStack) (all|mainhand|offhand|every [0-9]+|once|keep)$", ev["content"]):
      m = re.match(r"^!!bot action ([0-9A-Za-z_]{3,16}) (drop|dropStack) (all|mainhand|offhand|every [0-9]+|once|keep)$", ev["content"])
      if check_bot(server, ev["sender"], m.group(1)): act_bot(server, ev["sender"], m.group(1), m.group(2), m.group(3))
    elif re.match(r"^!!bot action ([0-9A-Za-z_]{3,16}) (sprint|sneak|unsneak|unsprint|stop|mount|dismount)$", ev["content"]):
      m = re.match(r"^!!bot action ([0-9A-Za-z_]{3,16}) (sprint|sneak|unsneak|unsprint|stop|mount|dismount)$", ev["content"])
      if check_bot(server, ev["sender"], m.group(1)): act2_bot(server, ev["sender"], m.group(1), m.group(2))
    elif re.match(r"^!!bot action ([0-9A-Za-z_]{3,16}) (look) (east|west|south|north|up|down)$", ev["content"]):
      m = re.match(r"^!!bot action ([0-9A-Za-z_]{3,16}) (look) (east|west|south|north|up|down)$", ev["content"])
      if check_bot(server, ev["sender"], m.group(1)): act_bot(server, ev["sender"], m.group(1), m.group(2), m.group(3))
    elif re.match(r"^!!bot action ([0-9A-Za-z_]{3,16}) (move) (forward|backward|left|right)$", ev["content"]):
      m = re.match(r"^!!bot action ([0-9A-Za-z_]{3,16}) (move) (forward|backward|left|right)$", ev["content"])
      if check_bot(server, ev["sender"], m.group(1)): act_bot(server, ev["sender"], m.group(1), m.group(2), m.group(3))
    elif re.match(r"^!!bot action ([0-9A-Za-z_]{3,16}) (turn) (back|left|right)$", ev["content"]):
      m = re.match(r"^!!bot action ([0-9A-Za-z_]{3,16}) (turn) (back|left|right)$", ev["content"])
      if check_bot(server, ev["sender"], m.group(1)): act_bot(server, ev["sender"], m.group(1), m.group(2), m.group(3))
    else:
      server.tell(ev["sender"], CC("[BOT] ","d"), CC("不存在该指令或参数不合法。请检查输入！", "c"))


name = "BotPlugin"
listener = [
  {"type": TRIGGER.PLAYER_INFO, 'func': oninfo},
  {"type": TRIGGER.PLAYER_JOIN, 'func': onjoin},
  {"type": TRIGGER.PLAYER_LEAVE, 'func': onleave},
  {"type": TRIGGER.PLUGIN_LOADED, 'func': onload},
  {"type": TRIGGER.PLUGIN_UNLOADING, 'func': onunload}
]
