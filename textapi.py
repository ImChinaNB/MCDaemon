#!/usr/bin/env python3
"""
MCDaemonReloaded Text API。
提供可格式化的 /tellraw 接口。
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