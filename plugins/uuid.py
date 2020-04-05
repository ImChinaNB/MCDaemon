"""
MCDaemonReloaded 服务器 UUID 转换插件
提供 UUID 与玩家名的转换。
"""
import config
import uuid,json
from event import TRIGGER
cfg = {
  "usercache": "",
  "offline": False,
  "u": {},  # uuid to name
  "c": {}  # name to uuid
}

class NULL_NAMESPACE:
    bytes = b''

def loaded(ev, server, plugin):
  if ev["name"] == name:
    cfg = config.loadConfig("uuid", cfg)
    cfg["offline"] = server.offline_login
    if cfg["usercache"] == "": cfg["usercache"] = server.cfg["aswd"] + "/usercache.json"

def unloading(ev, server, plugin):
  if ev["name"] == name:
    config.saveConfig("uuid", cfg)

def uuidfromapi(name):
  try:
    js = json.loads(str(urllib.request.urlopen(
        'http://tools.glowingmines.eu/convertor/nick/' + name).read()))
    return js['offlinesplitteduuid']
  except:
    return False
def namefromapi(uuid):
  try:
    js = json.loads(str(urllib.request.urlopen(
        'http://tools.glowingmines.eu/convertor/uuid/' + uuid).read()))
    return js['nick']
  except:
    return False

def uuidfromoffline(name):
  return str(uuid.uuid3(NULL_NAMESPACE, "OfflinePlayer:" + name))

def refreshcache():
  with open(cfg["usercache"], 'r') as f:
    try:
      js = json.load(f)
    except ValueError:
      return False
  for i in js:
    cfg["u"][i['uuid'].lower()] = i['name']
    cfg["c"][i['name'].lower()] = i['uuid'].lower()
def uuidfromcache(name):
  refreshcache()
  if name.lower() in cfg["c"]: return cfg["c"][name.lower()]
  else: return False
def namefromcache(uuid):
  refreshcache()
  if uuid.lower() in cfg["u"]: return cfg["u"][uuid.lower()]
  else: return False

def _uuid2name(uuid):
  t = namefromcache(uuid)
  if t: return t
  else:
    if cfg["offline"]: return False
    else: return namefromapi(uuid)
def _name2uuid(name):
  t = uuidfromcache(name)
  if t: return t
  else:
    if cfg["offline"]: return uuidfromoffline(name)
    else: return uuidfromapi(uuid)
def uuid2name(uuid):
  t = _uuid2name(uuid)
  if t:
    cfg["c"][t.lower()] = uuid.lower()
    cfg["u"][uuid.lower()] = t
  return t
def name2uuid(name):
  t = _name2uuid(name)
  if t:
    cfg["c"][name.lower()] = t
    cfg["u"][t.lower()] = name.lower()
  return t

listener = [
  {"type": TRIGGER.PLUGIN_LOADED, "func": loaded},
  {"type": TRIGGER.PLUGIN_UNLOADING, "func": unloading}
]
name = "UUIDPlugin"
