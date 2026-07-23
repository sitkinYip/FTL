"""
字体格式转换与保存逻辑

支持将 TTFont 对象保存为 woff2、woff、ttf 格式。
"""

import copy
from pathlib import Path
from fontTools.ttLib import TTFont


# 格式与对应文件扩展名
FORMAT_EXTENSIONS = {
    "woff2": ".woff2",
    "woff": ".woff",
    "ttf": ".ttf",
}

# 支持的输入格式
SUPPORTED_INPUT_EXTENSIONS = {".ttf", ".otf", ".woff", ".woff2"}


def save_font(font: TTFont, output_path: Path | str, fmt: str) -> Path:
    """
    将 TTFont 对象保存为指定格式

    Args:
        font: fontTools TTFont 对象
        output_path: 输出文件路径（不含扩展名或已含正确扩展名）
        fmt: 输出格式，支持 "woff2" / "woff" / "ttf"

    Returns:
        实际保存的文件路径

    Raises:
        ValueError: 不支持的格式
    """
    if fmt not in FORMAT_EXTENSIONS:
        raise ValueError(f"不支持的输出格式: {fmt}，支持: {list(FORMAT_EXTENSIONS.keys())}")

    output_path = Path(output_path)

    # 确保扩展名正确
    expected_ext = FORMAT_EXTENSIONS[fmt]
    if output_path.suffix != expected_ext:
        output_path = output_path.with_suffix(expected_ext)

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 设置 flavor
    if fmt == "woff2":
        font.flavor = "woff2"
    elif fmt == "woff":
        font.flavor = "woff"
    else:
        font.flavor = None

    # 保存
    font.save(str(output_path))
    return output_path


def convert_and_save(
    font: TTFont,
    output_dir: Path | str,
    base_name: str,
    formats: list[str],
) -> list[dict]:
    """
    将子集化后的字体保存为多种格式

    Args:
        font: 子集化后的 TTFont 对象
        output_dir: 输出目录
        base_name: 输出文件基础名（不含扩展名）
        formats: 输出格式列表，如 ["woff2", "woff", "ttf"]

    Returns:
        保存结果列表，每项包含 {"format", "path", "size"}
    """
    output_dir = Path(output_dir)
    results = []

    for fmt in formats:
        # 每种格式使用独立的字体副本，避免 flavor 冲突
        font_copy = copy.deepcopy(font)
        output_path = output_dir / f"{base_name}{FORMAT_EXTENSIONS[fmt]}"

        try:
            saved_path = save_font(font_copy, output_path, fmt)
            results.append({
                "format": fmt,
                "path": saved_path,
                "size": saved_path.stat().st_size,
                "success": True,
            })
        except Exception as e:
            results.append({
                "format": fmt,
                "path": output_path,
                "size": 0,
                "success": False,
                "error": str(e),
            })
        finally:
            font_copy.close()

    return results


def is_supported_font(file_path: Path | str) -> bool:
    """检查文件是否为支持的字体格式"""
    return Path(file_path).suffix.lower() in SUPPORTED_INPUT_EXTENSIONS
