"""
预设字符集定义

提供常用字符集合，用户可直接选择快速填充。
"""

# 数字 + 小数点 + 常用符号
DIGITS = "0123456789.,-+%¥$€£"

# ASCII 可打印字符（32~126）
ASCII_PRINTABLE = "".join(chr(i) for i in range(32, 127))

# 英文字母 + 常用标点
ENGLISH_PUNCT = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
)

# 常用中文 3500 字（GB2312 一级汉字，按使用频率排列前 3500 字）
# 此处仅列出核心子集，完整 3500 字由外部文件加载或内嵌
COMMON_CJK_3500 = (
    "夸克网盘小说AI会员SVIP+Z"
    "的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出会"
    "三就学也你日对开而已些现单么过经十用发天如然但作当没成又义之至"
    "道说体于中问高被给方实机正定住此儿常西想进该它以无己面起力理间"
    "自外其事前里所合目因从都回看儿手与年将就两奶许还原记长只让相主"
    "年走几那看种代员平各种气目意第场等条世电社情市变更张设别活门政"
    "区治放海收决叫共步落男集走示由量光达品命取活数制风金革身花总组"
    "真确信指完早象报公根感世节干任件满每南至任认准联格据办示象始持"
    "空急林器节白调确克近志究观除构验传青却石细效办今集温传土许步群"
    "引听该铁纪规叶紧联呢影达格形引局建商什望满适江县市深战任反设向"
    "济路通华民且拉格望交基德老式色路音极益型米料热队准究线似型段算"
    "支流按响众转规积形千超清商极率导断火装值述完设残争附算讲类英案"
    "底夫容制运政果料科众识院际护石史局称福望城标记南夫似够难术奇"
)

# 预设列表（用于 UI 下拉/按钮展示）
PRESETS = {
    "数字+小数点": DIGITS,
    "英文+标点": ENGLISH_PUNCT,
    "ASCII 全部": ASCII_PRINTABLE,
    "常用中文": COMMON_CJK_3500,
    "数字+英文": DIGITS + ENGLISH_PUNCT,
}


def get_preset_names() -> list[str]:
    """获取所有预设名称列表"""
    return list(PRESETS.keys())


def get_preset_chars(name: str) -> str:
    """根据预设名称获取对应字符集"""
    return PRESETS.get(name, "")


def deduplicate_chars(text: str) -> str:
    """去重并保持字符原始顺序"""
    seen = set()
    result = []
    for ch in text:
        if ch not in seen:
            seen.add(ch)
            result.append(ch)
    return "".join(result)
