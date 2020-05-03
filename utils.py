#!/usr/bin/env python3
"""
MCDaemonReloaded Utils。
1) 提供可格式化的 /tellraw 接口。
2) provide some utils to deal with utils files.
3) simple permission system
"""
import json
colorCodes = {
  '4': 'dark_red',
  'c': 'red',
  '6': 'gold',
  'e': 'yellow',
  '2': 'dark_green',
  'a': 'green',
  'b': 'aqua',
  '3': 'dark_aqua',
  '1': 'dark_blue',
  '9': 'blue',
  'd': 'light_purple',
  '5': 'dark_purple',
  'f': 'white',
  '7': 'gray',
  '8': 'dark_gray',
  '0': 'black'
}
formatCodes = {
  'k': 'obfuscated',
  'l': 'bold',
  'm': 'strikethrough',
  'n': 'underline',
  'o': 'italic'
}
# fromColorCode and FormatCode
def CC(text, codes="f"):
  r = {"text": text, "color": "white"}
  for f in ['obfuscated','bold','strikethrough','underline','italic']: r[f]=False
  for c in codes:
    if c in colorCodes:
      r["color"] = colorCodes[c]
    elif c in formatCodes:
      r[formatCodes[c]] = True
  return r
def NC(*texts):
  f = ""
  for text in texts:
    if isinstance(text, dict):
      f += text["text"]
    else:
      f += str(text)
  return f

## utils.py
import json, os, os.path, re, logging, builtins
import logging
l = logging.getLogger(__name__)

def vaildname(filename, prefix='config'):
  if not os.path.normpath(prefix+'/' + filename).startswith(prefix) or re.search(r'[^A-Za-z0-9_\-]', filename):
    return False
  return True
def loadConfig(filename, default = {}):
  if not vaildname(filename): return False
  l.debug("读取配置文件 %s", filename)
  try:
    with open("config/" + filename + ".json", "r", encoding='utf-8') as f:
      return json.load(f)
  except:
    return default
def loadData(filename, default = {}):
  if not vaildname(filename, 'data'): return False
  l.debug("读取数据文件 %s", filename)
  try:
    with open("data/" + filename + ".json", "r", encoding='utf-8') as f:
      return json.load(f)
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
def saveData(filename, content):
  if not vaildname(filename, 'data'): return False
  try:
    with open("data/" + filename + ".json", "w", encoding='utf-8') as f:
      json.dump(content, f, ensure_ascii=False, indent=4, sort_keys=False)
    return True
  except:
    return False

## perm system
