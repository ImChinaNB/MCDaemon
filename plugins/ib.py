"""
MCDaemonReloaded 服务器 增量备份插件 (Increasing Backup)
提供多个槽位的增量备份与回档功能。
"""
import config
import uuid, json
from event import TRIGGER

listener = [
]
name = "BackupPlugin"
