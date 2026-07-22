"""
共享 UI 原语 v3 - Apple 高密度工具风格

设计原则（design-taste-frontend §4.4）：
  高密度工具（VISUAL_DENSITY > 7）禁止到处套卡片。
  用「分节标题 + 1px hairline 分隔线 + 留白」代替卡片框。
  仅进度/日志区作为唯一一块有底色的面板（状态变化的功能区）。
"""

import flet as ft
from ui.theme import tokens, FONT_SECTION, FONT_LABEL, FONT_HINT, SPACING_SM


class SectionHeader(ft.Row):
    """分节标题：左对齐标题 + 可选副标题/计数（右对齐）。

    遵循 skill §4.6：标题在控件上方；不写浮动角标说明（split-header ban §4.7）。
    """

    def __init__(self, page: ft.Page, title: str, trailing: ft.Control = None):
        self._page = page
        self._title_text = title
        t = tokens(page)
        super().__init__(
            controls=[
                ft.Text(title, size=FONT_SECTION, weight=ft.FontWeight.W_600,
                        color=t["text_primary"]),
                ft.Container(expand=True),
                trailing if trailing else ft.Container(),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )


def hairline(page: ft.Page) -> ft.Divider:
    """1px hairline 分隔线（替代卡片框，分组用）。"""
    t = tokens(page)
    return ft.Divider(height=1, color=t["divider"], thickness=1)


def hint_text(page: ft.Page, text: str) -> ft.Text:
    """说明文字：小一号、次级色、在控件下方。"""
    t = tokens(page)
    return ft.Text(text, size=FONT_HINT, color=t["text_secondary"])
