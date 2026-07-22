"""
FTL - Font Tool Lite
字体子集压缩工具入口

基于 Flet + fontTools，支持多格式输出（woff2/woff/ttf）。
Apple 风格双模 UI（跟随系统外观）。
"""

import flet as ft
from ui.main_view import MainView
from ui.theme import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    ACCENT_LIGHT, ACCENT_DARK,
)


def _build_theme(accent: str) -> ft.Theme:
    """构造一套主题（浅色或深色共用，仅 accent 与 mode 由调用方区分）。"""
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=accent,
            on_primary="#FFFFFF",
            primary_container=ft.Colors.with_opacity(0.12, accent),
            on_primary_container=accent,
            secondary=accent,
            surface="#FFFFFF",
            on_surface="#1D1D1F",
        ),
        color_scheme_seed=accent,
    )


def main(page: ft.Page):
    """应用主入口"""
    # 窗口配置
    page.title = "FTL - Font Tool Lite"
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.window.min_width = WINDOW_MIN_WIDTH
    page.window.min_height = WINDOW_MIN_HEIGHT

    # 透明背景，由 MainView 接管（使其可随模式切换）
    page.padding = 0
    page.spacing = 0

    # macOS 标题栏
    page.window.title_bar_hidden = False

    # 跟随系统外观：同时装配浅 / 深两套主题
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.theme = _build_theme(ACCENT_LIGHT)
    page.dark_theme = _build_theme(ACCENT_DARK)

    # 主界面
    main_view = MainView(page)
    page.add(main_view)

    def _on_brightness_change(e):
        """系统外观切换时刷新整个视图（重算令牌、背景、卡片色）。"""
        main_view.apply_theme()
        page.update()

    page.on_platform_brightness_change = _on_brightness_change

    # 全局键盘监听：⌘V / Ctrl+V 粘贴字体文件
    page.on_keyboard_event = main_view.on_keyboard


if __name__ == "__main__":
    ft.app(target=main)  # 兼容旧版；Flet 0.80+ 可用 ft.run(main)
