import os,json
from os.path import join

CONFIG_PATH = os.path.dirname(__file__)

with open(join(CONFIG_PATH,'characters.json'), 'r', encoding='UTF-8') as f:
        characters = json.load(f)
with open(join(CONFIG_PATH,'charaname.json'), 'r', encoding='UTF-8') as f:
        charaname = json.load(f)

def check_chara(name:str) -> str:
    for i in charaname:
        if name in i:
            return i[0]
    return False

def check_name(name:str) -> dict:
    for i in characters:
        if i["name"] == name:
            return name
    return False