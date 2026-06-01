"""
高级处理选项组件 v2 - 深色毛玻璃风格
"""

import flet as ft
from ui.theme import (
    TEXT_LABEL, TEXT_DESC, PRIMARY,
    FONT_SECTION, FONT_LABEL,
    SPACING_SM, SPACING_MD,
)


class AdvancedOptions(ft.Column):
    """高级处理选项组件（可折叠）"""

    def __init__(self, page: ft.Page):
        super().__init__(spacing=SPACING_SM)
        self._page = page
        self._expanded = False

        self._sw_keep_layout = ft.Switch(
            label="保留布局特性表（GPOS/GSUB）", value=True, active_color=PRIMARY,
            label_text_style=ft.TextStyle(size=FONT_LABEL, color=TEXT_LABEL),
        )
        self._sw_keep_names = ft.Switch(
            label="保留完整 name 表", value=True, active_color=PRIMARY,
            label_text_style=ft.TextStyle(size=FONT_LABEL, color=TEXT_LABEL),
        )
        self._sw_notdef = ft.Switch(
            label="保留 .notdef 字形", value=True, active_color=PRIMARY,
            label_text_style=ft.TextStyle(size=FONT_LABEL, color=TEXT_LABEL),
        )
        self._sw_glyph_names = ft.Switch(
            label="保留字形名称（glyph names）", value=False, active_color=PRIMARY,
            label_text_style=ft.TextStyle(size=FONT_LABEL, color=TEXT_LABEL),
        )
        self._sw_hinting = ft.Switch(
            label="保留 hinting 信息", value=False, active_color=PRIMARY,
            label_text_style=ft.TextStyle(size=FONT_LABEL, color=TEXT_LABEL),
        )

        self._options_panel = ft.Column(
            [self._sw_keep_layout, self._sw_keep_names, self._sw_notdef,
             self._sw_glyph_names, self._sw_hinting],
            spacing=SPACING_SM, visible=False,
        )

        self._toggle_btn = ft.TextButton(
            "高级选项 ▶", icon=ft.Icons.TUNE, on_click=self._toggle,
            style=ft.ButtonStyle(color=TEXT_DESC),
        )

        self.controls = [self._toggle_btn, self._options_panel]

    @property
    def options_dict(self) -> dict:
        return {
            "keep_layout": self._sw_keep_layout.value,
            "keep_names": self._sw_keep_names.value,
            "notdef_glyph": self._sw_notdef.value,
            "glyph_names": self._sw_glyph_names.value,
            "keep_hinting": self._sw_hinting.value,
        }

    def _toggle(self, e):
        self._expanded = not self._expanded
        self._options_panel.visible = self._expanded
        self._toggle_btn.text = "高级选项 ▼" if self._expanded else "高级选项 ▶"
        self._page.update()
