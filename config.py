#!/usr/bin/env python3
"""
This is the config class file of MCDaemonReloaded.
Written by ChinaNB, GPL 3.0 License.

config: provide some utils to deal with config files.
"""
import json, os, os.path, re

def vaildname(filename):
  if not os.path.normpath('config/' + filename).startswith('config/') or re.search(r'[^A-Za-z0-9_\-]', filename):
    return False
  return True
def loadConfig(filename, default = {}):
  if not vaildname(filename): return False
  try:
    with open("config/" + filename + ".json", "r", encoding='utf-8') as f:
      return json.load(f)
  except:
    return default
def loadText(filename, default = ""):
  if not vaildname(filename): return False
  try:
    with open("config/" + filename + ".txt", "r", encoding='utf-8') as f:
      return f.read()
  except:
    return default
def saveConfig(filename, content):
  if not vaildname(filename): return False
  try:
    with open("config/" + filename + ".json", "w", encoding='utf-8') as f:
      json.dump(content, f, ensure_ascii=False, indent=4, sort_keys=False)
    return True
  except:
    return False
