import asyncio
import base64
import json
import random
from hoshino import Service, logger, HoshinoBot
from hoshino.typing import CQEvent, MessageSegment, Union
from hoshino.util import filt_message
from io import BytesIO
from .chara import check_chara, all_chara, check_name
from .pic import stick_maker
import os

PLUGIN_PATH = os.path.dirname(__file__)
config_path = os.path.join(PLUGIN_PATH, "config.json")

sv_help = '''
pjsk贴纸：pjsk角色贴纸生成器
指令：
1、pss [角色名] [贴纸编号] [任意文本]
示例：pss 1 1 测试文本
2、pss别名 [角色名]
示例：pss别名 1
3、pss角色 [角色名]
示例：pss角色 ena
4、pss列表
示例：pss列表
5、随机 [任意文本]
示例：随机 测试文本
'''
sv = Service(
    name='pjsk贴纸',
    enable_on_default=True,
    visible=False,
    help_=sv_help
)


def bytesio2b64(img: Union[BytesIO, bytes]) -> str:
    if isinstance(img, BytesIO):
        img = img.getvalue()
    return f"base64://{base64.b64encode(img).decode()}"


def get_configs(gid: str = False) -> Union[bool, dict]:
    if not os.path.exists(config_path):
        open(config_path, "w")
    try:
        configs: dict = json.load(open(config_path, "r", encoding='UTF-8'))
    except json.JSONDecodeError:
        configs: dict = {}
    if gid:
        if gid not in configs:
            configs[gid] = True
        return configs[gid]
    else:
        return configs


@sv.on_fullmatch('pss过滤')
async def pss_filter(bot: HoshinoBot, ev: CQEvent):
    gid = str(ev.group_id)
    configs = get_configs()
    if gid not in configs:
        configs[gid] = True
    else:
        configs[gid] = not configs[gid]
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(configs, indent=2, ensure_ascii=False))
    await bot.send(ev, f"本群过滤词已更改为{configs[gid]}")


@sv.on_prefix('pss角色')
async def sitcker_preview(bot: HoshinoBot, ev: CQEvent):
    try:
        random_chara = ev.message.extract_plain_text().strip()
        if name := await check_chara(random_chara):
            filepath = os.path.join(PLUGIN_PATH, 'img', 'info', f'{name}.png')
            chara_pic = open(filepath, "rb").read()
            msg = MessageSegment.image(bytesio2b64(chara_pic))
            # msg = f'[CQ:image,file=file:///{os.path.abspath(filepath)}]'
            await bot.send(ev, msg)
        else:
            await bot.send(ev, f'角色{random_chara}不存在!')
            return
    except Exception as e:
        logger.error(e)
        await bot.send(ev, "角色预览生成失败", at_sender=True)


@sv.on_fullmatch('pss列表')
async def characters_preview(bot: HoshinoBot, ev: CQEvent):
    try:
        filepath = os.path.join(PLUGIN_PATH, 'img', 'allchara.png')
        list_img = open(filepath, "rb").read()
        msg = MessageSegment.image(bytesio2b64(list_img))
        # msg = f'[CQ:image,file=file:///{os.path.abspath(filepath)}]'
        await bot.send(ev, msg)
    except Exception as e:
        logger.error(e)
        await bot.send(ev, "角色列表生成失败", at_sender=True)


@sv.on_prefix('pss别名')
async def characters_name(bot: HoshinoBot, ev: CQEvent):
    try:
        chara_id = ev.message.extract_plain_text().strip()
        if chara_name := await all_chara(chara_id):
            await bot.send(ev, f"角色:{chara_name[0]}\n{chara_name[1]}")
        else:
            await bot.send(ev, f"角色{chara_id}不存在")
    except Exception as e:
        logger.error(e)
        await bot.send(ev, "角色别名生成失败", at_sender=True)


@sv.on_prefix('随机')
async def random_stick(bot: HoshinoBot, ev: CQEvent):
    gid = str(ev.group_id)
    filt = get_configs(gid)
    try:
        info = ev.message.extract_plain_text().strip().split()
        text = "".join(info[:])
        # info0 = [x for x in info if x]
        random_chara = random.randint(1, 26)
        choices = [i for i in range(1, 20) if i % 5 != 0]
        while True:
            chara_id = random.choice(choices)
            chara_id = f"0{str(chara_id)}" if 0 < chara_id <= 9 else str(chara_id)
            if chara_name := await check_chara(f"{random_chara}"):
                name = f'{chara_name} {chara_id}'
                await asyncio.sleep(1)
                if await check_name(name):
                    break
            else:
                await bot.send(ev, f"角色{random_chara}不存在")
                return
        if filt:
            try:
                text = filt_message(text).replace("*", "")
            except TypeError:
                await bot.send(ev, "传入文本错误")
                return
            except Exception as e:
                sv.logger.info(e)
                await bot.send(ev, "参数错误，应为[pss 角色名 贴纸序号 任意文本]")
                return
        if img := await stick_maker(str(random_chara), chara_id, text):
            await bot.send(ev, img)
        else:
            await bot.send(ev, "贴纸生成失败", at_sender=True)
        return
    except Exception as e:
        await bot.send(ev, "贴纸生成失败", at_sender=True)
        logger.error(e)
        return


@sv.on_prefix('pss')
async def make_stick(bot: HoshinoBot, ev: CQEvent):
    gid = str(ev.group_id)
    filt = get_configs(gid)
    try:
        info = ev.message.extract_plain_text().strip().split()
        text = "".join(info[2:])
        # info0 = [x for x in info if x]
        try:
            random_chara = str(info[0])
            chara_id = str(info[1])
            try:
                if 0 < int(chara_id) <= 9:
                    chara_id = f"0{chara_id.lstrip('0')}"
                elif int(chara_id) in {5, 10, 15}:
                    await bot.send(ev, f"贴纸序号{chara_id}不存在")
                    return
            except ValueError:
                await bot.send(ev, "贴纸序号错误,应为正整数")
                return
            if filt:
                try:
                    text = filt_message(text).replace("*", "")
                except TypeError:
                    await bot.send(ev, "传入文本错误")
                    return
        except Exception as e:
            logger.error(e)
            await bot.send(ev, "参数错误，应为[pss 角色名 贴纸序号 任意文本]")
            return
        img = await stick_maker(random_chara, chara_id, text)
        await bot.send(ev, img)
    except Exception as e:
        logger.error(e)
        await bot.send(ev, "图片生成失败", at_sender=True)
