"""
MCDaemonReloaded 服务器 UUID 转换插件
提供 UUID 与玩家名的转换。
"""

cache = 'config/uuid.json'
c = {}
ac = {}


def fromapi(name):
  try:
    js = json.loads(str(urllib.request.urlopen('http://tools.glowingmines.eu/convertor/nick/' + name).read()))
    return js['offlinesplitteduuid']
  except:
    return False
def from