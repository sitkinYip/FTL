"""
文件选择区组件 v2 - 深色毛玻璃风格
支持：按钮选择 + 从剪贴板导入（Finder ⌘C 后一键导入）+ 手动粘贴路径
"""

import subprocess
import flet as ft
from pathlib import Path
from ui.theme import (
    TEXT_PRIMARY, TEXT_LABEL, TEXT_DESC, TEXT_HINT, TEXT_ON_PRIMARY,
    PRIMARY, PRIMARY_LIGHT, ACCENT,
    INPUT_BG, INPUT_BORDER, INPUT_BORDER_FOCUS, INPUT_TEXT, INPUT_HINT,
    FONT_SECTION, FONT_LABEL, FONT_BTN, FONT_BODY, FONT_HINT,
    SPACING_SM, SPACING_MD,
    BTN_HEIGHT, BTN_CHIP_HEIGHT, BTN_RADIUS, RADIUS_INPUT,
)
from font.converter import SUPPORTED_INPUT_EXTENSIONS


class FilePicker(ft.Column):
    """文件选择区组件（支持按钮选择 + 路径输入/拖拽）"""

    def __init__(self, page: ft.Page):
        super().__init__(spacing=SPACING_MD)
        self._page = page
        self._selected_files: list[str] = []
        self._picker = ft.FilePicker()

        # 路径输入框：支持粘贴路径 / 多行路径
        self._path_input = ft.TextField(
            hint_text="粘贴字体文件路径后按回车添加（支持多行）",
            hint_style=ft.TextStyle(color=INPUT_HINT, size=FONT_HINT),
            border_radius=RADIUS_INPUT,
            border_color=INPUT_BORDER,
            focused_border_color=INPUT_BORDER_FOCUS,
            border_width=1.5,
            bgcolor=INPUT_BG,
            color=INPUT_TEXT,
            text_size=FONT_BODY,
            cursor_color=PRIMARY,
            prefix_icon=ft.Icons.FILE_DOWNLOAD_OUTLINED,
            on_submit=self._on_path_submit,
            multiline=True,
            min_lines=1,
            max_lines=3,
            suffix=ft.IconButton(
                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                icon_color=PRIMARY_LIGHT,
                icon_size=20,
                on_click=self._pick_files,
                tooltip="选择文件",
            ),
        )

        self._file_list = ft.ListView(spacing=SPACING_SM, auto_scroll=True, height=30, visible=False)
        self._status = ft.Text("未选择文件", size=FONT_LABEL, color=TEXT_DESC)

        self.controls = [
            ft.Row([
                # 左侧列：标题、按钮、路径输入
                ft.Column([
                    ft.Row([
                        ft.Text("字体文件", size=FONT_SECTION, weight=ft.FontWeight.W_600, color=TEXT_LABEL),
                        ft.Container(expand=True),
                        self._status,
                    ]),
                    ft.Row([
                        ft.ElevatedButton(
                            "选择文件",
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=self._pick_files,
                            height=BTN_HEIGHT,
                            style=ft.ButtonStyle(
                                bgcolor=PRIMARY,
                                color=TEXT_ON_PRIMARY,
                                shape=ft.RoundedRectangleBorder(radius=BTN_RADIUS),
                                text_style=ft.TextStyle(size=FONT_BTN, weight=ft.FontWeight.W_500),
                            ),
                        ),
                        ft.ElevatedButton(
                            "从剪贴板导入",
                            icon=ft.Icons.CONTENT_PASTE,
                            on_click=self._import_from_clipboard,
                            height=BTN_HEIGHT,
                            tooltip="在 Finder 中选中文件按 ⌘C，然后点此导入",
                            style=ft.ButtonStyle(
                                bgcolor="rgba(108,107,255,0.2)",
                                color=TEXT_LABEL,
                                shape=ft.RoundedRectangleBorder(radius=BTN_RADIUS),
                                text_style=ft.TextStyle(size=FONT_BTN, weight=ft.FontWeight.W_500),
                            ),
                        ),
                        ft.TextButton("清空", icon=ft.Icons.CLEAR_ALL, on_click=self._clear_files,
                                      style=ft.ButtonStyle(color=TEXT_DESC)),
                    ], spacing=SPACING_SM),
                    # 文件列表（有文件时才可见）
                    self._file_list,
                ], expand=True),
            ]),
        ]

    @property
    def selected_files(self) -> list[str]:
        return self._selected_files.copy()

    def _on_path_submit(self, e):
        """路径输入回车或点击添加按钮"""
        raw = self._path_input.value or ""
        # 支持多路径：换行分隔 or 空格分隔（但要兼容路径中有空格的情况）
        # 先按换行拆分，每行再尝试整行作为一个路径
        lines = [l.strip().strip("'\"") for l in raw.split("\n") if l.strip()]
        added = False
        invalid = []
        for line in lines:
            # 尝试整行作为路径
            p = Path(line)
            if p.exists() and p.is_file():
                ext = p.suffix.lower()
                if ext in SUPPORTED_INPUT_EXTENSIONS and str(p) not in self._selected_files:
                    self._selected_files.append(str(p))
                    added = True
            elif line:
                invalid.append(line)
        if added:
            self._path_input.value = ""
            self._path_input.error_text = None
            self._refresh_list()
        if invalid and not added:
            self._path_input.error_text = f"无效路径或不支持的格式: {invalid[0][:40]}"
            self._page.update()

    def _import_from_clipboard(self, e):
        """从 macOS 剪贴板导入文件路径（Finder 中 ⌘C 复制的文件）"""
        try:
            # 使用 osascript 获取 Finder 中复制的文件路径（POSIX path）
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
                # 单文件情况
                paths = [result.stdout.strip()]
            else:
                # 尝试多文件（alias list）
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
                # fallback: 尝试 pbpaste（用户可能用 ⌥⌘C 复制了路径文本）
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
                self._show_snack(f"已从剪贴板导入 {added} 个文件", "#5AE87C")
            else:
                self._show_snack("剪贴板中没有有效的字体文件（需 .ttf/.otf/.woff/.woff2）", "#FF9500")

        except Exception as ex:
            self._show_snack(f"读取剪贴板失败: {ex}", "#FF5A5A")

    def _show_snack(self, msg: str, color: str):
        """显示 SnackBar 提示"""
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
        self._path_input.value = ""
        self._path_input.error_text = None
        self._refresh_list()

    def _remove_file(self, file_path: str):
        if file_path in self._selected_files:
            self._selected_files.remove(file_path)
            self._refresh_list()

    def _refresh_list(self):
        self._file_list.controls.clear()
        self._path_input.error_text = None
        if not self._selected_files:
            self._status.value = "未选择文件"
            self._file_list.visible = False
        else:
            self._status.value = f"已选 {len(self._selected_files)} 个文件"
            self._file_list.visible = True
            for fp in self._selected_files:
                p = Path(fp)
                size_kb = p.stat().st_size / 1024 if p.exists() else 0
                self._file_list.controls.append(
                    ft.Row([
                        ft.Icon(ft.Icons.INSERT_DRIVE_FILE, size=16, color=PRIMARY_LIGHT),
                        ft.Text(p.name, size=FONT_LABEL, color=TEXT_PRIMARY, expand=True),
                        ft.Text(f"{size_kb:.0f} KB", size=FONT_LABEL, color=TEXT_DESC),
                        ft.IconButton(ft.Icons.CLOSE, icon_size=14, icon_color=TEXT_DESC,
                                      on_click=lambda e, path=fp: self._remove_file(path)),
                    ], spacing=SPACING_SM)
                )
        self._page.update()
