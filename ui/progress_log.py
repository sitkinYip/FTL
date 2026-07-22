"""
进度条与日志区组件 v4 - Apple 高密度工具风格

作为全页唯一一块带底色面板（状态变化的功能区，§4.4 例外）。
预留固定高度，避免按下 Start 后布局跳动（§6.D）。
日志/时间戳用等宽字体（§7）。

所有 log_* 方法签名不变。
"""

import flet as ft
from datetime import datetime
from ui.theme import (
    tokens,
    FONT_LABEL, FONT_LOG, FONT_META,
    SPACING_SM, SPACING_MD, RADIUS_GROUP,
)


class ProgressLog(ft.Column):
    """进度条与日志区"""

    def __init__(self, page: ft.Page):
        super().__init__(spacing=SPACING_MD)
        self._page = page
        t = tokens(page)

        # 进度条：accent 填充 + 弱底轨道
        self._progress_bar = ft.ProgressBar(
            value=0,
            color=t["accent"],
            bgcolor=t["accent_bg"],
            bar_height=4,
            border_radius=2,
        )
        self._progress_text = ft.Text("就绪", size=FONT_META, color=t["text_secondary"],
                                      font_family="monospace")

        self._log_list = ft.ListView(spacing=2, auto_scroll=True, expand=True)

        # 日志容器：唯一带底色面板，预留固定高度
        self._log_container = ft.Container(
            content=self._log_list,
            border_radius=RADIUS_GROUP,
            bgcolor=t["log_bg"],
            padding=SPACING_SM,
            border=ft.border.all(1, t["border"]),
            height=110,
        )

        self.controls = [
            # 进度条行
            ft.Row([
                self._progress_bar,
                self._progress_text,
            ], spacing=SPACING_MD, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            self._log_container,
        ]

    def apply_theme(self):
        t = tokens(self._page)
        self._progress_bar.color = t["accent"]
        self._progress_bar.bgcolor = t["accent_bg"]
        self._progress_text.color = t["text_secondary"]
        self._log_container.bgcolor = t["log_bg"]
        self._log_container.border = ft.border.all(1, t["border"])

    def reset(self):
        self._progress_bar.value = 0
        self._progress_text.value = "就绪"
        self._log_list.controls.clear()
        self._page.update()

    def set_progress(self, value: float, text: str = ""):
        self._progress_bar.value = min(max(value, 0.0), 1.0)
        if text:
            self._progress_text.value = text
        self._page.update()

    def log_info(self, message: str):
        t = tokens(self._page)
        self._add_log(message, t["text_primary"], ft.Icons.INFO_OUTLINE, t)

    def log_success(self, message: str):
        t = tokens(self._page)
        self._add_log(message, t["success"], ft.Icons.CHECK_CIRCLE_OUTLINE, t)

    def log_error(self, message: str):
        t = tokens(self._page)
        self._add_log(message, t["error"], ft.Icons.ERROR_OUTLINE, t)

    def log_warning(self, message: str):
        t = tokens(self._page)
        self._add_log(message, t["warning"], ft.Icons.WARNING_AMBER_ROUNDED, t)

    def _add_log(self, message: str, color: str, icon: str, t: dict):
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_list.controls.append(
            ft.Row([
                ft.Icon(icon, size=13, color=color),
                ft.Text(ts, size=FONT_META, color=t["text_tertiary"], font_family="monospace"),
                ft.Text(message, size=FONT_LOG, color=color, expand=True),
            ], spacing=6)
        )
        self._page.update()
