"""
MCDaemonReloaded 开服天数插件
用于统计开服天数。
"""
import datetime

startday = datetime.datetime.strptime('2020-2-25', '%Y-%m-%d')

def getday():
  now = datetime.datetime.now()
  output = now - startday
  return str(output.days)

listener = [
]
name = "DayCountAPI"
