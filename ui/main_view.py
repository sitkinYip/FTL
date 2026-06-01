"""
主界面布局 v2 - 深色毛玻璃多层级卡片
"""



import flet as ft
from ui.glass_panel import GlassPanel
from ui.theme import (
    PRIMARY, TEXT_PRIMARY, TEXT_LABEL, TEXT_DESC, TEXT_ON_PRIMARY,
    BG_PAGE, BG_GRADIENT_START, BG_GRADIENT_END,
    FONT_TITLE, FONT_SECTION, FONT_LABEL, FONT_BTN,
    PADDING_MD, SPACING_MD,
    BTN_HEIGHT, BTN_RADIUS,
)
from ui.file_picker import FilePicker
from ui.charset_input import CharsetInput
from ui.format_options import FormatOptions

from ui.progress_log import ProgressLog

from font.subsetter import subset_font
from font.converter import convert_and_save
from utils.file_utils import (
    get_output_dir, ensure_output_dir, get_output_basename, format_file_size,
)
from utils.async_worker import AsyncWorker


class MainView(ft.Container):
    """主界面容器"""

    def __init__(self, page: ft.Page):
        self._page = page
        self._worker = AsyncWorker(max_workers=2)
        self._processing = False

        # 子组件
        self._file_picker = FilePicker(page)
        self._charset_input = CharsetInput(page)
        self._format_options = FormatOptions(page)
        
        self._progress_log = ProgressLog(page)

        # 开始按钮
        self._start_btn = ft.ElevatedButton(
            "开始处理",
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            on_click=self._on_start,
            width=220,
            height=BTN_HEIGHT + 6,
            style=ft.ButtonStyle(
                bgcolor=PRIMARY,
                color=TEXT_ON_PRIMARY,
                shape=ft.RoundedRectangleBorder(radius=BTN_RADIUS),
                text_style=ft.TextStyle(size=FONT_BTN, weight=ft.FontWeight.W_600),
            ),
        )

        # 多层级卡片布局
        content_column = ft.Column(
            [
                # 顶部按钮（固定可见）
                ft.Container(
                    content=ft.Row(
                        controls=[self._start_btn],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.symmetric(vertical=SPACING_MD),
                ),
                # 标题
                ft.Container(
                    content=ft.Column([
                        ft.Text("FTL - Font Tool Lite", size=FONT_TITLE,
                                weight=ft.FontWeight.W_700, color=TEXT_PRIMARY),
                        ft.Text("字体子集压缩工具 · 保留所需字符，极致缩小体积",
                                size=FONT_LABEL, color=TEXT_DESC),
                    ], spacing=4),
                    padding=ft.padding.only(bottom=SPACING_MD),
                ),
                # 文件选择 - 浅层卡片
                GlassPanel(content=self._file_picker, depth="light"),
                # 字符集 - 中层卡片
                GlassPanel(content=self._charset_input, depth="mid"),
                # 输出格式 - 中层卡片
                GlassPanel(content=self._format_options, depth="mid"),
                # 高级选项 - 浅层

                # 进度日志 - 深层卡片（占满剩余空间）
                GlassPanel(content=self._progress_log, depth="deep"),
            ],
            spacing=SPACING_MD,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        # 外层深色渐变背景
        # 背景层（使用背景图片或纯色渐变）
        background = ft.Container(
            content=ft.Image(src="assets/background.jpg", fit="cover", opacity=0.6),
            expand=True,
        )
        super().__init__(
            content=ft.Stack(
                [
                    background,
                    ft.Container(content=content_column, padding=PADDING_MD, expand=True),
                ]
            ),
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[BG_GRADIENT_START, BG_GRADIENT_END],
            ),
        )

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

        self._progress_log.reset()
        self._progress_log.log_info(f"开始处理 {len(files)} 个文件，字符数: {len(characters)}")

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
        last = progress.results[-1] if progress.results else None

        self._progress_log.set_progress(
            pct, f"{progress.completed}/{progress.total} - {progress.current_file}")

        if last:
            if last.success:
                outputs = last.outputs
                flat = outputs[0] if isinstance(outputs, list) and outputs and isinstance(outputs[0], list) else outputs
                for item in (flat if isinstance(flat, list) else [flat]):
                    if isinstance(item, dict) and item.get("success"):
                        self._progress_log.log_success(
                            f"{last.input_file} -> {item['format']} ({format_file_size(item.get('size', 0))})")
                    elif isinstance(item, dict):
                        self._progress_log.log_error(
                            f"{last.input_file} -> {item.get('format','?')} 失败: {item.get('error','')}")
            else:
                self._progress_log.log_error(f"{last.input_file} 失败: {last.error}")

    def _on_all_complete(self, progress):
        ok = sum(1 for r in progress.results if r.success)
        fail = len(progress.results) - ok
        t = sum(r.elapsed for r in progress.results)

        self._progress_log.set_progress(1.0, "完成")
        self._progress_log.log_info(f"完成！成功 {ok}，失败 {fail}，耗时 {t:.2f}s")

        self._processing = False
        self._start_btn.disabled = False
        self._start_btn.text = "开始处理"
        self._page.update()

    def _show_error(self, message: str):
        sb = ft.SnackBar(content=ft.Text(message, color="#FFFFFF"), bgcolor="#FF5A5A")
        self._page.overlay.append(sb)
        sb.open = True
        self._page.update()
