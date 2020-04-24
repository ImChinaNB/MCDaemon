"""
MCDaemonReloaded 服务器 增量备份插件 (Increasing Backup)
提供多个槽位的增量备份与回档功能。
要求 rdiff-backup.
"""
import config, uuid, json, os, time, shlex, datetime
from pathlib import Path
from event import TRIGGER
from subprocess import Popen
from textapi import CC

cfg = config.loadConfig("backup", {"world": "", "slot": "16", "backupdir": "/backup", "backupwhenrollback": True, "logfile": "rdiff.log", "backups": []})
aborted = False
confirmed = False
inProgress = False
savedGame = False
dest = None

def syncBackupList():
  global cfg
  fl = []
  tf = {}
  newest = None
  newesttime = -1
  newesttimee = -1
  havelatest = False
  havelatestdescription = False
  for bk in cfg["backups"]:
    if bk["file"]: tf[bk["file"]] = bk["description"]
    elif bk["file"] == False:
      havelatest = True
      havelatestdescription = bk["description"]
  for path in Path(cfg['backupdir'] + '/rdiff-backup-data/').glob('./increments.*.dir'):
    if path.is_file():
      if path.stat().st_mtime > newesttimee:
        newesttimee = path.stat().st_mtime
      if path.parts[-1] in tf: fl.append({"file": path.parts[-1], "description": tf[path.parts[-1]], "time": path.stat().st_mtime})
      elif path.stat().st_mtime > newesttime:
        newest = path.parts[-1]
        newesttime = path.stat().st_mtime
  if havelatest and newest != None and newesttimee == newesttime: fl.append({"file": newest, "description": havelatestdescription, "time": newesttime})
  if havelatest and newest == None: fl.append({"file": False, "description": havelatestdescription, "time": int(datetime.datetime.now().timestamp())})
  fl.sort(key=lambda x: x['time'], reverse=True)
  cfg["backups"] = fl
def runCmd(cmd):
  t = Popen(shlex.split(cmd))
  t.wait()
  return t.returncode

def doBackup(description, removeOld = True):
  global cfg
  if runCmd("rdiff-backup " + cfg["world"] + " " + cfg["backupdir"]) == 0: # rdiff-backup /home/mc/fabric/world* /backup/
    if removeOld: runCmd("rdiff-backup --force --remove-older-than " + cfg["slot"] + "B " + cfg["backupdir"])
    syncBackupList()
    cfg['backups'].append({'file': False, 'description': description, 'time':0})
    syncBackupList()
    return True
  else:
    syncBackupList()
    return False
def doRestore(filen):
  global cfg
  # rdiff-backup host.net::/remote-dir/rdiff-backup-data/increments/file.2003-03-05T12:21:41-07:00.diff.gz local-dir/file
  if filen == False or Path(cfg['backupdir'] + '/rdiff-backup-data/' + filen).is_file():
    print("[IB] 备份原存档...")
    if cfg["backupwhenrollback"]:
      if doBackup("回档前自动备份", False) and filen == False:
        filen = cfg['backups'][0]['file']
    print("[IB] 开始回档...")
    cmd = "rdiff-backup --force " + ("-r now" + cfg['backupdir']) if filen == False else (cfg['backupdir'] + '/rdiff-backup-data/' + filen) + " " + cfg["world"]
    if runCmd("rm -rf " + cfg["world"]) == 0:
      return bool(runCmd(cmd))
    else: return False
  else:
    return False
def makeBackup(server, description = ""):
  global inProgress, savedGame
  if inProgress:
    server.say(CC("[IB] ","a"), CC("已经在进行备份或回档，请勿重复操作！", "cl"))
    return
  inProgress = True
  server.say(CC("[IB] ","a"), CC("开始备份，正在保存世界...", "e"))
  server.execute("save-off")
  savedGame = False
  server.execute("save-all")
  for i in range(10000):
    time.sleep(0.01)
    if savedGame: break
  server.say(CC("[IB] ","a"), CC("保存完毕，开始备份世界！", "e"))
  server.say(CC("[IB] ","a"), CC("备份 >> 执行 rdiff-backup...", "e"))
  res = doBackup(description)
  if res:
    server.say(CC("[IB] ","a"), CC("备份 >> 同步增量文件...", "e"))
    server.say(CC("[IB] ","a"), CC("备份 <","e"), CC(description, "f"), CC("> 备份完毕！", "e"))
  else:
    server.say(CC("[IB] ","a"), CC("备份失败！请联系服务器管理员查询原因。", "e"))
  server.execute("save-on")
  savedGame = False
  inProgress = False
def makeRestore(server, slot):
  global inProgress, savedGame, cfg, confirmed, dest, aborted
  if inProgress:
    server.say(CC("[IB] ","a"), CC("已经在进行备份或回档，请勿重复操作！", "cl"))
    return
  try:
    idd = int(slot)
    if cfg['backups'][idd]['file'] != '':
      inProgress = True
      server.say(CC("[IB] ","a"), CC("将要回档到 <", "e"), CC(cfg['backups'][idd]['description'], 'f'), CC('> ', 'e'), CC(cfg['backups'][idd]['file'], 'f'), CC('，是否继续？在 20 秒内输入 !!ib confirm 确认操作。', 'e'))
  except:
    server.say(CC("[IB] ","a"), CC("输入的槽位有误！请检查。", "c"))
    return
  confirmed = False
  dest = cfg['backups'][int(slot)]['file']
  for i in range(2000):
    time.sleep(0.01)
    if confirmed: break
  if not confirmed:
    dest = None
    inProgress = False
    server.say(CC("[IB] ","a"), CC("确认超时，回档已取消。", "e"))
    return
  server.say(CC("[IB] ","a"), CC("开始回档，正在保存世界...", "e"))
  server.execute("save-off")
  savedGame = False
  server.execute("save-all")
  for i in range(10000):
    time.sleep(0.01)
    if savedGame: break
  server.say(CC("[IB] ","a"), CC("保存完毕，开始进行回档！10 秒后执行关服操作...", "e"))
  server.say(CC("[IB] ","a"), CC("输入 !!ib a 或 !!ib abort 以停止回档！", "e"))
  server.say(CC("[IB] ","a"), CC("如果服务器在 3 分钟内没有启动请联系管理！", "e"))
  aborted = False
  for i in range(1000):
    time.sleep(0.01)
    if aborted: break
  if aborted:
    inProgress = False
    dest = None
    server.say(CC("[IB] ","a"), CC("回档已被终止。", "e"))
    return
  print("[IB] 回档中:", inProgress, " 目标文件:", dest)
  server.stop()

def onstopped(ev,server,plugin):
  global inProgress, dest
  print("[IB] 服务器停止了。正在检测回档情况...")
  print("[IB] 回档中:", inProgress, " 目标文件:", dest)
  
  if inProgress and dest is not None: # 继续回档
    print("[IB] 继续回档操作。正在回档...")
    if doRestore(dest):
      print("[IB] 回档成功。启动服务器。")
      server.start()
    else:
      print("[IB] 回档失败。服务器将处于停滞状态。")
    
    dest = None
    inProgress = False

def printhelp(server):
  global cfg, inProgress
  if not inProgress:
    for t in """Increasing Backup 帮助
!!ib help - 查看此帮助
!!ib backup <说明> - 建立新备份
!!ib restore <ID> - 回档到 <ID>
!!ib view - 查看所有备份
!!ib refresh - 手动刷新备份列表-不推荐使用
!!ib confirm/abort 确认/取消 回档操作。""".split("\n"): server.say(CC(t,"e"))

def makeView(server):
  global cfg, inProgress
  if not inProgress:
    server.say(CC("[IB] ","a"), CC("下面为所有的备份：(ID/说明)", "e"))
    for i,j in enumerate(cfg["backups"]):
      server.say(CC(str(i), "d"), CC(" / ", "f"), CC("无说明" if j["description"].strip()=="" else j["description"], "e"), CC(" / ", "f"), CC(datetime.datetime.fromtimestamp(int(j["time"])).strftime('%Y.%m.%d %H:%M:%S')))
def refreshView(server):
  global cfg, inProgress
  if not inProgress:
    syncBackupList()
    server.say(CC("[IB] ","a"), CC("刷新完毕。", "e"))

def makeConfirm(server, user):
  if user not in ["ImSingularity", "2233Cheers", "ImLinDun", False]:
    server.tell(user, CC("[IB] ","a"), CC("你没有确认回档的权限。", "c"))
  else:
    global confirmed, dest
    if inProgress and dest is not None: confirmed = True
    else: server.tell(user, CC("[IB] ","a"), CC("没有什么可确认的。", "c"))
def makeAbort(server):
  global aborted
  if inProgress and dest is not None: aborted = True

def oncmd(ev, server, plugin):
  t = ev["content"]
  if not t.startswith("!!ib"): return
  g = t.split(" ")
  if (len(g) == 2 and g[1] == "help") or (len(g) == 1):
    printhelp(server)
  elif (len(g) >= 2 and g[1] == "view"):
    makeView(server)
  elif (len(g) >= 2 and g[1] == "backup"):
    if len(g) == 2: makeBackup(server)
    else: makeBackup(server, ' '.join(g[2:]))
  elif (len(g) >= 3 and g[1] == "restore"):
    makeRestore(server, g[2])
  elif (len(g) >= 2 and g[1] == "confirm"):
    makeConfirm(server, ev["sender"])
  elif (len(g) >= 2 and g[1] == "refresh"):
    refreshView(server)
  elif (len(g) >= 2 and g[1].startswith("a")):
    makeAbort(server)
  else:
    server.say(CC("[IB] ", "a"), CC("错误的或不存在的指令。输入 !!ib help 查看命令帮助。"))
def oninfo(ev, server,plugin):
  global savedGame, inProgress
  if ev["content"].startswith('Saved the game') and inProgress:
    savedGame = True
def onunload(ev,server,plugin):
  config.saveConfig("backup", cfg)
listener = [
  {"type": TRIGGER.SERVER_STOPPED, "func": onstopped},
  {"type": TRIGGER.PLAYER_INFO, "func": oncmd},
  {"type": TRIGGER.SERVER_INFO, "func": oninfo},
  {"type": TRIGGER.PLUGIN_UNLOADING, "func": onunload}
]
name = "BackupPlugin"
