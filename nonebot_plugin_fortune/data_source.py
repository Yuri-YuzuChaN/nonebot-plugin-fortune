import json
import random
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

import aiofiles
from PIL import Image, ImageDraw, ImageFont

from .config import *


def theme_flag_check(theme: str) -> bool:
    """
    检查主题是否启用
    """
    return config.model_dump().get(theme + "_flag", False)


class FortuneManager:
    
    _user_data: Dict[str, Dict[str, Dict[str, Union[str, int, date]]]]
    _group_rules: Dict[str, str]
    _specific_rules: Dict[str, List[str]]
    _copywrting: List[CopyWrting] = []
    
    def __init__(self, group_id: int, user_id: Optional[int] = None):
        self.group_id = str(group_id)

        if self.group_id not in self._group_rules:
            self._group_rules.update(
                {
                    self.group_id: "random"
                }
            )
        self.group_rule = self.group_rule[self.group_id]
        
        if self.group_id not in self._user_data:
            self._user_data[self.group_id] = {}
        self.group_config = self._user_data[self.group_id]
        
        if user_id is not None:
            self.user_id = str(user_id)
            if user_id not in self.group_config:
                self.group_config[self.user_id] = {
                    "last_sign_date": 0
                }
            self.user_config = self.group_config[self.user_id]
    
    @classmethod
    async def load(cls):
        cls._user_data = await cls.open(user_data_file)
        cls._group_rules = await cls.open(group_rules_file)
        cls._specific_rules = await cls.open(specific_rules_file)
        copywrting = await cls.open(copywriting_file)
        cls._copywrting = [CopyWrting.model_validate(_) for _ in copywrting["copywriting"]]
    
    @staticmethod
    def autosave(file: Iterator[Path]):
        """
        自动保存装饰器
        
        Params:
            `file`: `Path` 迭代器
        """
        def decorator(func: Callable):
            async def wrapper(self: "FortuneManager", *args, **kwargs) -> Optional[bool]:
                try:
                    return await func(*args, **kwargs)
                finally:
                    _file = {
                        user_data_file: self._user_data,
                        group_rules_file: self._group_rules,
                        specific_rules_file: self._specific_rules,
                    }
                    for _f, _d in zip(file, _file[file]):
                        await self.save(_f, _d)
            return wrapper
        return decorator
    
    async def open(self, file: Path) -> Dict:
        """
        打开文件并序列化
        """
        async with aiofiles.open(file, "r", encoding="utf-8") as f:
            return json.loads(await f.read())
    
    async def save(self, file: Path, data: Any):
        """
        保存文件
        """
        async with aiofiles.open(file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=4))
            
    def get_group_theme(self) -> str:
        """
        获取群主题
        """
        return self.group_rule

    def _multi_divine_check(self, nowtime: date) -> bool:
        """
        检测是否重复抽签：判断此时与上次签到时间是否为同一天（年、月、日均相同）
        """
        if isinstance(self.user_config["last_sign_date"], int):
            return False

        last_sign_date = datetime.strptime(self.user_config["last_sign_date"], "%Y-%m-%d")
        return last_sign_date.date() == nowtime

    def specific_check(self, charac: str) -> Optional[str]:
        """
        检测是否有该签底规则
        检查指定规则的签底所对应主题是否开启或路径是否存在
        """
        if not self._specific_rules.get(charac, False):
            return None

        spec_path: str = random.choice(self._specific_rules[charac])
        for theme in FortuneThemesDict:
            if theme in spec_path:
                return spec_path if theme_flag_check(theme) else None

        return None
    
    def drawing(self, theme: str, spec_path: Optional[str] = None) -> Path:
        """
        绘制运势
        
        Params:
            `theme`: 主题
            `spec_path`: 角色
        Returns:
            `Path`
        """
        luck = random.choice(self._copywrting)
        title = luck.good_luck
        text = random.choice(luck.content)
        
        imgPath = random_basemap(theme, spec_path)
        img = Image.open(imgPath).convert("RGB")
        draw = ImageDraw.Draw(img)
        
        mamelon = ImageFont.truetype(MAMELON, 45)
        font_size = 25
        sakura = ImageFont.truetype(SAKURA, font_size)
        
        font_length = mamelon.getbbox(title)
        draw.text(
            (
                140 - font_length[2] / 2,
                99 - font_length[3] / 2,
            ),
            title,
            fill="#F5F5F5",
            font=mamelon,
        )
        slices, result = decrement(text)
        for i in range(slices):
            font_height: int = len(result[i]) * (font_size + 4)
            textVertical: str = "\n".join(result[i])
            x: int = int(
                140
                + (slices - 2) * font_size / 2
                + (slices - 1) * 4
                - i * (font_size + 4)
            )
            y: int = int(297 - font_height / 2)
            draw.text((x, y), textVertical, fill="#323232", font=sakura)

        if not out_dir.exists():
            out_dir.mkdir(exist_ok=True, parents=True)

        outPath = out_dir / f"{self.group_id}_{self.user_id}.png"

        img.save(outPath)
        return outPath
    

    async def divine(
        self,
        theme: Optional[str] = None,
        spec_path: Optional[str] = None
    ) -> Tuple[bool, Optional[bytes]]:
        """
        今日运势抽签，主题已确认合法
        """
        now_time = date.today()

        if not isinstance(theme, str):
            _theme = self.group_rule
        else:
            _theme = theme

        if not self._multi_divine_check(now_time):
            try:
                img_path = self.drawing(_theme, spec_path)
            except Exception:
                return True, None

            await self._end_data_handle(now_time)
            return True, img_path.read_bytes()
        else:
            img_path = out_dir / f"{self.group_id}_{self.user_id}.png"
            return False, img_path.read_bytes()
    
    def theme_enable_check(self, theme: str) -> bool:
        """
        检查是否开启主题
        
        Params:
            `theme`: 主题
        Returns:
            `bool`
        """
        return theme == "random" or theme_flag_check(theme)

    @autosave([user_data_file, group_rules_file])
    async def _end_data_handle(self, nowtime: date) -> None:
        """
        占卜结束数据保存
        """
        self.user_config["last_sign_date"] = nowtime


    @autosave([group_rules_file])
    async def divination_setting(self, theme: str) -> bool:
        """
        分群管理抽签设置
        """
        if self.theme_enable_check(theme):
            self.group_rule = theme
            return True

        return False


def get_available_themes() -> str:
    """
    获取可设置的抽签主题
    """
    msg = "可选抽签主题"
    for theme in FortuneThemesDict:
        if theme != "random" and theme_flag_check(theme):
            msg += f"\n{FortuneThemesDict[theme][0]}"

    return msg


def random_basemap(theme: str, spec_path: Optional[str] = None) -> Path:
    """
    选择主题和角色
    
    Params:
        `theme`: 主题
        `spec_path`: 角色
    Returns:
        `Path`: 路径
    """
    if isinstance(spec_path, str):
        p = theme_dir / spec_path
        return p

    if theme == "random":
        themes = [
            f.name for f in theme_dir.iterdir() if theme_flag_check(f.name)
        ]
        picked = random.choice(themes)

        _p = theme_dir / picked
    else:
        _p = theme_dir / theme
    return random.choice(list(_p.iterdir()))


def decrement(text: str) -> Tuple[int, List[str]]:
    """
    Split the text, return the number of columns and text list
    TODO: Now, it ONLY fit with 2 columns of text
    """
    length = len(text)
    result: List[str] = []
    cardinality = 9
    if length > 4 * cardinality:
        raise Exception

    col_num = 1
    while length > cardinality:
        col_num += 1
        length -= cardinality

    space = " "
    length = len(text)

    if col_num == 2:
        if length % 2 == 0:
            fillIn = space * int(9 - length / 2)
            return col_num, [
                text[: int(length / 2)] + fillIn,
                fillIn + text[int(length / 2) :],
            ]
        else:
            fillIn = space * int(9 - (length + 1) / 2)
            return col_num, [
                text[: int((length + 1) / 2)] + fillIn,
                fillIn + space + text[int((length + 1) / 2) :],
            ]

    for i in range(col_num):
        if i == col_num - 1 or col_num == 1:
            result.append(text[i * cardinality :])
        else:
            result.append(text[i * cardinality : (i + 1) * cardinality])

    return col_num, result


def clean_out_pics() -> None:
    """
    清楚昨日所有运势图片
    """
    for pic in out_dir.iterdir():
        pic.unlink()