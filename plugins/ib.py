"""
MCDaemonReloaded 服务器 增量备份插件 (Increasing Backup)
提供多个槽位的增量备份与回档功能。
"""

listener = [
  {"type": TRIGGER.PLUGIN_LOADED, "func": loaded},
  {"type": TRIGGER.PLUGIN_UNLOADING, "func": unloading}
]
name = "UUIDPlugin"
