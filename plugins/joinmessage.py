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
  server.tell(ev["sender"], CC("MCDR 更新日志 [巨大更新 50%]：", "e"))
  server.tell(ev["sender"], CC("1)! 修复 MCDR 后台 thread.join() 卡死重载线程的 bug"))
  server.tell(ev["sender"], CC("2)  !!here 能够导入到 VoxelMap"))
  server.tell(ev["sender"], CC("3)  添加了 !!loc ex 指令，能够导入坐标点到 VoxelMap"))
  server.tell(ev["sender"], CC("4)  召唤bot时，使用-notp将会将其传至上次位置"))
  server.tell(ev["sender"], CC("5)  添加 !!bot log 用于查询bot召唤、踢出日志"))
  server.tell(ev["sender"], CC("6)  添加 !!whereis 用于查询他人位置"))
  server.tell(ev["sender"], CC("7)  添加 !!help"))
  server.tell(ev["sender"], CC("*)  条目数字后有 * 的表示管理更新，有 ^ 的表示仍处于测试阶段，有 ! 的表示为重要安全或功能修复。"))
  server.tell(ev["sender"], CC("*)  由于测试时可能的误操作或者捣乱等问题，处于测试阶段的指令不公开，在其稳定后才会公开。"))

listener = [
  {"type": TRIGGER.PLAYER_JOIN, "func": onjoin}
]
name = "JoinMessagePlugin"
