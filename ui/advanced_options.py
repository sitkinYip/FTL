"""
高级处理选项组件 v4 - Apple 高密度工具风格

折叠面板：chevron 图标 + 系统蓝开关。
options_dict 公共属性不变。
"""

import flet as ft
from ui.theme import (
    tokens,
    FONT_LABEL, FONT_HINT,
    SPACING_SM, SPACING_MD,
)


class AdvancedOptions(ft.Column):
    """高级处理选项组件（可折叠）"""

    def __init__(self, page: ft.Page):
        super().__init__(spacing=SPACING_SM)
        self._page = page
        self._expanded = False
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

        self._options_panel = ft.Column(
            self._switches,
            spacing=SPACING_SM, visible=False,
        )

        # 折叠切换：文字 + chevron 图标
        self._toggle_btn = ft.TextButton(
            "高级选项",
            icon=ft.Icons.TUNE_OUTLINED,
            on_click=self._toggle,
            style=ft.ButtonStyle(color=t["text_secondary"]),
        )
        self._chevron = ft.Icon(ft.Icons.EXPAND_MORE, size=18, color=t["text_secondary"])

        self.controls = [
            ft.Row([self._toggle_btn, self._chevron], spacing=2),
            self._options_panel,
        ]

    def apply_theme(self):
        t = tokens(self._page)
        for sw in self._switches:
            sw.active_color = t["accent"]
            sw.label_text_style = ft.TextStyle(size=FONT_LABEL, color=t["text_primary"])
        self._toggle_btn.style.color = t["text_secondary"]
        self._chevron.color = t["text_secondary"]

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
        self._chevron.icon = ft.Icons.EXPAND_LESS if self._expanded else ft.Icons.EXPAND_MORE
        self._page.update()
