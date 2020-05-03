from event import TRIGGER
from utils import CC

lines = """可用指令有（一般的，输入!!<指令> help 可查看对应帮助）:
!!bot - 机器人管理
!!dropman - 掉落物管理
!!gm - 高级灵魂出窍
!!help - 查看所有帮助
!!here - 广播自己位置
!!ib - 增量备份
!!loc - 路标管理
!!mail - 收发邮件
!!stats - 沙雕榜
!!self - 影分身
!!tasks - 任务管理
!!whereis - 广播别人位置
可用表达式有：
== <表达式> 游戏内计算器。如 ==1+2/3 返回 1.666666, ==1+2//3 返回 1 (//是整除)
=? <关键字> 在 Minecraft Wiki 上搜索关键字并返回链接
=! <关键字> 在 Minecraft Wiki 的B站镜像站上搜索关键字并返回链接
在消息中用 @ <玩家名> 可以提到某人，该玩家将会听到声音
"""

def helpPlugin(ev, server, plugin):
  if ev["content"] != "!!help": return
  for line in lines.split("\n"):
    server.tell(ev["sender"], CC(line, "e"))

listener = [
  {"type": TRIGGER.PLAYER_INFO, "func": helpPlugin}
]
name = "HelpPlugin"
