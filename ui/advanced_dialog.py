"""
高级选项弹窗 v2 - 模态承载 AdvancedOptions

修复 v1 弹窗过高留白：内容用 tight=True 收缩到开关组实际高度，
固定适中宽度，弹窗贴合内容不再撑出大片空白。
"""


import flet as ft
from ui.theme import (
    tokens, FONT_SECTION, FONT_BODY,
    PADDING_LG, SPACING_MD,
)
from ui.advanced_options import AdvancedOptions


class AdvancedDialog:
    """高级选项模态弹窗（贴合开关组高度）。"""

    def __init__(self, page: ft.Page):
        self._page = page
        self._advanced = AdvancedOptions(page)
        t = tokens(page)

        # 内容列：tight=True 让其收缩到开关组实际高度，不再留白
        content = ft.Column(
            [self._advanced],
            spacing=0,
            tight=True,
            width=360,
        )

        self._dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("高级选项", size=FONT_SECTION, weight=ft.FontWeight.W_600,
                          color=t["text_primary"]),
            content=content,
            content_padding=PADDING_LG,
            bgcolor=t["surface"],
            actions=[
                ft.TextButton("完成", on_click=lambda e: self.close(),
                              style=ft.ButtonStyle(color=t["accent"])),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    @property
    def advanced_options(self) -> AdvancedOptions:
        """暴露内部 AdvancedOptions，供外部读 options_dict。"""
        return self._advanced

    def apply_theme(self):
        t = tokens(self._page)
        self._dialog.bgcolor = t["surface"]
        self._dialog.title.color = t["text_primary"]
        self._advanced.apply_theme()
        self._dialog.actions[0].style.color = t["accent"]

    def open(self):
        """打开弹窗。"""
        if self._dialog not in self._page.overlay:
            self._page.overlay.append(self._dialog)
        self._dialog.open = True
        self._page.update()

    def close(self):
        """关闭弹窗。"""
        self._dialog.open = False
        self._page.update()
