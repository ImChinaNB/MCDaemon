from event import TRIGGER
from utils import CC
from urllib.parse import quote

def oninfo(ev, server, plugin):
  if ev['sender'] == False: return
  if ev["content"].startswith("=? "):
    search_content = ev["content"][3:]
    server.execute('tellraw ' + ev['sender'] + ' {"text":"Wiki: 搜索 §6' + search_content + '§r 的结果","underlined":"false","clickEvent":{"action":"open_url","value":"https://minecraft-zh.gamepedia.com/index.php?search=' + quote(search_content) + '"}}')
  elif ev["content"].startswith("=! "):
    search_content = ev["content"][3:]
    server.execute('tellraw ' + ev['sender'] + ' {"text":"BiliWiki: 搜索 §6' + search_content + '§r 的结果","underlined":"false","clickEvent":{"action":"open_url","value":"https://searchwiki.biligame.com/mc/index.php?search=' + quote(search_content) + '"}}')

name = "WikiPlugin"
listener = [
  {"type": TRIGGER.PLAYER_INFO, "func": oninfo}
]
