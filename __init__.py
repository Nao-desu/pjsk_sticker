from hoshino import Service
from hoshino.typing import CQEvent
from .chara import check_chara
from .pic import stick_maker
import os

PLUGIN_PATH = os.path.dirname(__file__)
sv_help = '''
pisk贴纸：pjsk角色贴纸生成器
指令：
[pss 角色名 贴纸编号 任意文本]生成贴纸,角色名支持昵称
[贴纸预览 角色名]查看角色贴纸预览
[角色列表]查看所有角色
'''
sv=Service('pjsk贴纸',enable_on_default=True, help_=sv_help)

@sv.on_prefix('贴纸预览')
async def sitcker_preview(bot, ev: CQEvent):
    chara = ev.message.extract_plain_text().strip()
    name = check_chara(chara)
    if not name:
        await bot.send(ev,f'角色{chara}不存在!')
        return
    filepath = os.path.join(PLUGIN_PATH,f'img\info\\{chara}.png')
    msg = f'[CQ:image,file=file:///{os.path.abspath(filepath)}]'
    await bot.send(ev,msg)

@sv.on_fullmatch('角色预览','角色列表')
async def sitcker_preview(bot, ev: CQEvent):
    filepath = os.path.join(PLUGIN_PATH,f'img\\allchara.png')
    msg = f'[CQ:image,file=file:///{os.path.abspath(filepath)}]'
    await bot.send(ev,msg)

@sv.on_prefix('pss')
async def make_stick(bot, ev: CQEvent):
    try:
        info = ev.message.extract_plain_text().strip().split()
        info0 = [x for x in info if x]
        try:
            chara,id,text = info0
            text = "".join(info0[2:])
        except:
            await bot.send(ev,"参数错误，应为[pss 角色名 贴纸序号 任意文本]")
            return
        img = await stick_maker(chara,id,text)
        if img == -1:
            await bot.send(ev,f"角色{chara}不存在")
            return
        if img == -2:
            await bot.send(ev,f"id不存在,请用[贴纸预览 角色名]查看对应贴纸")
        await bot.send(ev,img)
    except Exception as e:
        await bot.send(ev,f"生成失败：{e}")
