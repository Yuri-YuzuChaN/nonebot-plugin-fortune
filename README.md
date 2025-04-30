<div align="center">

# Fortune

🙏 今日运势 🙏

</div>
<div align="center">

  [![python3](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

</div>

## 版本

> [!WARNING]
> 暂不可用

修改自 [nonebot_plugin_fortune](https://github.com/MinatoAquaCrews/nonebot_plugin_fortune)，适配 `nonebot > 2.0.0`

[如何添加更多的抽签主题资源？欢迎贡献！🙏](https://github.com/Yuri-YuzuChaN/nonebot-plugin-fortune/blob/master/How-to-add-new-theme.md)

## 安装
    
   - 使用 `nb-cli` 安装
      ``` python
      nb plugin install nonebot-plugin-fortune
      ```
   - 使用 `pip` 安装
      ``` python
      pip install nonebot-plugin-fortune
      ```
   - 使用源代码（不推荐） **需自行安装额外依赖**
      ``` git
      git clone https://github.com/Yuri-YuzuChaN/nonebot-plugin-fortune
      ```

## 配置

1. 下载静态资源文件，将该压缩文件解压，且解压完为文件夹 `resource`

   - [私人云盘](#)
   - [AList网盘](#)
   - [onedrive](#)

2. 在 `.env` 文件中配置静态文件绝对路径 `FORTUNE_PATH`

   ``` dotenv
   FORTUNE_PATH=path.to.resource

   # 例如 windows 平台，非 "管理员模式" 运行Bot尽量避免存放在C盘
   FORTUNE_PATH=D:\bot\resource
   # 例如 linux 平台
   FORTUNE_PATH=/root/resource
   ```

3. 可选，在 `env` 下设置 `xxx_FLAG` 以启用或关闭抽签随机主题（默认全部开启），**请确保不全为 `false`，否则会抛出错误**，例如：

   ``` dotenv
   AMAZING_GRACE_FLAG=false    # 奇异恩典·圣夜的小镇
   ARKNIGHTS_FLAG=true         # 明日方舟
   ASOUL_FLAG=true             # A-SOUL
   AZURE_FLAG=true             # 碧蓝航线
   DC4_FLAG=false              # dc4
   EINSTEIN_FLAG=true          # 爱因斯坦携爱敬上
   GENSHIN_FLAG=true           # 原神
   GRANBLUE_FANTASY_FLAG=true  # 碧蓝幻想
   HOLOLIVE_FLAG=true          # Hololive
   HOSHIZORA_FLAG=true         # 星空列车与白的旅行
   LIQINGGE_FLAG=true          # 李清歌
   ONMYOJI_FLAG=false          # 阴阳师
   PCR_FLAG=true               # 公主连结
   PRETTY_DERBY_FLAG=true      # 赛马娘
   PUNISHING_FLAG=true         # 战双帕弥什
   SAKURA_FLAG=true            # 樱色之云绯色之恋
   SUMMER_POCKETS_FLAG=false   # 夏日口袋
   SWEET_ILLUSION_FLAG=true    # 灵感满溢的甜蜜创想
   TOUHOU_FLAG=true            # 东方
   TOUHOU_LOSTWORD_FLAG=true   # 东方归言录
   TOUHOU_OLD_FLAG=false       # 东方旧版
   WARSHIP_GIRLS_R_FLAG=true   # 战舰少女R
   ```

4. 可选，在 `resource/fortune_setting.json` 内配置**指定抽签**规则，例如：

   ```json
   {
     "group_rule": {
       "123456789": "random",
       "987654321": "azure",
       "123454321": "granblue_fantasy"
     },
     "specific_rule": {
       "凯露": ["pcr/frame_1.jpg", "pcr/frame_2.jpg"],
       "可可萝": ["pcr/frame_41.jpg"]
     }
   }
   ```

   `group_rule` 会自动生成，`specific_rule` 可手动配置

   指定凯露签，由于存在两张凯露的签底，配置凯露签的**路径列表**即可；其余类似，**请确保图片路径、格式输入正确**！

5. 占卜一下你的今日运势！🎉

## 功能

1. 随机抽取今日运势，配置多种抽签主题：原神、PCR、Hololive、东方、东方归言录、明日方舟、赛马娘、阴阳师、碧蓝航线、碧蓝幻想、战双帕弥什，galgame主题等……

2. 可指定主题抽签；

3. 每群每人一天限抽签1次，0点刷新（贪心的人是不会有好运的🤗）抽签信息并清除 `resource/out` 下生成的图片；

4. 抽签的信息会保存在 `resource/fortune_data.json` 内；群抽签设置及指定抽签规则保存在 `resource/fortune_setting.json` 内；抽签生成的图片当天会保存在 `resource/out` 下；

5. `fortune_setting.json` 已预置明日方舟、Asoul、原神、东方、Hololive、李清歌的指定抽签规则；

## 命令

1. 一般抽签：今日运势、抽签、运势；

2. 指定主题抽签：[xx抽签]，例如：pcr抽签、holo抽签、碧蓝抽签；

3. 指定签底并抽签：指定[xxx]签，在 `resource/fortune_setting.json` 内手动配置；

4. [群管或群主或超管] 配置抽签主题：

   - 设置[原神/pcr/东方/vtb/方舟]签：设置群抽签主题；

   - 重置（抽签）主题：设置群抽签主题为随机；

5. 抽签设置：查看当前群抽签主题的配置；

6. 今日运势帮助：显示插件帮助文案；

7. 查看（抽签）主题：显示当前已启用主题；

## 本插件改自

[nonebot_plugin_fortune](https://github.com/MinatoAquaCrews/nonebot_plugin_fortune)
[opqqq-plugin](https://github.com/opq-osc/opqqq-plugin)

## 抽签图片及文案资源

1. [opqqq-plugin](https://github.com/opq-osc/opqqq-plugin)：原神、PCR、Hololive抽签主题；

2. 感谢江樂丝提供东方签底；

3. 东方归言录(Touhou Lostword)：[KafCoppelia](https://github.com/KafCoppelia)；

4. [FloatTech-zbpdata/Fortune](https://github.com/FloatTech/zbpdata)：其余主题签；

5. 战舰少女R(Warship Girls R)：[veadex](https://github.com/veadex)、[EsfahanMakarov](https://github.com/EsfahanMakarov)；

6. 运势文案：[KafCoppelia](https://github.com/KafCoppelia)。`copywriting.json` 整合了関係運、全体運、勉強運、金運、仕事運、恋愛運、総合運、大吉、中吉、小吉、吉、半吉、末吉、末小吉、凶、小凶、半凶、末凶、大凶及700+条运势文案！来源于Hololive早安系列2019年第6.10～9.22期，有修改。
