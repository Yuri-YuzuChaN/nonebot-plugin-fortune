import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Union

from nonebot import get_driver, get_plugin_config
from nonebot.log import logger
from pydantic import BaseModel, Field, model_validator

FortuneThemesDict: Dict[str, List[str]] = {
    "random":           ["随机"],
    "amazing_grace":    ["奇异恩典"],
    "arknights":        ["明日方舟", "方舟", "arknights", "鹰角", "Arknights", "舟游"],
    "asoul":            ["Asoul", "asoul", "a手", "A手", "as", "As"],
    "azure":            ["碧蓝航线", "碧蓝", "azure", "Azure"],
    "dc4":              ["dc4", "DC4", "Dc4"],
    "einstein":         ["爱因斯坦携爱敬上", "爱因斯坦", "einstein", "Einstein"],
    "genshin":          ["原神", "Genshin Impact", "genshin", "Genshin", "op", "原批"],
    "granblue_fantasy": ["碧蓝幻想", "Granblue Fantasy", "granblue fantasy", "幻想"],
    "hololive":         ["Hololive", "hololive", "Vtb", "vtb", "管人", "Holo", "holo", "管人痴"],
    "hoshizora":        ["星空列车与白的旅行", "星空列车"],
    "liqingge":         ["李清歌", "清歌"],
    "onmyoji":          ["阴阳师", "yys", "Yys", "痒痒鼠"],
    "pcr":              ["PCR", "公主链接", "公主连结", "Pcr", "pcr"],
    "pretty_derby":     ["赛马娘", "马", "马娘", "赛马"],
    "punishing":        ["战双", "战双帕弥什"],
    "sakura":           ["樱色之云绯色之恋", "樱云之恋", "樱云绯恋", "樱云"],
    "summer_pockets":   ["夏日口袋", "夏兜", "sp", "SP"],
    "sweet_illusion":   ["灵感满溢的甜蜜创想", "甜蜜一家人", "富婆妹"],
    "touhou":           ["东方", "touhou", "Touhou", "车万"],
    "touhou_lostword":  ["东方归言录", "东方lostword", "touhou lostword"],
    "touhou_old":       ["旧东方", "旧版东方", "老东方", "老版东方", "经典东方"],
    "warship_girls_r":  ["战舰少女R", "舰r", "舰R", "wsgr", "WSGR", "战舰少女r"],
}
"""
抽签主题对应表，第一键值为 `抽签设置` 或 `主题列表` 展示的主题名称
Key-Value: 主题资源文件夹名-主题别名
"""

class PluginConfig(BaseModel, extra='ignore'):
    
    fortune_path: Path


class ThemesFlagConfig(BaseModel, extra='ignore'):
    """
    Switches of themes only valid in random divination.
    Make sure NOT ALL FALSE!
    """

    amazing_grace_flag: bool    = True
    arknights_flag: bool        = True
    asoul_flag: bool            = True
    azure_flag: bool            = True
    dc4_flag: bool              = True
    einstein_flag: bool         = True
    genshin_flag: bool          = True
    granblue_fantasy_flag: bool = True
    hololive_flag: bool         = True
    hoshizora_flag: bool        = True
    liqingge_flag: bool         = True
    onmyoji_flag: bool          = True
    pcr_flag: bool              = True
    pretty_derby_flag: bool     = True
    punishing_flag: bool        = True
    sakura_flag: bool           = True
    summer_pockets_flag: bool   = True
    sweet_illusion_flag: bool   = True
    touhou_flag: bool           = True
    touhou_lostword_flag: bool  = True
    touhou_old_flag: bool       = True
    warship_girls_r_flag: bool  = True

    @model_validator(mode='before')
    def check_all_disabled(cls, values: dict) -> None:
        """检查是否所有主题都为关闭"""
        flag: bool = False
        for theme in values:
            if values.get(theme, False):
                flag = True
                break

        if not flag:
            raise ValueError("Fortune themes ALL disabled! Please check!")

        return values


class FortuneConfig(PluginConfig, ThemesFlagConfig):
    pass


class DateTimeEncoder(json.JSONEncoder):
    
    def default(self, obj) -> Union[str, Any]:
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")

        return json.JSONEncoder.default(self, obj)


class CopyWrting(BaseModel):
    
    good_luck: str = Field(alias='good-luck')
    rank: int
    content: List[str]


driver = get_driver()
config = get_plugin_config(FortuneConfig)

# path
theme_dir   = config.fortune_path / "img"
out_dir     = config.fortune_path / "out"

# json
user_data_file: Path        = config.fortune_path / "fortune_data.json"
group_rules_file: Path      = config.fortune_path / "group_rules.json"
specific_rules_file: Path   = config.fortune_path / "specific_rules.json"
copywriting_file: Path      = config.fortune_path / "fortune" / "copywriting.json"

# font
MAMELON = config.fortune_path / "font" / "Mamelon.otf"
SAKURA  = config.fortune_path / "font" / "sakura.ttf"