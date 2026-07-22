"""
GlassPanel v3 - Apple 风格单级玻璃卡片

设计来源：
  - high-end-visual-design 的 Double-Bezel 嵌套硬件感
  - design-taste-frontend 的 Liquid Glass 诚实近似（标注非官方材质）

实现要点：
  - 单层容器（不再 light/mid/deep 三级）—— Bento 布局下所有卡片同级
  - 提供 elevated 档用于需突出的卡片（主按钮容器 / 进度卡）
  - 模式感知：浅色近白通透，深色近黑通透
  - 边框 1px hairline（Apple 标准分隔）
  - 阴影 tinted 到背景色、漫射；无外发光
  - 顶部 inset 高光近似 Liquid Glass 上边缘反光（诚实标注为近似，非官方）
"""

import flet as ft
from ui.theme import tokens, RADIUS_CARD, PADDING_LG


class GlassPanel(ft.Container):
    """
    Apple 风格玻璃卡片组件

    用法:
        GlassPanel(page=page, content=...)
        GlassPanel(page=page, content=..., elevated=True)   # 突出档
    """

    def __init__(
        self,
        page: ft.Page,
        content: ft.Control = None,
        elevated: bool = False,
        width: int = None,
        height: int = None,
        padding: int = PADDING_LG,
        border_radius: int = RADIUS_CARD,
        expand: bool = False,
        **kwargs,
    ):
        super().__init__()
        self._page = page
        self._elevated = elevated
        self._content = content
        self._width = width
        self._height = height
        self._padding = padding
        self._border_radius = border_radius
        self._expand = expand
        self._extra_kwargs = kwargs
        self.apply_theme()

    def apply_theme(self):
        """按当前模式重算样式（系统外观切换时由外部调用）。"""
        t = tokens(self._page)
        bg = t["glass_bg_elevated"] if self._elevated else t["glass_bg"]
        sh = t["shadow_card_elevated"] if self._elevated else t["shadow_card"]

        shadows = [
            ft.BoxShadow(
                offset=ft.Offset(0, sh["offset_y"]),
                blur_radius=sh["blur"],
                color=sh["color"],
            ),
        ]

        self.width = self._width
        self.height = self._height
        self.padding = self._padding
        self.expand = self._expand
        self.border_radius = self._border_radius
        self.bgcolor = bg
        self.border = ft.border.all(1, t["border"])
        self.shadow = shadows
        # 不设 alignment —— 让内容（Column）填满容器宽高，而非缩成自然尺寸居中
        self.alignment = None
        self.content = self._content
        # 透传其余参数
        for k, v in self._extra_kwargs.items():
            setattr(self, k, v)
