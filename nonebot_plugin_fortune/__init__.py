from nonebot import on_command, on_fullmatch, on_regex, require
from nonebot.adapters.onebot.v11 import (
    GROUP_ADMIN,
    GROUP_OWNER,
    GroupMessageEvent,
    Message,
    MessageSegment,
)
from nonebot.log import logger
from nonebot.params import CommandArg, RegexMatched
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

from .config import FortuneConfig, FortuneThemesDict
from .data_source import *

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

__fortune_version__ = "0.0.1"
__fortune_usages__ = """
[今日运势/抽签/运势] 一般抽签
[xx抽签]     指定主题抽签
[指定xx签] 指定特殊角色签底，需要自己尝试哦~
[设置xx签] 设置群抽签主题
[重置主题] 重置群抽签主题
[主题列表] 查看可选的抽签主题
[查看主题] 查看群抽签主题""".strip()

__plugin_meta__ = PluginMetadata(
    name="今日运势",
    description="抽签！占卜你的今日运势🙏",
    usage=__fortune_usages__,
    type="application",
    homepage="https://github.com/Yuri-YuzuChaN/nonebot-plugin-fortune",
    config=FortuneConfig,
    extra={
        "author": "Yuri-YuzuChaN <806235364@qq.com>",
        "version": __fortune_version__,
    },
)

@driver.on_startup
async def _():
    await FortuneManager.load()


general_divine  = on_command("运势", aliases={"抽签"})
specific_divine = on_regex(r"^[^/]\S+抽签$")
limit_setting   = on_regex(r"^指定(.*?)签$")
themes_list     = on_fullmatch("主题列表", block=True)
show_themes     = on_regex("^查看(抽签)?主题$", block=True)
change_theme    = on_regex(
    r"^设置(.*?)签$",
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    block=True,
)
reset_themes    = on_regex(
    "^重置(抽签)?主题$",
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    block=True,
)


@general_divine.handle()
async def _(event: GroupMessageEvent, message: Message = CommandArg()):
    args = message.extract_plain_text()

    if "帮助" in args[-2:]:
        await general_divine.finish(__fortune_usages__)

    fortune = FortuneManager(event.group_id, event.user_id)

    is_first, image_file = await fortune.divine()
    if image_file is None:
        await general_divine.finish("今日运势生成出错……")

    if not is_first:
        msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(image_file)
    else:
        logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
        msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)

    await general_divine.finish(msg, at_sender=True)


@specific_divine.handle()
async def _(event: GroupMessageEvent, match = RegexMatched()):
    user_theme = match.group(1)
    if len(user_theme) < 1:
        await specific_divine.finish("输入参数错误")
    
    fortune = FortuneManager(event.group_id, event.user_id)
    for theme in FortuneThemesDict:
        if user_theme not in FortuneThemesDict[theme]:
            continue
        if fortune.theme_enable_check(theme):
            is_first, image_file = await fortune.divine(theme)
            if image_file is None:
                await specific_divine.finish("今日运势生成出错……")

            if not is_first:
                msg = MessageSegment.text(
                    "你今天抽过签了，再给你看一次哦🤗\n"
                ) + MessageSegment.image(image_file)
            else:
                logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
                msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)
        else:
            msg = "该抽签主题未启用~"

        await specific_divine.finish(msg, at_sender=True)

    await specific_divine.finish("还没有这种抽签主题哦~")


@change_theme.handle()
async def _(event: GroupMessageEvent, match = RegexMatched()):
    user_theme = match.group(1)
    fortune = FortuneManager(event.group_id)
    for theme in FortuneThemesDict:
        if user_theme in FortuneThemesDict[theme]:
            if not await fortune.divination_setting(theme):
                await change_theme.finish("该抽签主题未启用~")
            else:
                await change_theme.finish("已设置当前群抽签主题~")

    await change_theme.finish("还没有这种抽签主题哦~")


@limit_setting.handle()
async def _(event: GroupMessageEvent, match = RegexMatched()):
    theme = match.group(1)
    
    fortune = FortuneManager(event.group_id, event.user_id)

    if theme == "随机":
        spec_path = None
    else:
        spec_path = fortune.specific_check(theme)
        if spec_path is None:
            await limit_setting.finish("还不可以指定这种签哦，请确认该签底对应主题开启或图片路径存在~")
    
    is_first, image_file = await fortune.divine(spec_path=spec_path)
    if image_file is None:
        await limit_setting.finish("今日运势生成出错……")

    if not is_first:
        msg = MessageSegment.text(
            "你今天抽过签了，再给你看一次哦🤗\n"
        ) + MessageSegment.image(image_file)
    else:
        logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
        msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)

    await limit_setting.finish(msg, at_sender=True)


@reset_themes.handle()
async def _(event: GroupMessageEvent):
    fortune = FortuneManager(event.group_id)
    if not await fortune.divination_setting("random"):
        await reset_themes.finish("重置群抽签主题失败！")

    await reset_themes.finish("已重置当前群抽签主题为随机~")


@show_themes.handle()
async def _(event: GroupMessageEvent):
    fortune = FortuneManager(event.group_id)
    theme = fortune.get_group_theme()
    await show_themes.finish(f"当前群抽签主题：{FortuneThemesDict[theme][0]}")


@themes_list.handle()
async def _(event: GroupMessageEvent):
    await themes_list.finish(get_available_themes())


@scheduler.scheduled_job("cron", hour=0, minute=0, misfire_grace_time=60)
async def _():
    clean_out_pics()
    logger.info("昨日运势图片已清空！")
