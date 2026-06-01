"""
FTL - Font Tool Lite
字体子集压缩工具入口

基于 Flet + fontTools，支持多格式输出（woff2/woff/ttf）。
iOS 18 毛玻璃风格 UI。
"""

import flet as ft
from ui.main_view import MainView
from ui.theme import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT


def main(page: ft.Page):
    """应用主入口"""
    # 窗口配置
    page.title = "FTL - Font Tool Lite"
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.window.min_width = WINDOW_MIN_WIDTH
    page.window.min_height = WINDOW_MIN_HEIGHT

    # 深色背景
    page.bgcolor = "#0F0E1A"
    page.padding = 0
    page.spacing = 0

    # macOS 标题栏风格
    page.window.title_bar_hidden = False

    # 深色主题
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.DEEP_PURPLE,
    )

    # 加载主界面
    main_view = MainView(page)
    page.add(main_view)


if __name__ == "__main__":
    ft.app(target=main)  # 兼容旧版；Flet 0.80+ 可用 ft.run(main)
