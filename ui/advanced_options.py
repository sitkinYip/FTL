"""
高级处理选项组件 v5 - 弹窗承载

变化（v5）：从可折叠面板改为弹窗内容。本组件只渲染开关组，
打开/关闭由 AdvancedDialog（main_view 持有）控制。
options_dict 公共属性不变。
"""

import flet as ft
from ui.theme import (
    tokens,
    FONT_LABEL,
    SPACING_SM, SPACING_MD,
)


class AdvancedOptions(ft.Column):
    """高级处理选项（开关组，作为弹窗内容）"""

    def __init__(self, page: ft.Page):
        super().__init__(spacing=SPACING_MD)
        self._page = page
        t = tokens(page)

        self._sw_keep_layout = ft.Switch(
            label="保留布局特性表（GPOS/GSUB）", value=True, active_color=t["accent"],
            label_text_style=ft.TextStyle(size=FONT_LABEL, color=t["text_primary"]),
        )
        self._sw_keep_names = ft.Switch(
            label="保留完整 name 表", value=True, active_color=t["accent"],
            label_text_style=ft.TextStyle(size=FONT_LABEL, color=t["text_primary"]),
        )
        self._sw_notdef = ft.Switch(
            label="保留 .notdef 字形", value=True, active_color=t["accent"],
            label_text_style=ft.TextStyle(size=FONT_LABEL, color=t["text_primary"]),
        )
        self._sw_glyph_names = ft.Switch(
            label="保留字形名称（glyph names）", value=False, active_color=t["accent"],
            label_text_style=ft.TextStyle(size=FONT_LABEL, color=t["text_primary"]),
        )
        self._sw_hinting = ft.Switch(
            label="保留 hinting 信息", value=False, active_color=t["accent"],
            label_text_style=ft.TextStyle(size=FONT_LABEL, color=t["text_primary"]),
        )

        self._switches = [self._sw_keep_layout, self._sw_keep_names, self._sw_notdef,
                          self._sw_glyph_names, self._sw_hinting]

        self.controls = self._switches

    def apply_theme(self):
        t = tokens(self._page)
        for sw in self._switches:
            sw.active_color = t["accent"]
            sw.label_text_style = ft.TextStyle(size=FONT_LABEL, color=t["text_primary"])

    @property
    def options_dict(self) -> dict:
        return {
            "keep_layout": self._sw_keep_layout.value,
            "keep_names": self._sw_keep_names.value,
            "notdef_glyph": self._sw_notdef.value,
            "glyph_names": self._sw_glyph_names.value,
            "keep_hinting": self._sw_hinting.value,
        }
