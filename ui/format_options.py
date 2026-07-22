"""
输出格式与路径选项组件 v4 - Apple 高密度工具风格

紧凑双列布局（§4.7 section-layout-repetition ban：与文件/字符集区结构不同）：
  左列：格式复选框（woff2/woff/ttf）
  右列：输出位置单选 + 自定义目录
  下方：高级选项（折叠）
不再套 GlassPanel。

业务逻辑与公共属性不变。
"""

import flet as ft
from ui.theme import (
    tokens,
    FONT_LABEL, FONT_BODY, FONT_HINT,
    SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL,
)
from ui.advanced_options import AdvancedOptions


class FormatOptions(ft.Column):
    """输出格式与路径选项组件"""

    def __init__(self, page: ft.Page):
        super().__init__(spacing=SPACING_MD)
        self._page = page
        t = tokens(page)

        # 格式复选框（左列）
        self._cb_woff2 = ft.Checkbox(label="WOFF2", value=True, active_color=t["accent"],
                                     check_color="#FFFFFF",
                                     label_style=ft.TextStyle(size=FONT_BODY, color=t["text_primary"]))
        self._cb_woff = ft.Checkbox(label="WOFF", value=True, active_color=t["accent"],
                                    check_color="#FFFFFF",
                                    label_style=ft.TextStyle(size=FONT_BODY, color=t["text_primary"]))
        self._cb_ttf = ft.Checkbox(label="TTF", value=True, active_color=t["accent"],
                                   check_color="#FFFFFF",
                                   label_style=ft.TextStyle(size=FONT_BODY, color=t["text_primary"]))

        self._format_col = ft.Column(
            [
                ft.Text("格式", size=FONT_HINT, color=t["text_tertiary"]),
                ft.Row([self._cb_woff2, self._cb_woff, self._cb_ttf], spacing=SPACING_MD),
            ],
            spacing=SPACING_SM,
        )

        # 输出位置（右列）
        self._output_mode = ft.RadioGroup(
            value="subdir",
            on_change=self._on_mode_change,
            content=ft.Column([
                ft.Radio(value="subdir", label="源文件同目录子文件夹",
                         active_color=t["accent"],
                         label_style=ft.TextStyle(size=FONT_LABEL, color=t["text_primary"])),
                ft.Radio(value="custom", label="自定义目录",
                         active_color=t["accent"],
                         label_style=ft.TextStyle(size=FONT_LABEL, color=t["text_primary"])),
            ], spacing=SPACING_SM),
        )

        self._dir_picker = ft.FilePicker()
        self._custom_dir_text = ft.Text("", size=FONT_HINT,
                                        color=t["text_secondary"], visible=False,
                                        font_family="monospace")
        self._custom_dir_btn = ft.OutlinedButton(
            "选择目录", icon=ft.Icons.FOLDER_OUTLINED,
            on_click=self._pick_dir, visible=False, height=32,
            style=ft.ButtonStyle(
                color=t["text_primary"],
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, t["border_strong"]),
                text_style=ft.TextStyle(size=FONT_LABEL),
                icon_color=t["text_primary"],
            ),
        )
        self._custom_dir_value: str = ""

        self._location_col = ft.Column(
            [
                ft.Text("输出位置", size=FONT_HINT, color=t["text_tertiary"]),
                self._output_mode,
                ft.Row([self._custom_dir_btn, self._custom_dir_text], spacing=SPACING_SM),
            ],
            spacing=SPACING_SM,
        )

        # 高级选项（折叠，下方整宽）
        self._advanced_options = AdvancedOptions(page)

        # 双列：格式 | 输出位置
        self._two_col = ft.Row(
            [self._format_col, self._location_col],
            spacing=SPACING_XL,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        self.controls = [
            self._two_col,
            self._advanced_options,
        ]

    def apply_theme(self):
        t = tokens(self._page)
        for cb in (self._cb_woff2, self._cb_woff, self._cb_ttf):
            cb.active_color = t["accent"]
            cb.label_style = ft.TextStyle(size=FONT_BODY, color=t["text_primary"])
        for radio in self._output_mode.content.controls:
            radio.active_color = t["accent"]
            radio.label_style = ft.TextStyle(size=FONT_LABEL, color=t["text_primary"])
        self._custom_dir_text.color = t["text_secondary"]
        self._custom_dir_btn.style.color = t["text_primary"]
        self._custom_dir_btn.style.side = ft.BorderSide(1, t["border_strong"])
        self._custom_dir_btn.style.icon_color = t["text_primary"]
        self._format_col.controls[0].color = t["text_tertiary"]
        self._location_col.controls[0].color = t["text_tertiary"]
        self._advanced_options.apply_theme()

    @property
    def selected_formats(self) -> list[str]:
        formats = []
        if self._cb_woff2.value:
            formats.append("woff2")
        if self._cb_woff.value:
            formats.append("woff")
        if self._cb_ttf.value:
            formats.append("ttf")
        return formats

    @property
    def output_mode(self) -> str:
        return self._output_mode.value

    @property
    def custom_dir(self) -> str:
        return self._custom_dir_value

    @property
    def advanced_options(self) -> AdvancedOptions:
        """暴露高级选项组件，供外部读取其 options_dict。"""
        return self._advanced_options

    def _on_mode_change(self, e):
        is_custom = self._output_mode.value == "custom"
        self._custom_dir_btn.visible = is_custom
        self._custom_dir_text.visible = is_custom
        self._page.update()

    async def _pick_dir(self, e):
        result = await self._dir_picker.get_directory_path(dialog_title="选择输出目录")
        if result:
            self._custom_dir_value = result
            self._custom_dir_text.value = result
            self._custom_dir_text.visible = True
            self._page.update()
