"""
GlassPanel v2 - 深色毛玻璃卡片组件

单层容器 + 半透明深色背景 + 单层阴影 + 统一圆角 18。
内部不再叠加额外黑底层。
"""

import flet as ft
from ui.theme import (
    GLASS_BG_LIGHT,
    GLASS_BG_MID,
    GLASS_BG_DEEP,
    GLASS_BORDER,
    RADIUS,
    PADDING_LG,
    SHADOW_CARD,
)


class GlassPanel(ft.Container):
    """
    毛玻璃卡片组件（深色系）

    三种深度预设：
        - "light": 上方参数区（最浅）
        - "mid": 中间内容区
        - "deep": 底部日志区（最深）

    用法:
        GlassPanel(content=..., depth="light")
    """

    DEPTH_MAP = {
        "light": GLASS_BG_LIGHT,
        "mid": GLASS_BG_MID,
        "deep": GLASS_BG_DEEP,
    }

    def __init__(
        self,
        content: ft.Control = None,
        depth: str = "mid",
        width: int = None,
        height: int = None,
        padding: int = PADDING_LG,
        border_radius: int = RADIUS,
        border_color: str = GLASS_BORDER,
        shadow: dict = None,
        expand: bool = False,
        **kwargs,
    ):
        if shadow is None:
            shadow = SHADOW_CARD

        bg = self.DEPTH_MAP.get(depth, GLASS_BG_MID)

        super().__init__(
            content=content,
            width=width,
            height=height,
            padding=padding,
            expand=expand,
            border_radius=border_radius,
            bgcolor=bg,
            border=ft.border.all(1, border_color),
            shadow=ft.BoxShadow(
                offset=ft.Offset(shadow["offset_x"], shadow["offset_y"]),
                blur_radius=shadow["blur_radius"],
                color=shadow["color"],
            ),
            **kwargs,
        )
