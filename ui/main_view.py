"""
主界面布局 v6 - Apple 高密度工具风格（上传铺满 + 双列配置）

Design Read（design-taste-frontend §0.B）:
  紧凑型字体子集化工具，Linear / Apple System Preferences 语言，
  高密度（VISUAL_DENSITY 8）/ 低变化（VARIANCE 3）/ 低动效（MOTION 2）。

布局策略（单屏装下，无需滚动）：
    ┌────────────────────────────────────────────────┐
    │ 品牌行                                         │
    ├────────────────────────────────────────────────┤
    │ 投放区（上传）铺满整宽                          │
    │ ☁ 点击 / 拖拽 / ⌘V 粘贴                       │
    ├────────────────────────┬───────────────────────┤
    │ 字符集                 │ 输出格式              │
    │ （文本域 + 预设）      │ （复选 + 位置）       │
    │                        │ [高级选项]（弹窗）    │
    ├────────────────────────┴───────────────────────┤
    │            [ 开始处理 ]（底部固定）            │
    └────────────────────────────────────────────────┘
  高级选项通过弹窗承载（不再内嵌折叠）。
  处理进度通过全局模态弹窗显示，不再埋底部日志。

业务逻辑（_on_start / _process_single_file / 回调）不变。
所有子组件的公共属性 / 方法签名保持不变。
"""


from pathlib import Path

import flet as ft
from ui.theme import (
    tokens, FONT_DISPLAY, FONT_LABEL, FONT_HINT,
    SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL,
    PADDING_LG, BTN_HEIGHT_LG, RADIUS_BTN_PILL,
)
from ui.widgets import SectionHeader
from ui.file_picker import FilePicker
from ui.charset_input import CharsetInput
from ui.format_options import FormatOptions
from ui.advanced_dialog import AdvancedDialog
from ui.processing_dialog import ProcessingDialog

from font.subsetter import subset_font
from font.converter import convert_and_save
from utils.file_utils import (
    get_output_dir, ensure_output_dir, get_output_basename, format_file_size,
)
from utils.async_worker import AsyncWorker


class MainView(ft.Container):
    """主界面容器（Apple 工具风格：上传铺满 + 双列配置）"""

    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self._page = page
        self._worker = AsyncWorker(max_workers=2)
        self._processing = False

        # 高级选项弹窗（先建，FormatOptions 引用其 advanced_options）
        self._advanced_dialog = AdvancedDialog(page)

        # 子组件（公共 API 不变）
        self._file_picker = FilePicker(page)
        self._charset_input = CharsetInput(page)
        self._format_options = FormatOptions(page, self._advanced_dialog.advanced_options)

        # 处理进度弹窗（替代原 ProgressLog）
        self._dialog = ProcessingDialog(page)

        t = tokens(page)

        # 开始按钮
        self._start_btn = ft.ElevatedButton(
            "开始处理",
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            on_click=self._on_start,
            width=220,
            height=BTN_HEIGHT_LG,
            style=ft.ButtonStyle(
                bgcolor=t["accent"],
                color=t["accent_on"],
                shape=ft.RoundedRectangleBorder(radius=RADIUS_BTN_PILL),
                text_style=ft.TextStyle(size=FONT_LABEL, weight=ft.FontWeight.W_600),
                icon_color=t["accent_on"],
            ),
        )

        # 高级选项触发按钮（放输出格式区标题旁）
        self._advanced_btn = ft.TextButton(
            "高级选项", icon=ft.Icons.TUNE_OUTLINED,
            on_click=lambda e: self._advanced_dialog.open(),
            style=ft.ButtonStyle(color=t["text_secondary"]),
        )

        # 品牌行
        self._brand_title = ft.Text(
            "FTL", size=FONT_DISPLAY, weight=ft.FontWeight.W_700,
            color=t["text_primary"],
        )
        self._brand_name = ft.Text(
            "Font Tool Lite", size=FONT_DISPLAY, weight=ft.FontWeight.W_400,
            color=t["text_secondary"],
        )
        self._brand_desc = ft.Text(
            "字体子集压缩工具",
            size=FONT_HINT, color=t["text_tertiary"],
        )

        self._build_layout()
        self.apply_theme()

    # ------------------------------------------------------------
    # 布局构建
    # ------------------------------------------------------------
    def _build_layout(self):
        """上传铺满 → 字符集/输出格式双列 → 底部开始按钮。"""

        # 品牌行
        brand_row = ft.Row(
            [
                ft.Row([self._brand_title, self._brand_name], spacing=8,
                       vertical_alignment=ft.CrossAxisAlignment.END),
                ft.Container(expand=True),
                self._brand_desc,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.END,
        )

        # 上传区（铺满整宽）—— FilePicker 自带投放区，直接整块放
        upload_section = ft.Column(
            [self._file_picker],
            spacing=0,
        )

        # 左列：字符集
        header_charset = ft.Row([
            ft.Text("字符集", size=17, weight=ft.FontWeight.W_600,
                    color=tokens(self._page)["text_primary"]),
        ])
        left_col = ft.Column(
            [header_charset, self._charset_input],
            spacing=SPACING_MD,
            expand=True,
        )

        # 右列：输出格式（标题带「高级选项」按钮）
        header_output = ft.Row([
            ft.Text("输出格式", size=17, weight=ft.FontWeight.W_600,
                    color=tokens(self._page)["text_primary"]),
            ft.Container(expand=True),
            self._advanced_btn,
        ])
        right_col = ft.Column(
            [header_output, self._format_options],
            spacing=SPACING_MD,
            expand=True,
        )

        # 双列：字符集 | 输出格式
        config_row = ft.Row(
            [left_col, right_col],
            spacing=SPACING_XL,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        )

        # 底部固定开始按钮栏
        start_bar = ft.Container(
            content=ft.Row(
                [self._start_btn],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(top=SPACING_SM, bottom=SPACING_SM),
        )

        self._header_charset = header_charset.controls[0]
        self._header_output = header_output.controls[0]

        self.padding = PADDING_LG
        self.content = ft.Column(
            [brand_row, upload_section, config_row, start_bar],
            spacing=SPACING_LG,
            expand=True,
        )

    # ------------------------------------------------------------
    # 主题应用
    # ------------------------------------------------------------
    def apply_theme(self):
        t = tokens(self._page)

        self.gradient = ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=[t["canvas"], t["canvas_gradient_end"]],
        )

        self._brand_title.color = t["text_primary"]
        self._brand_name.color = t["text_secondary"]
        self._brand_desc.color = t["text_tertiary"]

        self._start_btn.style.bgcolor = t["accent"]
        self._start_btn.style.color = t["accent_on"]
        self._start_btn.style.icon_color = t["accent_on"]

        self._header_charset.color = t["text_primary"]
        self._header_output.color = t["text_primary"]
        self._advanced_btn.style.color = t["text_secondary"]

        for comp in (self._file_picker, self._charset_input, self._format_options):
            comp.apply_theme()

        self._advanced_dialog.apply_theme()
        self._dialog.apply_theme()

    # ------------------------------------------------------------
    # 全局键盘监听（⌘V / Ctrl+V 粘贴字体文件）
    # ------------------------------------------------------------
    def on_keyboard(self, e: ft.KeyboardEvent):
        """全局键盘事件：检测粘贴动作（mac ⌘V / win Ctrl+V）。"""
        is_paste = (e.key == "V" or e.key == "v") and (e.meta or e.ctrl)
        if is_paste and not self._processing:
            self._file_picker.handle_paste()

    # ------------------------------------------------------------
    # 业务逻辑（不变，进度改为弹窗反馈）
    # ------------------------------------------------------------
    def _on_start(self, e):
        if self._processing:
            return

        files = self._file_picker.selected_files
        if not files:
            self._show_error("请先选择至少一个字体文件")
            return

        characters = self._charset_input.characters
        if not characters:
            self._show_error("请输入需要保留的字符集")
            return

        formats = self._format_options.selected_formats
        if not formats:
            self._show_error("请至少选择一种输出格式")
            return

        self._processing = True
        self._start_btn.disabled = True
        self._start_btn.text = "处理中..."
        self._page.update()

        # 弹出处理弹窗
        self._dialog.start(total=len(files))

        tasks = []
        for fp in files:
            tasks.append({
                "fn": self._process_single_file,
                "args": (fp, characters, formats),
                "file_name": Path(fp).name,
            })

        self._worker.submit_batch(
            tasks=tasks,
            on_progress=self._on_progress,
            on_all_complete=self._on_all_complete,
        )

    def _process_single_file(self, file_path, characters, formats):
        input_path = Path(file_path)
        options_dict = self._format_options.advanced_options.options_dict

        output_dir = get_output_dir(
            input_path,
            mode=self._format_options.output_mode,
            custom_dir=self._format_options.custom_dir,
        )
        ensure_output_dir(output_dir)

        font = subset_font(input_path, characters, options_dict)
        base_name = get_output_basename(input_path)
        results = convert_and_save(font, output_dir, base_name, formats)
        font.close()
        return results

    def _on_progress(self, progress):
        pct = progress.progress
        self._dialog.update_progress(pct, progress.current_file)

        last = progress.results[-1] if progress.results else None
        if last:
            if last.success:
                outputs = last.outputs
                flat = outputs[0] if isinstance(outputs, list) and outputs and isinstance(outputs[0], list) else outputs
                for item in (flat if isinstance(flat, list) else [flat]):
                    if isinstance(item, dict) and item.get("success"):
                        self._dialog.log_success(
                            f"{last.input_file} -> {item['format']} ({format_file_size(item.get('size', 0))})")
                    elif isinstance(item, dict):
                        self._dialog.log_error(
                            f"{last.input_file} -> {item.get('format','?')} 失败: {item.get('error','')}")
            else:
                self._dialog.log_error(f"{last.input_file} 失败: {last.error}")

    def _on_all_complete(self, progress):
        ok = sum(1 for r in progress.results if r.success)
        fail = len(progress.results) - ok
        elapsed = sum(r.elapsed for r in progress.results)

        self._dialog.finish(f"成功 {ok} · 失败 {fail} · 耗时 {elapsed:.2f}s")

        self._processing = False
        self._start_btn.disabled = False
        self._start_btn.text = "开始处理"
        self._page.update()

    def _show_error(self, message: str):
        t = tokens(self._page)
        sb = ft.SnackBar(content=ft.Text(message, color="#FFFFFF"), bgcolor=t["error"])
        self._page.overlay.append(sb)
        sb.open = True
        self._page.update()
