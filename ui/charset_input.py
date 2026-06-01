"""
字符集输入区组件 v2 - 深色毛玻璃风格
"""

import flet as ft
from pathlib import Path
from ui.theme import (
    TEXT_PRIMARY, TEXT_LABEL, TEXT_DESC, TEXT_HINT, TEXT_ON_PRIMARY,
    PRIMARY, INPUT_BG, INPUT_BORDER, INPUT_BORDER_FOCUS, INPUT_TEXT, INPUT_HINT,
    FONT_SECTION, FONT_LABEL, FONT_BODY, FONT_BTN, FONT_HINT,
    SPACING_SM, SPACING_MD,
    BTN_CHIP_HEIGHT, BTN_RADIUS, RADIUS_INPUT,
)
from utils.charset_presets import get_preset_names, get_preset_chars, deduplicate_chars


class CharsetInput(ft.Column):
    """字符集输入区组件"""

    def __init__(self, page: ft.Page):
        super().__init__(spacing=SPACING_SM)
        self._page = page
        self._txt_picker = ft.FilePicker()

        self._input = ft.TextField(
            label="输入或粘贴需要保留的字符",
            hint_text="例如：0123456789. 或粘贴一段中文文本",
            multiline=True,
            min_lines=2,
            max_lines=4,
            on_change=self._on_input_change,
            border_radius=RADIUS_INPUT,
            border_color=INPUT_BORDER,
            focused_border_color=INPUT_BORDER_FOCUS,
            border_width=1.5,
            bgcolor=INPUT_BG,
            color=INPUT_TEXT,
            hint_style=ft.TextStyle(color=INPUT_HINT, size=FONT_HINT),
            label_style=ft.TextStyle(color=TEXT_DESC, size=FONT_LABEL),
            text_size=FONT_BODY,
            cursor_color=PRIMARY,
            expand=True,
        )

        self._char_count = ft.Text("0 个字符（去重后 0 个）", size=FONT_LABEL, color=TEXT_DESC)

        preset_chips = []
        for name in get_preset_names():
            preset_chips.append(
                ft.OutlinedButton(
                    name,
                    on_click=lambda e, n=name: self._apply_preset(n),
                    height=BTN_CHIP_HEIGHT,
                    style=ft.ButtonStyle(
                        color=TEXT_LABEL,
                        shape=ft.RoundedRectangleBorder(radius=BTN_RADIUS),
                        side=ft.BorderSide(1, INPUT_BORDER),
                        text_style=ft.TextStyle(size=FONT_LABEL),
                    ),
                )
            )

        self.controls = [
            ft.Row([
                ft.Text("字符集", size=FONT_SECTION, weight=ft.FontWeight.W_600, color=TEXT_LABEL),
                ft.Container(expand=True),
                self._char_count,
            ]),
            self._input,
            ft.Row(
                [ft.Text("预设：", size=FONT_LABEL, color=TEXT_DESC), *preset_chips],
                wrap=True, spacing=SPACING_SM, run_spacing=SPACING_SM, expand=True,
            ),
            ft.Row([
                ft.TextButton("从 TXT 导入", icon=ft.Icons.UPLOAD_FILE, on_click=self._pick_txt,
                              style=ft.ButtonStyle(color=TEXT_DESC)),
                ft.TextButton("去重", icon=ft.Icons.FILTER_ALT, on_click=self._deduplicate,
                              style=ft.ButtonStyle(color=TEXT_DESC)),
                ft.TextButton("清空", icon=ft.Icons.DELETE_OUTLINE, on_click=self._clear_input,
                              style=ft.ButtonStyle(color=TEXT_DESC)),
            ], expand=True),
        ]

    @property
    def characters(self) -> str:
        return deduplicate_chars(self._input.value or "")

    @property
    def raw_text(self) -> str:
        return self._input.value or ""

    def _on_input_change(self, e):
        raw = self._input.value or ""
        unique = deduplicate_chars(raw)
        self._char_count.value = f"{len(raw)} 个字符（去重后 {len(unique)} 个）"
        self._page.update()

    def _apply_preset(self, preset_name: str):
        chars = get_preset_chars(preset_name)
        current = self._input.value or ""
        self._input.value = current + chars
        self._on_input_change(None)
        self._page.update()

    async def _pick_txt(self, e):
        result = await self._txt_picker.pick_files(
            dialog_title="选择字符集文本文件",
            allow_multiple=False,
            allowed_extensions=["txt"],
        )
        if result:
            file_path = result[0].path
            if not file_path:
                return
            try:
                content = Path(file_path).read_text(encoding="utf-8")
                current = self._input.value or ""
                self._input.value = current + content
                self._on_input_change(None)
                self._page.update()
            except Exception as ex:
                sb = ft.SnackBar(content=ft.Text(f"读取失败: {ex}", color="#FFFFFF"), bgcolor="#FF3B30")
                self._page.overlay.append(sb)
                sb.open = True
                self._page.update()

    def _deduplicate(self, e):
        self._input.value = deduplicate_chars(self._input.value or "")
        self._on_input_change(None)
        self._page.update()

    def _clear_input(self, e):
        self._input.value = ""
        self._on_input_change(None)
        self._page.update()
