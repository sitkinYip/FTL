"""
文件选择区组件 v6 - AntD Upload 风格的选择区

两个真可用的入口统一到一块醒目区域：
  1. 点击 → 打开文件选择对话框
  2. ⌘V (mac) / Ctrl+V (win) → 全局粘贴，读取剪贴板文件路径

注：原生文件拖拽（Finder 拖进窗口）在 Flet 0.82 桌面端无干净绕过
（client-server 架构拿不到原生窗口句柄，无 PyObjC/tkinter），
故不提供拖拽入口，避免「能用却没反应」的误导。

设计参照 Ant Design Upload.Dragger：
  - 大块虚线边框区域
  - 居中图标 + 主提示 + 次提示
  - hover 视觉反馈
  - 下方文件列表（有文件时）

业务逻辑与公共属性不变。
"""

import subprocess
import flet as ft
from pathlib import Path
from ui.theme import (
    tokens,
    FONT_LABEL, FONT_BTN, FONT_BODY, FONT_HINT, FONT_META, FONT_SECTION,
    SPACING_SM, SPACING_MD,
    BTN_HEIGHT, RADIUS_INPUT, RADIUS_CARD,
)
from font.converter import SUPPORTED_INPUT_EXTENSIONS


class FilePicker(ft.Column):
    """文件选择区组件（AntD Upload 风格投放区 + 文件列表）"""

    def __init__(self, page: ft.Page):
        super().__init__(spacing=SPACING_MD)
        self._page = page
        self._selected_files: list[str] = []
        self._picker = ft.FilePicker()

        t = tokens(page)

        # —— 状态行 ——
        self._status = ft.Text("未选择文件", size=FONT_HINT, color=t["text_secondary"])

        self._clear_btn = ft.TextButton(
            "清空", icon=ft.Icons.DELETE_OUTLINE_OUTLINED, on_click=self._clear_files,
            style=ft.ButtonStyle(color=t["text_secondary"]),
            visible=False,
        )

        # —— 投放区图标 + 文案 ——
        self._drop_icon = ft.Icon(
            ft.Icons.CLOUD_UPLOAD_OUTLINED, size=40, color=t["accent"],
        )
        self._drop_title = ft.Text(
            "点击选择字体文件",
            size=FONT_BODY, weight=ft.FontWeight.W_500, color=t["text_primary"],
            text_align=ft.TextAlign.CENTER,
        )
        self._drop_hint = ft.Text(
            "支持 .ttf .otf .woff .woff2 · 也可在 Finder 复制后按 ⌘V 粘贴",
            size=FONT_HINT, color=t["text_secondary"],
            text_align=ft.TextAlign.CENTER,
        )

        # 选择区主体（虚线边框 + hover 态）
        drop_content = ft.Column(
            [self._drop_icon, self._drop_title, self._drop_hint],
            spacing=SPACING_SM,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self._drop_zone = ft.Container(
            content=drop_content,
            width=float("inf"),
            height=120,
            alignment=ft.Alignment(0, 0),  # 居中
            border=ft.border.all(2, t["border_strong"]),
            border_radius=RADIUS_CARD,
            bgcolor=t["surface_sunken"],
            on_click=self._pick_files,  # 点击打开对话框
            on_hover=self._on_hover,
            ink=True,  # 点击涟漪反馈
        )

        # —— 文件列表（有文件时显示）——
        self._file_list = ft.ListView(spacing=2, auto_scroll=True, height=90, visible=False)

        self.controls = [
            # 状态行
            ft.Row([
                self._status,
                ft.Container(expand=True),
                self._clear_btn,
            ], spacing=SPACING_SM),
            # 选择区
            self._drop_zone,
            # 文件列表
            self._file_list,
        ]

    # ------------------------------------------------------------
    # 主题
    # ------------------------------------------------------------
    def apply_theme(self):
        t = tokens(self._page)
        self._status.color = t["text_secondary"]
        self._clear_btn.style.color = t["text_secondary"]
        self._drop_icon.color = t["accent"]
        self._drop_title.color = t["text_primary"]
        self._drop_hint.color = t["text_secondary"]
        self._drop_zone.border = ft.border.all(2, t["border_strong"])
        self._drop_zone.bgcolor = t["surface_sunken"]
        self._refresh_list_colors()

    def _refresh_list_colors(self):
        """刷新已渲染文件列表项的颜色（主题切换时）。"""
        t = tokens(self._page)
        for row in self._file_list.controls:
            for ctrl in row.controls:
                if isinstance(ctrl, ft.Icon):
                    if ctrl.icon == ft.Icons.INSERT_DRIVE_FILE_OUTLINED:
                        ctrl.color = t["accent"]
                    else:
                        ctrl.color = t["text_tertiary"]

    # ------------------------------------------------------------
    # 公共属性
    # ------------------------------------------------------------
    @property
    def selected_files(self) -> list[str]:
        return self._selected_files.copy()

    # ------------------------------------------------------------
    # 全局键盘监听（⌘V / Ctrl+V）—— 由 main_view 转发
    # ------------------------------------------------------------
    def handle_paste(self):
        """处理粘贴动作：读取剪贴板并导入字体文件。

        由 MainView 的 on_keyboard_event 在检测到 ⌘V/Ctrl+V 时调用。
        """
        self._import_from_clipboard(None)

    # ------------------------------------------------------------
    # 选择区交互
    # ------------------------------------------------------------
    def _on_hover(self, e):
        """鼠标进入/离开选择区的视觉反馈。"""
        t = tokens(self._page)
        if e.data == "true":
            self._drop_zone.bgcolor = t["accent_bg"]
            self._drop_zone.border = ft.border.all(2, t["accent"])
        else:
            self._drop_zone.bgcolor = t["surface_sunken"]
            self._drop_zone.border = ft.border.all(2, t["border_strong"])
        self._page.update()

    # ------------------------------------------------------------
    # 文件添加 / 选择 / 粘贴
    # ------------------------------------------------------------
    def _import_from_clipboard(self, e):
        """从剪贴板导入文件路径（Finder ⌘C 复制的文件 / 或纯文本路径）。"""
        try:
            script = (
                'set theFiles to (the clipboard as «class furl») as text\n'
                'set posixPath to POSIX path of theFiles\n'
                'return posixPath'
            )
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=3
            )

            paths = []
            if result.returncode == 0 and result.stdout.strip():
                paths = [result.stdout.strip()]
            else:
                script_multi = (
                    'set fileList to (the clipboard as «class furl»)\n'
                    'set output to ""\n'
                    'repeat with f in fileList\n'
                    '  set output to output & (POSIX path of (f as text)) & linefeed\n'
                    'end repeat\n'
                    'return output'
                )
                result2 = subprocess.run(
                    ["osascript", "-e", script_multi],
                    capture_output=True, text=True, timeout=3
                )
                if result2.returncode == 0 and result2.stdout.strip():
                    paths = [l.strip() for l in result2.stdout.strip().split("\n") if l.strip()]

            if not paths:
                # fallback: pbpaste（用户可能用 ⌥⌘C 复制了路径文本）
                result3 = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=2)
                if result3.returncode == 0 and result3.stdout.strip():
                    paths = [l.strip().strip("'\"") for l in result3.stdout.strip().split("\n") if l.strip()]

            added = 0
            for p_str in paths:
                p = Path(p_str)
                if p.exists() and p.is_file():
                    ext = p.suffix.lower()
                    if ext in SUPPORTED_INPUT_EXTENSIONS and str(p) not in self._selected_files:
                        self._selected_files.append(str(p))
                        added += 1

            if added > 0:
                self._refresh_list()
                self._show_snack(f"已从剪贴板导入 {added} 个文件", tokens(self._page)["success"])
            else:
                self._show_snack("剪贴板中没有有效的字体文件（需 .ttf/.otf/.woff/.woff2）",
                                 tokens(self._page)["warning"])

        except Exception as ex:
            self._show_snack(f"读取剪贴板失败: {ex}", tokens(self._page)["error"])

    def _show_snack(self, msg: str, color: str):
        sb = ft.SnackBar(content=ft.Text(msg, color="#FFFFFF"), bgcolor=color)
        self._page.overlay.append(sb)
        sb.open = True
        self._page.update()

    async def _pick_files(self, e):
        result = await self._picker.pick_files(
            dialog_title="选择字体文件",
            allow_multiple=True,
            allowed_extensions=["ttf", "otf", "woff", "woff2"],
        )
        if result:
            for f in result:
                fp = f.path
                if fp and fp not in self._selected_files:
                    if Path(fp).suffix.lower() in SUPPORTED_INPUT_EXTENSIONS:
                        self._selected_files.append(fp)
            self._refresh_list()

    def _clear_files(self, e):
        self._selected_files.clear()
        self._refresh_list()

    def _remove_file(self, file_path: str):
        if file_path in self._selected_files:
            self._selected_files.remove(file_path)
            self._refresh_list()

    def _refresh_list(self):
        t = tokens(self._page)
        self._file_list.controls.clear()
        if not self._selected_files:
            self._status.value = "未选择文件"
            self._clear_btn.visible = False
            self._file_list.visible = False
        else:
            self._status.value = f"已选 {len(self._selected_files)} 个文件"
            self._clear_btn.visible = True
            self._file_list.visible = True
            for fp in self._selected_files:
                p = Path(fp)
                size_kb = p.stat().st_size / 1024 if p.exists() else 0
                self._file_list.controls.append(
                    ft.Row([
                        ft.Icon(ft.Icons.INSERT_DRIVE_FILE_OUTLINED, size=16, color=t["accent"]),
                        ft.Text(p.name, size=FONT_LABEL, color=t["text_primary"], expand=True),
                        # 文件大小用等宽字体
                        ft.Text(f"{size_kb:.0f} KB", size=FONT_META, color=t["text_secondary"],
                                font_family="monospace"),
                        ft.IconButton(ft.Icons.CLOSE_ROUNDED, icon_size=14,
                                      icon_color=t["text_tertiary"],
                                      on_click=lambda e, path=fp: self._remove_file(path)),
                    ], spacing=SPACING_SM)
                )
        self._page.update()
