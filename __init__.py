from hoshino import Service,logger
from hoshino.typing import CQEvent
from hoshino.util import filt_message
from .chara import check_chara,all_chara
from .pic import stick_maker
import os

PLUGIN_PATH = os.path.dirname(__file__)
sv_help = '''
pisk贴纸：pjsk角色贴纸生成器
指令：
[pss 角色名 贴纸编号 任意文本]生成贴纸,角色名支持昵称
[pss角色 角色名]查看角色贴纸预览
[pss别名 角色编号]查看角色别名
[pss列表]查看所有角色
'''
sv=Service('pjsk贴纸',enable_on_default=True, help_=sv_help)

@sv.on_prefix('pss角色')
async def sitcker_preview(bot, ev: CQEvent):
    try:
        chara = ev.message.extract_plain_text().strip()
        if name := await check_chara(chara):
            filepath = os.path.join(PLUGIN_PATH,f'img\\info\\{name}.png')
            msg = f'[CQ:image,file=file:///{os.path.abspath(filepath)}]'
            await bot.send(ev,msg)
        else:
            await bot.send(ev,f'角色{chara}不存在!')
            return
    except Exception as e:
        logger.error(e)
        await bot.send(ev, "角色预览生成失败", at_sender=True)

@sv.on_fullmatch('pss列表')
async def characters_preview(bot, ev: CQEvent):
    try:
        filepath = os.path.join(PLUGIN_PATH,f'img\\allchara.png')
        msg = f'[CQ:image,file=file:///{os.path.abspath(filepath)}]'
        await bot.send(ev,msg)
    except Exception as e:
        logger.error(e)
        await bot.send(ev, "角色列表生成失败", at_sender=True)

@sv.on_prefix('pss别名')
async def characters_name(bot, ev: CQEvent):
    try:
        chara_id = ev.message.extract_plain_text().strip()
        if chara_name := await all_chara(chara_id):
            await bot.send(ev,f"角色:{chara_name[0]}\n{chara_name[1]}")
        else:
            await bot.send(ev,f"角色{chara_id}不存在")
    except Exception as e:
        logger.error(e)
        await bot.send(ev, "角色别名生成失败", at_sender=True)

@sv.on_prefix('pss')
async def make_stick(bot, ev: CQEvent):
    try:
        info = ev.message.extract_plain_text().strip().split()
        #info0 = [x for x in info if x]
        try:
            chara=str(info[0])
            chara_id=str(info[1])
            try:
                if 0<int(chara_id)<=9:
                    chara_id = f"0{chara_id.lstrip('0')}"
                elif int(chara_id)==10:
                    await bot.send(ev,"贴纸序号10不存在")
                    return
            except ValueError:
                await bot.send(ev,"贴纸序号错误,应为正整数")
                return
            try:
                text = filt_message("".join(info[2:]))
            except TypeError:
                await bot.send(ev,"传入文本错误")
                return
        except Exception as e:
            logger.error(e)
            await bot.send(ev,"参数错误，应为[pss 角色名 贴纸序号 任意文本]")
            return
        img = await stick_maker(chara,chara_id,text)
        await bot.send(ev,img)
    except Exception as e:
        logger.error(e)
        await bot.send(ev, "图片生成失败", at_sender=True)
