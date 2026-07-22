"""
输出格式与路径选项组件 v2 - 深色毛玻璃风格
"""

import flet as ft
from ui.theme import (
    TEXT_PRIMARY, TEXT_LABEL, TEXT_DESC,
    PRIMARY, DIVIDER_COLOR,
    FONT_SECTION, FONT_LABEL, FONT_BODY,
    SPACING_SM, SPACING_MD,
)
from ui.advanced_options import AdvancedOptions


class FormatOptions(ft.Column):
    """输出格式与路径选项组件"""

    def __init__(self, page: ft.Page):
        super().__init__(spacing=SPACING_SM)
        self._page = page

        self._cb_woff2 = ft.Checkbox(label="WOFF2", value=True, active_color=PRIMARY,
                                     check_color="#FFFFFF",
                                     label_style=ft.TextStyle(size=FONT_BODY, color=TEXT_PRIMARY))
        # 实例化高级选项组件
        self._advanced_options = AdvancedOptions(page)
        self._cb_woff = ft.Checkbox(label="WOFF", value=True, active_color=PRIMARY,
                                    check_color="#FFFFFF",
                                    label_style=ft.TextStyle(size=FONT_BODY, color=TEXT_PRIMARY))
        self._cb_ttf = ft.Checkbox(label="TTF", value=True, active_color=PRIMARY,
                                   check_color="#FFFFFF",
                                   label_style=ft.TextStyle(size=FONT_BODY, color=TEXT_PRIMARY))

        self._output_mode = ft.RadioGroup(
            value="subdir",
            on_change=self._on_mode_change,
            content=ft.Row([
                ft.Radio(value="subdir", label="源文件同目录子文件夹",
                         active_color=PRIMARY,
                         label_style=ft.TextStyle(size=FONT_LABEL, color=TEXT_PRIMARY)),
                ft.Radio(value="custom", label="自定义目录",
                         active_color=PRIMARY,
                         label_style=ft.TextStyle(size=FONT_LABEL, color=TEXT_PRIMARY)),
            ], spacing=SPACING_MD),
        )

        self._dir_picker = ft.FilePicker()
        self._custom_dir_text = ft.Text("", size=FONT_LABEL, color=TEXT_DESC, visible=False)
        self._custom_dir_btn = ft.TextButton("选择目录", icon=ft.Icons.FOLDER,
                                             on_click=self._pick_dir, visible=False,
                                             style=ft.ButtonStyle(color=TEXT_DESC))
        self._custom_dir_value: str = ""

        self.controls = [
            ft.Text("输出格式", size=FONT_SECTION, weight=ft.FontWeight.W_600, color=TEXT_LABEL),
            ft.Row([self._cb_woff2, self._cb_woff, self._cb_ttf], spacing=SPACING_SM),
            ft.Divider(height=1, color=DIVIDER_COLOR),
            ft.Text("输出位置", size=FONT_SECTION, weight=ft.FontWeight.W_600, color=TEXT_LABEL),
            self._output_mode,
            ft.Row([self._custom_dir_btn, self._custom_dir_text]),
            # 合并高级选项
            self._advanced_options,
        ]

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
