"""
进度条与日志区组件 v2 - 深色风格，亮色文字
"""

import flet as ft
from datetime import datetime
from ui.theme import (
    TEXT_LABEL, TEXT_DESC, LOG_BG, LOG_TEXT,
    PRIMARY, SUCCESS, ERROR, WARNING,
    FONT_SECTION, FONT_LABEL, FONT_LOG,
    SPACING_SM, SPACING_MD, RADIUS_SM,
)


class ProgressLog(ft.Column):
    """进度条与日志区"""

    def __init__(self, page: ft.Page):
        super().__init__(spacing=SPACING_MD)
        self._page = page

        self._progress_bar = ft.ProgressBar(
            value=0, color=PRIMARY, bgcolor="rgba(108,107,255,0.2)",
            bar_height=6, border_radius=3,
        )
        self._progress_text = ft.Text("就绪", size=FONT_LABEL, color=TEXT_DESC)

        self._log_list = ft.ListView(spacing=2, auto_scroll=True, expand=True)

        self.controls = [
            ft.Row([
                ft.Text("处理进度", size=FONT_SECTION, weight=ft.FontWeight.W_600, color=TEXT_LABEL),
                ft.Container(expand=True),
                self._progress_text,
            ]),
            self._progress_bar,
            ft.Container(
                content=self._log_list,
                border_radius=RADIUS_SM,
                bgcolor=LOG_BG,
                padding=10,
            ),
        ]

    def reset(self):
        self._progress_bar.value = 0
        self._progress_text.value = "就绪"
        self._log_list.controls.clear()
        self._log_list.visible = False
        self._page.update()

    def set_progress(self, value: float, text: str = ""):
        self._progress_bar.value = min(max(value, 0.0), 1.0)
        if text:
            self._progress_text.value = text
        self._page.update()

    def log_info(self, message: str):
        self._add_log(message, LOG_TEXT, ft.Icons.INFO_OUTLINE)

    def log_success(self, message: str):
        self._add_log(message, SUCCESS, ft.Icons.CHECK_CIRCLE_OUTLINE)

    def log_error(self, message: str):
        self._add_log(message, ERROR, ft.Icons.ERROR_OUTLINE)

    def log_warning(self, message: str):
        self._add_log(message, WARNING, ft.Icons.WARNING_AMBER)

    def _add_log(self, message: str, color: str, icon: str):
        ts = datetime.now().strftime("%H:%M:%S")
        if not self._log_list.visible:
            self._log_list.visible = True
        self._log_list.controls.append(
            ft.Row([
                ft.Icon(icon, size=14, color=color),
                ft.Text(ts, size=11, color=TEXT_DESC, font_family="monospace"),
                ft.Text(message, size=FONT_LOG, color=color, expand=True),
            ], spacing=6)
        )
        self._page.update()
