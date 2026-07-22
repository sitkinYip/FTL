"""
输出格式与路径选项组件 v5 - Apple 高密度工具风格

变化（v5）：
  - 高级选项从内嵌折叠改为弹窗承载（由 MainView 持有 dialog）。
  - FormatOptions 接收外部注入的 AdvancedOptions 实例，仍暴露 advanced_options 属性。
  - 紧凑单列：格式复选 + 输出位置单选 + 自定义目录。

业务逻辑与公共属性不变。
"""

import flet as ft
from ui.theme import (
    tokens,
    FONT_LABEL, FONT_BODY, FONT_HINT,
    SPACING_SM, SPACING_MD,
)
from ui.advanced_options import AdvancedOptions


class FormatOptions(ft.Column):
    """输出格式与路径选项组件"""

    def __init__(self, page: ft.Page, advanced_options: AdvancedOptions):
        super().__init__(spacing=SPACING_MD)
        self._page = page
        self._advanced_options = advanced_options  # 由 MainView 注入（弹窗承载）
        t = tokens(page)

        # 格式复选框
        self._cb_woff2 = ft.Checkbox(label="WOFF2", value=True, active_color=t["accent"],
                                     check_color="#FFFFFF",
                                     label_style=ft.TextStyle(size=FONT_BODY, color=t["text_primary"]))
        self._cb_woff = ft.Checkbox(label="WOFF", value=True, active_color=t["accent"],
                                    check_color="#FFFFFF",
                                    label_style=ft.TextStyle(size=FONT_BODY, color=t["text_primary"]))
        self._cb_ttf = ft.Checkbox(label="TTF", value=True, active_color=t["accent"],
                                   check_color="#FFFFFF",
                                   label_style=ft.TextStyle(size=FONT_BODY, color=t["text_primary"]))

        self._format_label = ft.Text("格式", size=FONT_HINT, color=t["text_tertiary"])

        # 输出位置
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

        self._location_label = ft.Text("输出位置", size=FONT_HINT, color=t["text_tertiary"])

        self._dir_picker = ft.FilePicker()
        self._custom_dir_text = ft.Text("", size=FONT_HINT,
                                        color=t["text_secondary"], visible=False,
                                        font_family="monospace", max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS)
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

        self.controls = [
            self._format_label,
            ft.Row([self._cb_woff2, self._cb_woff, self._cb_ttf], spacing=SPACING_MD),
            self._location_label,
            self._output_mode,
            ft.Row([self._custom_dir_btn, self._custom_dir_text], spacing=SPACING_SM),
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
        self._format_label.color = t["text_tertiary"]
        self._location_label.color = t["text_tertiary"]
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
