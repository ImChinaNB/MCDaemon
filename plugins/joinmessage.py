"""
MCDaemonReloaded 进服插件
用于广播进服信息。
"""
from event import TRIGGER
from textapi import CC
from plugins.daycount import getday

def onjoin(ev, server, plugin):
  server.tell(ev["sender"], CC("=======", "7"), CC(" 欢迎回到","r"),CC(" HTS","e"),CC(" =======", "7"))
  server.tell(ev["sender"], CC("今天是"), CC(" HTS ","e"),CC("开服的第","r"),CC(getday(),"e"),CC("天","r"))
  server.tell(ev["sender"], CC("-------","7"),CC(" 祝您爆肝愉快 xD ","r"),CC("-------","7"))
  server.tell(ev["sender"], CC("MCDR 更新日志 [巨大更新 25%] (4/24 6:28 PM COMMITED)："))
  server.tell(ev["sender"], CC("1)  修复 !!ib 无法使用的问题"))
  server.tell(ev["sender"], CC("2)  让机器人召唤时可以不被传送到你所在位置，添加 !!bot tppos 指令"))
  server.tell(ev["sender"], CC("3)* 部分人员现在可以踢出非自己召唤的机器人了 *注：helper 包括 (ImSingularity, ImLinDun, Herbst_Q, 2233Cheers)，需要可以来申请"))
  server.tell(ev["sender"], CC("4)^ 添加玩家死亡以及进出服务器，改变维度的日志，并自动合并同类项，删除 5 天前的记录"))
  server.tell(ev["sender"], CC("5)^ 添加扫地姬，在玩家死亡后自动停止，并能够添加玩家死亡忽略名单和物品白名单（用于挖山啥的）"))
  server.tell(ev["sender"], CC("6)  修复 !!self rightclick 无法使用的问题"))
  server.tell(ev["sender"], CC("*)  条目数字后有 * 的表示管理更新，有 ^ 的表示仍处于测试阶段。"))

listener = [
  {"type": TRIGGER.PLAYER_JOIN, "func": onjoin}
]
name = "JoinMessagePlugin"
