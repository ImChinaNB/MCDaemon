# -*- coding: utf-8 -*-

import json, os, time
import urllib.request, urllib.error, urllib.parse
from textapi import CC

name = 'StatsPlugin'
ScoreboardName = 'stats'
UUIDFile = 'config/uuid.json'
RankAmount = 15
rankColor = ['§b', '§d', '§e', '§f']
HelpMessage = """MCDaemonReloaded Stats 插件
帮助你查询/排名/使用计分板列出各类统计信息。
§a【格式说明】§r
§7!!stats§r 显示帮助信息
§7!!stats query §b[玩家] §6[统计类别] §e[统计内容]§r
§7!!stats rank §6[统计类别] §e[统计内容] §7(-bot)§r
§7!!stats scoreboard §6[统计类别] §e[统计内容] §7(-bot)§r
§7!!stats scoreboard show§r 显示该插件的计分板
§7!!stats scoreboard hide§r 隐藏该插件的计分板
§7!!stats refreshUUID§r 刷新玩家UUID列表，插件重载后使用
§a【参数说明】§r
§6[统计类别]§r: §6killed§r, §6killed_by§r, §6dropped§r, §6picked_up§r, §6used§r, §6mined§r, §6broken§r, §6crafted§r, §6custom§r
§6killed§r, §6killed_by§r 的 §e[统计内容] §r为 §e[生物id]§r
§6picked_up§r, §6used§r, §6mined§r, §6broken§r, §6crafted§r 的 §e[统计内容]§r 为 §e[物品/方块id]§r
§6custom§r 的 §e[统计内容]§r 详见统计信息的json文件
上述内容无需带minecraft前缀
§7(-bot)§r: 统计bot; §7(-all)§r: 列出所有项
§a【例子】§r
§7!!stats query §b2233Cheers §6used §ewater_bucket§r
§7!!stats rank §6custom §etime_since_rest §7-bot§r
§7!!stats scoreboard §6mined §estone§r
"""

UUID = {}

def name_to_uuid_fromAPI(name):
    url = 'http://tools.glowingmines.eu/convertor/nick/' + name
    response = urllib.request.urlopen(url)
    data = response.read()
    js = json.loads(str(data))
    return js['offlinesplitteduuid']

def name_to_uuid(name):
    global UUID
    if name in UUID:
        return UUID[name]
    UUID[name] = name_to_uuid_fromAPI(name)
    return UUID[name]

def refreshUUIDList(server, showTip=False):
    global UUID
    UUID_file = {}
    UUID_cache = {}
    if os.path.isfile(UUIDFile):
        UUID_file = json.load(open(UUIDFile, 'r'))
    if os.path.isfile('fabric/usercache.json'):
        with open('fabric/usercache.json', 'r') as f:
            try:
                js = json.load(f)
            except ValueError:
                server.say('[Stats] 错误：无法打开或解析 UUID 文件！')
                return False
            for i in js:
                UUID_cache[i['name']] = i['uuid']
    UUID = dict(UUID, **dict(UUID_cache, **UUID_file))
    json.dump(UUID, open(UUIDFile, 'w'))
    if server != None and showTip:
        server.say('[Stats] UUID 列表刷新完成，加载了 ' + str(len(UUID)) + ' 个 UUID！')


def isBot(name):
    blacklist = '#Notch##########'
    blackkey = ['bot_', 'bot-']
    if blacklist.find(name) >= 0: return True
    if len(name) < 4 or len(name) > 16: return True
    for i in blackkey:
        if name.find(i) >= 0:
            return True
    return False

def getStatsData(uuid, classification, target):
    jsonfile = 'fabric/world/stats/' + uuid + '.json'
    if not os.path.isfile(jsonfile):
        return (0, False)

    with open(jsonfile, 'r') as f:
        try:
            js = json.load(f)
        except ValueError:
            return (0, False)
        try:
            data = js['stats']['minecraft:' + classification]['minecraft:' + target]
        except KeyError:
            return (0, False)
        return (data, True)


def getPlayerList(listBot):
    global UUID
    ret = []
    for i in list(UUID.items()):
        if listBot or not isBot(i[0]):
            ret.append(i)
    return ret


def triggerSaveAll(server):
    server.execute('save-all')
    time.sleep(0.2)


def getString(classification, target):
    return '§6' + classification + '§r.§e' + target + '§r'

def showStats(server, name, classification, target):
    uuid = name_to_uuid(name)

    data = getStatsData(uuid, classification, target)

    msg = '[Stats] 玩家§b' + name + '§r的统计信息[' + getString(classification, target) + ']的值为§a' + str(data) + '§r'
    server.say(msg)


def showRank(server, classification, target, listBot, isAll):
    getPlayerListResult = getPlayerList(listBot)
    arr = []
    sum = 0
    for player in getPlayerListResult:
        ret = getStatsData(player[1], classification, target)
        if ret[1] and ret[0] > 0:
            data = ret[0]
            arr.append((player[0], data))
            sum += data

    if len(arr) == 0:
        server.say('[Stats] 未找到该统计项或该统计项全空！')
    arr.sort(key=lambda x: x[0])
    arr.reverse()
    arr.sort(key=lambda x: x[1])
    arr.reverse()

    showRange = min(RankAmount + isAll * len(arr), len(arr))
    server.say('[Stats] 统计信息[{}]的总数为§c{}§r，前{}名为'.format(getString(classification, target), str(sum), str(showRange)))
    maxNameLength = 0
    for i in range(0, showRange):
        maxNameLength = max(maxNameLength, len(str(arr[i][1])))
    for i in range(0, showRange):
        s = '#' + str(i + 1) + ' ' * (4 - len(str(i + 1))) + \
              str(arr[i][1]) + ' ' * (maxNameLength - len(str(arr[i][1])) + 2) + \
              str(arr[i][0])
        server.say(rankColor[min(i, len(rankColor) - 1)] + s)

def showScoreboard(server):
    server.execute('scoreboard objectives setdisplay sidebar ' + ScoreboardName)


def hideScoreboard(server):
    server.execute('scoreboard objectives setdisplay sidebar')


def buildScoreboard(server, classification, target, listBot):
    playerList = getPlayerList(listBot)
    triggerSaveAll(server)
    server.execute('scoreboard objectives remove ' + ScoreboardName)
    server.execute('scoreboard objectives add ' + ScoreboardName + ' ' +
                   'minecraft.' + classification + ':minecraft.' + target +
                   ' {"text":"§6' + classification + '§r.§e' + target + '"}')
    for player in playerList:
        ret = getStatsData(player[1], classification, target)
        if ret[1]:
            server.execute('scoreboard players set ' + player[0] + ' ' + ScoreboardName + ' ' + str(ret[0]))
    showScoreboard(server)

def onServerInfo(info, server, plugin):
    content = info["content"]
    listBot = content.find('-bot') >= 0
    content = content.replace('-bot', '')
    isAll = content.find('-all') >= 0
    content = content.replace('-all', '')
    command = content.split()
    
    if len(command) == 0 or command[0] != "!!stats":
        return
    del command[0]

    if len(command) == 0:
        server.say(HelpMessage)
        return

    cmdlen = len(command)
    # query [玩家] [统计类别] [统计内容] (-uuid)
    if cmdlen == 4 and command[0] == 'query':
        showStats(server, command[1], command[2], command[3])
    # rank [统计类别] [统计内容] (过滤bot前缀)
    elif cmdlen == 3 and command[0] == 'rank':
        showRank(server, command[1], command[2], listBot, isAll)
    elif cmdlen == 3 and command[0] == 'scoreboard':
        buildScoreboard(server, command[1], command[2], listBot)
    elif cmdlen == 2 and command[0] == 'scoreboard' and command[1] == 'show':
        showScoreboard(server, info)
    elif cmdlen == 2 and command[0] == 'scoreboard' and command[1] == 'hide':
        hideScoreboard(server, info)
    elif cmdlen == 1 and command[0] == 'refreshUUID':
        refreshUUIDList(server, True)
    else:
        server.say('[Stats] 参数错误！请输入 !!stats 以获取插件帮助')


def onServerStartup(info, server, plugin):
    refreshUUIDList(server)

def onPlayerJoin(info, server, plugin):
    refreshUUIDList(server)

def test(info, server, plugin):
  if info["name"] == name:
    refreshUUIDList(server)

from event import TRIGGER
listener = [
    {"type": TRIGGER.PLAYER_INFO, "func": onServerInfo},
    {"type": TRIGGER.SERVER_STARTED, "func": onServerStartup},
    {"type": TRIGGER.PLAYER_JOIN, "func": onPlayerJoin},
    {"type": TRIGGER.PLUGIN_LOADED, "func": test}
]
