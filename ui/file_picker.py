"""
文件选择区组件 v4 - Apple 高密度工具风格

不再套 GlassPanel（高密度工具 §4.4 禁卡片）。作为分节内容直接呈现。
布局：状态行 → 按钮行 → 路径输入 → 文件列表（有文件时）。
文件大小 / 字符数用等宽字体（§7 mono for numbers）。

业务逻辑与公共属性不变。
"""

import subprocess
import flet as ft
from pathlib import Path
from ui.theme import (
    tokens,
    FONT_LABEL, FONT_BTN, FONT_BODY, FONT_HINT, FONT_META,
    SPACING_SM, SPACING_MD,
    BTN_HEIGHT, RADIUS_INPUT, RADIUS_BTN,
)
from font.converter import SUPPORTED_INPUT_EXTENSIONS


class FilePicker(ft.Column):
    """文件选择区组件（支持按钮选择 + 路径输入/拖拽）"""

    def __init__(self, page: ft.Page):
        super().__init__(spacing=SPACING_MD)
        self._page = page
        self._selected_files: list[str] = []
        self._picker = ft.FilePicker()

        t = tokens(page)

        # 状态文字（与按钮行同行右侧）
        self._status = ft.Text("未选择文件", size=FONT_HINT, color=t["text_secondary"])

        # 按钮行
        self._pick_btn = ft.ElevatedButton(
            "选择文件",
            icon=ft.Icons.FOLDER_OPEN_OUTLINED,
            on_click=self._pick_files,
            height=BTN_HEIGHT,
            style=ft.ButtonStyle(
                bgcolor=t["accent"],
                color=t["accent_on"],
                shape=ft.RoundedRectangleBorder(radius=RADIUS_BTN),
                text_style=ft.TextStyle(size=FONT_BTN, weight=ft.FontWeight.W_500),
                icon_color=t["accent_on"],
            ),
        )
        self._clipboard_btn = ft.OutlinedButton(
            "从剪贴板导入",
            icon=ft.Icons.CONTENT_PASTE_ROUNDED,
            on_click=self._import_from_clipboard,
            height=BTN_HEIGHT,
            tooltip="在 Finder 中选中文件按 ⌘C，然后点此导入",
            style=ft.ButtonStyle(
                color=t["text_primary"],
                shape=ft.RoundedRectangleBorder(radius=RADIUS_BTN),
                side=ft.BorderSide(1, t["border_strong"]),
                text_style=ft.TextStyle(size=FONT_BTN, weight=ft.FontWeight.W_500),
                icon_color=t["text_primary"],
            ),
        )
        self._clear_btn = ft.TextButton(
            "清空", icon=ft.Icons.CLEAR_ALL_OUTLINED, on_click=self._clear_files,
            style=ft.ButtonStyle(color=t["text_secondary"]),
        )

        # 路径输入框
        self._path_input = ft.TextField(
            hint_text="粘贴字体文件路径后按回车添加（支持多行）",
            hint_style=ft.TextStyle(color=t["text_hint"], size=FONT_HINT),
            border_radius=RADIUS_INPUT,
            border_color=t["input_border"],
            focused_border_color=t["input_border_focus"],
            border_width=1,
            bgcolor=t["input_bg"],
            color=t["input_text"],
            text_size=FONT_BODY,
            cursor_color=t["accent"],
            prefix_icon=ft.Icons.LINK_OUTLINED,
            on_submit=self._on_path_submit,
            multiline=True,
            min_lines=1,
            max_lines=2,
            suffix=ft.IconButton(
                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                icon_color=t["accent"],
                icon_size=20,
                on_click=self._pick_files,
                tooltip="选择文件",
            ),
        )

        # 文件列表（有文件时显示）
        self._file_list = ft.ListView(spacing=2, auto_scroll=True, height=100, visible=False)

        self.controls = [
            # 按钮行 + 状态
            ft.Row([
                self._pick_btn,
                self._clipboard_btn,
                self._clear_btn,
                ft.Container(expand=True),
                self._status,
            ], spacing=SPACING_SM),
            self._path_input,
            self._file_list,
        ]

    def apply_theme(self):
        t = tokens(self._page)
        self._status.color = t["text_secondary"]
        self._pick_btn.style.bgcolor = t["accent"]
        self._pick_btn.style.color = t["accent_on"]
        self._pick_btn.style.icon_color = t["accent_on"]
        self._clipboard_btn.style.color = t["text_primary"]
        self._clipboard_btn.style.side = ft.BorderSide(1, t["border_strong"])
        self._clipboard_btn.style.icon_color = t["text_primary"]
        self._clear_btn.style.color = t["text_secondary"]
        self._path_input.hint_style = ft.TextStyle(color=t["text_hint"], size=FONT_HINT)
        self._path_input.border_color = t["input_border"]
        self._path_input.focused_border_color = t["input_border_focus"]
        self._path_input.bgcolor = t["input_bg"]
        self._path_input.color = t["input_text"]
        self._path_input.cursor_color = t["accent"]

    @property
    def selected_files(self) -> list[str]:
        return self._selected_files.copy()

    def _on_path_submit(self, e):
        raw = self._path_input.value or ""
        lines = [l.strip().strip("'\"") for l in raw.split("\n") if l.strip()]
        added = False
        invalid = []
        for line in lines:
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
        self._path_input.value = ""
        self._path_input.error_text = None
        self._refresh_list()

    def _remove_file(self, file_path: str):
        if file_path in self._selected_files:
            self._selected_files.remove(file_path)
            self._refresh_list()

    def _refresh_list(self):
        t = tokens(self._page)
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
                        ft.Icon(ft.Icons.INSERT_DRIVE_FILE_OUTLINED, size=16, color=t["accent"]),
                        ft.Text(p.name, size=FONT_LABEL, color=t["text_primary"], expand=True),
                        # 文件大小用等宽字体（§7 mono for numbers）
                        ft.Text(f"{size_kb:.0f} KB", size=FONT_META, color=t["text_secondary"],
                                font_family="monospace"),
                        ft.IconButton(ft.Icons.CLOSE_ROUNDED, icon_size=14,
                                      icon_color=t["text_tertiary"],
                                      on_click=lambda e, path=fp: self._remove_file(path)),
                    ], spacing=SPACING_SM)
                )
        self._page.update()
