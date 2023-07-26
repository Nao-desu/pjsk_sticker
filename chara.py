import os,json
from os.path import join
from hoshino import logger

CONFIG_PATH = os.path.dirname(__file__)

with open(join(CONFIG_PATH,'characters.json'), 'r', encoding='UTF-8') as f:
        characters = json.load(f)
with open(join(CONFIG_PATH,'charaname.json'), 'r', encoding='UTF-8') as f:
        charaname = json.load(f)

async def check_chara(name:str):
    try:
        for i in charaname:
            if name in i:
                return i[0]
        return None
    except Exception as e:
        logger.error(e)
        return None


async def check_name(name:str):
    try:
        for i in characters:
            if i["name"] == name:
                return i
        return None
    except Exception as e:
        logger.error(e)
        return None

async def all_chara(name:str):
    try:
        for i in charaname:
            if name in i:
                return [i[0],",".join(i)]
        return None
    except Exception as e:
        logger.error(e)
        return None