"""
路径管理与输出目录处理工具

提供输出路径计算、目录创建、zip 打包等功能。
"""

import zipfile
from pathlib import Path
from datetime import datetime


def get_output_dir(
    input_path: Path | str,
    mode: str = "subdir",
    custom_dir: Path | str = None,
) -> Path:
    """
    根据模式计算输出目录

    Args:
        input_path: 输入字体文件路径
        mode: 输出模式
            - "subdir": 在源文件同目录下创建子目录
            - "custom": 使用自定义目录
        custom_dir: 自定义输出目录（mode="custom" 时使用）

    Returns:
        输出目录路径
    """
    input_path = Path(input_path)

    if mode == "custom" and custom_dir:
        output_dir = Path(custom_dir)
    else:
        # 默认：源文件同目录下的 "subset_output" 子目录
        output_dir = input_path.parent / "subset_output"

    return output_dir


def ensure_output_dir(output_dir: Path | str) -> Path:
    """
    确保输出目录存在，不存在则创建

    Args:
        output_dir: 输出目录路径

    Returns:
        创建后的目录路径

    Raises:
        PermissionError: 目录不可写
    """
    output_dir = Path(output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise PermissionError(f"无法创建输出目录（权限不足）: {output_dir}")
    return output_dir


def get_output_basename(input_path: Path | str, suffix: str = ".subset") -> str:
    """
    生成输出文件基础名

    Args:
        input_path: 输入文件路径
        suffix: 附加后缀标识

    Returns:
        基础文件名（不含扩展名）
    """
    input_path = Path(input_path)
    stem = input_path.stem
    return f"{stem}{suffix}"


def zip_results(files: list[Path], output_zip: Path | str) -> Path:
    """
    将多个文件打包为 zip

    Args:
        files: 要打包的文件路径列表
        output_zip: 输出 zip 文件路径

    Returns:
        zip 文件路径
    """
    output_zip = Path(output_zip)
    output_zip.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            if f.exists():
                zf.write(f, f.name)

    return output_zip


def format_file_size(size_bytes: int) -> str:
    """将字节数格式化为易读字符串"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def generate_timestamp_name() -> str:
    """生成时间戳名称，用于批量输出目录"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
