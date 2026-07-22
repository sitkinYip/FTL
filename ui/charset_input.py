"""
字符集输入区组件 v4 - Apple 高密度工具风格

修复 v3 的拥挤问题：
  - 文本域给足高度（不再挤）
  - 预设 chips 用 wrap 流式换行
  - 操作按钮独立成行，不再与 chips 挤在一起
  - 字符数用等宽字体（§7）
"""

import flet as ft
from pathlib import Path
from ui.theme import (
    tokens,
    FONT_LABEL, FONT_BODY, FONT_HINT, FONT_META,
    SPACING_SM, SPACING_MD,
    BTN_CHIP_HEIGHT, RADIUS_INPUT, RADIUS_CHIP,
)
from utils.charset_presets import get_preset_names, get_preset_chars, deduplicate_chars


class CharsetInput(ft.Column):
    """字符集输入区组件"""

    def __init__(self, page: ft.Page):
        super().__init__(spacing=SPACING_SM)
        self._page = page
        self._txt_picker = ft.FilePicker()

        t = tokens(page)

        # 字符计数（右上角，等宽字体）
        self._char_count = ft.Text("0 个字符（去重后 0 个）",
                                   size=FONT_META, color=t["text_secondary"],
                                   font_family="monospace")

        # 文本域：给足高度，hairline 边框
        self._input = ft.TextField(
            label="输入或粘贴需要保留的字符",
            hint_text="例如：0123456789. 或粘贴一段中文文本",
            multiline=True,
            min_lines=3,
            max_lines=5,
            on_change=self._on_input_change,
            border_radius=RADIUS_INPUT,
            border_color=t["input_border"],
            focused_border_color=t["input_border_focus"],
            border_width=1,
            bgcolor=t["input_bg"],
            color=t["input_text"],
            hint_style=ft.TextStyle(color=t["text_hint"], size=FONT_HINT),
            label_style=ft.TextStyle(color=t["text_secondary"], size=FONT_LABEL),
            text_size=FONT_BODY,
            cursor_color=t["accent"],
        )

        # 预设标签
        self._preset_label = ft.Text("预设", size=FONT_HINT, color=t["text_tertiary"])

        # 预设 chips：pill 全圆，wrap 流式
        self._preset_chips = []
        for name in get_preset_names():
            self._preset_chips.append(
                ft.OutlinedButton(
                    name,
                    on_click=lambda e, n=name: self._apply_preset(n),
                    height=BTN_CHIP_HEIGHT,
                    style=ft.ButtonStyle(
                        color=t["text_primary"],
                        shape=ft.RoundedRectangleBorder(radius=RADIUS_CHIP),
                        side=ft.BorderSide(1, t["border_strong"]),
                        bgcolor=t["surface_sunken"],
                        text_style=ft.TextStyle(size=FONT_LABEL, weight=ft.FontWeight.W_500),
                    ),
                )
            )

        self._preset_row = ft.Row(
            [self._preset_label, *self._preset_chips],
            wrap=True, spacing=SPACING_SM, run_spacing=SPACING_SM,
        )

        # 操作按钮：独立一行，与 chips 分开
        self._action_row = ft.Row([
            ft.TextButton("从 TXT 导入", icon=ft.Icons.UPLOAD_FILE_OUTLINED,
                          on_click=self._pick_txt,
                          style=ft.ButtonStyle(color=t["text_secondary"])),
            ft.TextButton("去重", icon=ft.Icons.FILTER_ALT_OUTLINED,
                          on_click=self._deduplicate,
                          style=ft.ButtonStyle(color=t["text_secondary"])),
            ft.TextButton("清空", icon=ft.Icons.DELETE_OUTLINE,
                          on_click=self._clear_input,
                          style=ft.ButtonStyle(color=t["text_secondary"])),
        ], spacing=SPACING_MD)

        self.controls = [
            # 计数行
            ft.Row([ft.Container(expand=True), self._char_count]),
            self._input,
            # 预设 chips（wrap）
            self._preset_row,
            # 操作按钮（独立行）
            self._action_row,
        ]

    def apply_theme(self):
        t = tokens(self._page)
        self._char_count.color = t["text_secondary"]
        self._input.border_color = t["input_border"]
        self._input.focused_border_color = t["input_border_focus"]
        self._input.bgcolor = t["input_bg"]
        self._input.color = t["input_text"]
        self._input.hint_style = ft.TextStyle(color=t["text_hint"], size=FONT_HINT)
        self._input.label_style = ft.TextStyle(color=t["text_secondary"], size=FONT_LABEL)
        self._input.cursor_color = t["accent"]
        self._preset_label.color = t["text_tertiary"]
        for chip in self._preset_chips:
            chip.style.color = t["text_primary"]
            chip.style.side = ft.BorderSide(1, t["border_strong"])
            chip.style.bgcolor = t["surface_sunken"]
        for btn in self._action_row.controls:
            btn.style.color = t["text_secondary"]

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
                t = tokens(self._page)
                sb = ft.SnackBar(content=ft.Text(f"读取失败: {ex}", color="#FFFFFF"),
                                 bgcolor=t["error"])
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
