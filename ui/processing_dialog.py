"""
处理进度弹窗 v1 - 全局步骤式模态

替代原先埋在页面底部的日志区（用户反馈：日志放下方无感知）。
处理开始时弹出模态，显示：
  - 标题（处理中 / 完成 / 出错）
  - 当前处理的文件名
  - 进度条 + 百分比
  - 结果列表（每个文件成功/失败 + 体积）
  - 完成/出错时的关闭按钮

调用方通过 start() / update_progress() / finish() / fail() 控制。
"""


import flet as ft
from datetime import datetime
from ui.theme import (
    tokens, FONT_SECTION, FONT_LABEL, FONT_BODY, FONT_META,
    SPACING_SM, SPACING_MD, SPACING_LG, PADDING_LG,
    RADIUS_CARD,
)


class ProcessingDialog:
    """处理进度模态弹窗（步骤式 loading + message）。

    生命周期：
        start()              -> 弹出「处理中」态
        update_progress(p)   -> 更新进度条/当前文件
        log_success/error()  -> 追加结果行
        finish(summary)      -> 切换为「完成」态（显示关闭按钮）
        fail(msg)            -> 切换为「出错」态
        close()              -> 关闭弹窗（重置）
    """

    def __init__(self, page: ft.Page):
        self._page = page
        self._closed_by_user = False

        t = tokens(page)

        # 状态图标 + 标题
        self._status_icon = ft.Icon(ft.Icons.AUTO_AWESOME_OUTLINED, size=28, color=t["accent"])
        self._title = ft.Text("正在处理", size=FONT_SECTION, weight=ft.FontWeight.W_600,
                              color=t["text_primary"])
        self._subtitle = ft.Text("正在压缩字体...", size=FONT_LABEL, color=t["text_secondary"])

        # 当前文件
        self._current_file = ft.Text("", size=FONT_META, color=t["text_tertiary"],
                                     font_family="monospace", max_lines=1,
                                     overflow=ft.TextOverflow.ELLIPSIS)

        # 进度条 + 百分比
        self._progress_bar = ft.ProgressBar(
            value=0, color=t["accent"], bgcolor=t["accent_bg"],
            bar_height=6, border_radius=3,
        )
        self._progress_pct = ft.Text("0%", size=FONT_META, color=t["text_secondary"],
                                     font_family="monospace")

        # 结果列表（可滚动）
        self._result_list = ft.ListView(spacing=4, auto_scroll=True, height=160)

        self._result_container = ft.Container(
            content=self._result_list,
            bgcolor=t["log_bg"],
            border=ft.border.all(1, t["border"]),
            border_radius=RADIUS_CARD - 4,
            padding=SPACING_SM,
            visible=False,  # 有结果时才显示
        )

        # 关闭按钮（完成/出错时显示）
        self._close_btn = ft.ElevatedButton(
            "完成", on_click=lambda e: self.close(),
            width=160, height=40,
            style=ft.ButtonStyle(
                bgcolor=t["accent"], color=t["accent_on"],
                shape=ft.RoundedRectangleBorder(radius=999),
                text_style=ft.TextStyle(size=FONT_BODY, weight=ft.FontWeight.W_500),
            ),
            visible=False,
        )

        content = ft.Column(
            [
                # 状态行
                ft.Row([self._status_icon, ft.Column([self._title, self._subtitle], spacing=2)],
                       spacing=SPACING_MD, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                # 当前文件
                self._current_file,
                # 进度行
                ft.Column([
                    self._progress_bar,
                    ft.Row([
                        ft.Container(expand=True),
                        self._progress_pct,
                    ], spacing=SPACING_SM),
                ], spacing=SPACING_SM),
                # 结果
                self._result_container,
                # 关闭按钮居中
                ft.Row([self._close_btn], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=SPACING_MD,
            tight=True,
            width=460,
        )

        self._dialog = ft.AlertDialog(
            modal=True,
            content=content,
            content_padding=PADDING_LG,
            bgcolor=t["surface"],
            on_dismiss=self._on_dismiss,
        )

    def _on_dismiss(self, e):
        self._closed_by_user = True

    def apply_theme(self):
        t = tokens(self._page)
        self._dialog.bgcolor = t["surface"]
        self._title.color = t["text_primary"]
        self._subtitle.color = t["text_secondary"]
        self._status_icon.color = t["accent"]
        self._current_file.color = t["text_tertiary"]
        self._progress_bar.color = t["accent"]
        self._progress_bar.bgcolor = t["accent_bg"]
        self._progress_pct.color = t["text_secondary"]
        self._result_container.bgcolor = t["log_bg"]
        self._result_container.border = ft.border.all(1, t["border"])
        self._close_btn.style.bgcolor = t["accent"]
        self._close_btn.style.color = t["accent_on"]

    # ------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------
    def start(self, total: int):
        """开始处理：弹出模态，进入「处理中」态。"""
        self._closed_by_user = False
        t = tokens(self._page)
        self._status_icon.icon = ft.Icons.AUTO_AWESOME_OUTLINED
        self._status_icon.color = t["accent"]
        self._title.value = "正在处理"
        self._subtitle.value = f"共 {total} 个文件"
        self._current_file.value = ""
        self._progress_bar.value = 0
        self._progress_pct.value = "0%"
        self._result_list.controls.clear()
        self._result_container.visible = False
        self._close_btn.visible = False
        self._show()

    def update_progress(self, value: float, current_file: str = ""):
        """更新进度（0.0-1.0）和当前文件名。"""
        self._progress_bar.value = min(max(value, 0.0), 1.0)
        self._progress_pct.value = f"{int(value * 100)}%"
        if current_file:
            self._current_file.value = current_file
        self._page.update()

    def log_success(self, message: str):
        t = tokens(self._page)
        self._add_result(message, t["success"], ft.Icons.CHECK_CIRCLE_OUTLINE, t)

    def log_error(self, message: str):
        t = tokens(self._page)
        self._add_result(message, t["error"], ft.Icons.CANCEL_OUTLINE, t)

    def _add_result(self, message: str, color: str, icon: str, t: dict):
        ts = datetime.now().strftime("%H:%M:%S")
        self._result_container.visible = True
        self._result_list.controls.append(
            ft.Row([
                ft.Icon(icon, size=14, color=color),
                ft.Text(message, size=FONT_META, color=color, expand=True,
                        max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
            ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.START)
        )
        self._page.update()

    def finish(self, summary: str):
        """处理完成：切「完成」态，显示关闭按钮。"""
        t = tokens(self._page)
        self._status_icon.icon = ft.Icons.CHECK_CIRCLE
        self._status_icon.color = t["success"]
        self._title.value = "处理完成"
        self._subtitle.value = summary
        self._current_file.value = ""
        self._progress_bar.value = 1.0
        self._progress_pct.value = "100%"
        self._close_btn.visible = True
        self._page.update()

    def fail(self, message: str):
        """处理出错：切「出错」态。"""
        t = tokens(self._page)
        self._status_icon.icon = ft.Icons.ERROR_OUTLINE
        self._status_icon.color = t["error"]
        self._title.value = "处理出错"
        self._subtitle.value = message
        self._close_btn.visible = True
        self._page.update()

    def close(self):
        """关闭弹窗并重置。"""
        self._dialog.open = False
        self._page.update()

    def _show(self):
        """显示弹窗。"""
        if self._dialog not in self._page.overlay:
            self._page.overlay.append(self._dialog)
        self._dialog.open = True
        self._page.update()
