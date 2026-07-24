"""
fontTools subset 核心封装

提供字体子集化功能，将字体文件裁剪为仅包含指定字符的子集。
"""

from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options


def create_subset_options(options_dict: dict) -> Options:
    """
    根据用户选项创建 fontTools Subsetter 的 Options 对象

    Args:
        options_dict: 用户选项字典
            - keep_layout: bool, 是否保留布局特性表
            - keep_names: bool, 是否保留完整 name 表
            - notdef_glyph: bool, 是否保留 .notdef 字形
            - glyph_names: bool, 是否保留字形名称

    Returns:
        配置好的 Options 对象
    """
    options = Options()

    # 布局特性表
    if options_dict.get("keep_layout", True):
        options.layout_features = ["*"]
    else:
        options.layout_features = []

    # name 表
    if options_dict.get("keep_names", True):
        options.name_IDs = ["*"]
    else:
        options.name_IDs = [0, 1, 2, 3, 4, 5, 6]

    # .notdef 字形
    options.notdef_glyph = options_dict.get("notdef_glyph", True)
    options.notdef_outline = options_dict.get("notdef_glyph", True)

    # 字形名称
    options.glyph_names = options_dict.get("glyph_names", False)

    # 通用优化选项
    options.hinting = options_dict.get("keep_hinting", False)
    options.desubroutinize = True

    return options


def subset_font(
    input_path: Path | str,
    characters: str,
    options_dict: dict = None,
) -> TTFont:
    """
    对字体进行子集化处理

    Args:
        input_path: 输入字体文件路径
        characters: 需要保留的字符集字符串
        options_dict: 处理选项字典

    Returns:
        处理后的 TTFont 对象

    Raises:
        FileNotFoundError: 输入文件不存在
        ValueError: 字符集为空
        Exception: fontTools 处理错误
    """
    if options_dict is None:
        options_dict = {}

    input_path = Path(input_path)

    # 校验
    if not input_path.exists():
        raise FileNotFoundError(f"字体文件不存在: {input_path}")

    if not characters or not characters.strip():
        raise ValueError("字符集不能为空")

    # 去重字符
    unique_chars = "".join(set(characters))

    # 加载字体
    font = TTFont(str(input_path))

    # 创建子集化选项
    options = create_subset_options(options_dict)

    # 执行子集化
    subsetter = Subsetter(options=options)
    subsetter.populate(text=unique_chars)
    subsetter.subset(font)

    return font


def get_font_info(font_path: Path | str) -> dict:
    """
    获取字体基本信息

    Args:
        font_path: 字体文件路径

    Returns:
        包含字体信息的字典
    """
    font_path = Path(font_path)
    font = TTFont(str(font_path))

    info = {
        "file_name": font_path.name,
        "file_size": font_path.stat().st_size,
        "glyph_count": len(font.getGlyphOrder()),
        "tables": list(font.keys()),
    }

    # 尝试获取字体名称
    if "name" in font:
        name_table = font["name"]
        for record in name_table.names:
            if record.nameID == 4:  # Full Name
                try:
                    info["full_name"] = record.toUnicode()
                    break
                except Exception:
                    pass

    font.close()
    return info
