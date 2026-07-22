"""
FTL 主题令牌 v3 - Apple 风格双模设计系统

跟随系统外观（浅色/深色），单一锁定强调色（Apple 系统蓝）。
所有语义令牌按模式分组，组件统一通过 tokens(page) 取值。

设计原则（迁移自 design-taste-frontend / high-end-visual-design）：
  - COLOR CONSISTENCY LOCK: 全页仅一个强调色
  - SHAPE CONSISTENCY LOCK: 统一圆角尺度（card 20 / input 12 / pill 全圆）
  - 阴影 tinted 到背景色，无纯黑投影
  - 无 AI 紫渐变、无 mesh 辉光、无外发光
  - 无 em-dash，无占位假名
"""

import flet as ft


# ============================================================
# 强调色（COLOR CONSISTENCY LOCK - 全页唯一）
# Apple 系统蓝：浅色 #0071E3，深色 #0A84FF
# ============================================================

ACCENT_LIGHT = "#0071E3"
ACCENT_HOVER_LIGHT = "#0077ED"
ACCENT_DARK = "#0A84FF"
ACCENT_HOVER_DARK = "#409CFF"


# ============================================================
# 状态色（跨模式语义色，Apple 系统色板）
# ============================================================

SUCCESS_LIGHT = "#1D8C3E"
SUCCESS_DARK = "#30D158"
WARNING_LIGHT = "#C27300"
WARNING_DARK = "#FFD60A"
ERROR_LIGHT = "#D70015"
ERROR_DARK = "#FF453A"


# ============================================================
# 圆角尺度（SHAPE CONSISTENCY LOCK）
# ============================================================

RADIUS_CARD = 20       # 卡片 / 玻璃面板
RADIUS_INPUT = 12      # 输入框
RADIUS_GROUP = 14      # 日志区等次级容器
RADIUS_CHIP = 999      # pill / chip 全圆
RADIUS_BTN = 12        # 普通按钮
RADIUS_BTN_PILL = 999  # 主 CTA 全圆


# ============================================================
# 间距（8 倍数体系）
# ============================================================

SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 12
SPACING_LG = 16
SPACING_XL = 24
SPACING_XXL = 32

PADDING_SM = 12
PADDING_MD = 16
PADDING_LG = 20
PADDING_XL = 28


# ============================================================
# 字号（SF 语义层级）
# ============================================================

FONT_DISPLAY = 24   # 品牌标题
FONT_TITLE = 20     # 卡片内大标题
FONT_SECTION = 17   # 分区标题（SF Large Title 语义）
FONT_LABEL = 13     # 标签 / 次级
FONT_BODY = 15      # 正文 / 输入
FONT_BTN = 15       # 按钮文字
FONT_LOG = 13       # 日志
FONT_HINT = 13      # 提示 / 占位
FONT_META = 11      # 时间戳等元信息


# ============================================================
# 按钮
# ============================================================

BTN_HEIGHT = 36       # Apple HIG 常规按钮（控钮）
BTN_HEIGHT_LG = 44    # 主 CTA / Apple HIG 大按钮
BTN_CHIP_HEIGHT = 32


# ============================================================
# 窗口尺寸
# ============================================================

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 780
WINDOW_MIN_WIDTH = 720
WINDOW_MIN_HEIGHT = 600


# ============================================================
# 双模语义令牌
# ============================================================

_LIGHT = {
    # 画布与表面
    "canvas": "#F5F5F7",            # Apple 灰白
    "canvas_gradient_end": "#ECECEF",
    "surface": "#FFFFFF",           # 实心卡片
    "surface_elevated": "#FFFFFF",
    "surface_sunken": "#F2F2F4",    # 凹陷区（输入框底 / 日志底）
    "surface_hover": "#EFEFF2",

    # 玻璃 / 边框（卡片用实色白，hairline 边框）
    "glass_bg": "#FFFFFF",
    "glass_bg_elevated": "#FFFFFF",
    "border": "rgba(60, 60, 67, 0.12)",        # Apple 标准 hairline
    "border_strong": "rgba(60, 60, 67, 0.29)",
    "border_focus": ACCENT_LIGHT,
    "divider": "rgba(60, 60, 67, 0.18)",

    # 文字层级
    "text_primary": "#1D1D1F",     # Apple ink
    "text_secondary": "#6E6E73",
    "text_tertiary": "#86868B",
    "text_on_accent": "#FFFFFF",
    "text_hint": "#8E8E93",

    # 输入框
    "input_bg": "#F5F5F7",
    "input_border": "rgba(60, 60, 67, 0.18)",
    "input_border_focus": ACCENT_LIGHT,
    "input_text": "#1D1D1F",

    # 强调与状态
    "accent": ACCENT_LIGHT,
    "accent_hover": ACCENT_HOVER_LIGHT,
    "accent_bg": "rgba(0, 113, 227, 0.10)",    # accent 弱底（进度条轨道 / 选中 chip）
    "accent_on": "#FFFFFF",
    "success": SUCCESS_LIGHT,
    "warning": WARNING_LIGHT,
    "error": ERROR_LIGHT,

    # 日志
    "log_bg": "#F5F5F7",
    "log_text": "#1D1D1F",

    # 阴影（tinted 黑，漫射）
    "shadow_card": {"offset_y": 1, "blur": 6, "color": "rgba(0, 0, 0, 0.08)"},
    "shadow_card_elevated": {"offset_y": 8, "blur": 30, "color": "rgba(0, 0, 0, 0.10)"},
    # inset 高光（近似 Liquid Glass 上边缘反光，诚实标注非官方材质）
    "inset_highlight": "rgba(255, 255, 255, 0.6)",
}

_DARK = {
    # 画布与表面（canvas 用深灰而非纯黑，避免卡片融进背景）
    "canvas": "#161617",
    "canvas_gradient_end": "#0E0E10",
    "surface": "#1C1C1E",
    "surface_elevated": "#2C2C2E",
    "surface_sunken": "#0E0E0F",
    "surface_hover": "#3A3A3C",

    # 玻璃 / 边框（卡片用实色更稳，边框加亮让卡片与背景分离）
    "glass_bg": "#242426",
    "glass_bg_elevated": "#2C2C2E",
    "border": "rgba(255, 255, 255, 0.12)",
    "border_strong": "rgba(255, 255, 255, 0.28)",
    "border_focus": ACCENT_DARK,
    "divider": "rgba(255, 255, 255, 0.14)",

    # 文字层级
    "text_primary": "#F5F5F7",
    "text_secondary": "#AEAEB2",
    "text_tertiary": "#8E8E93",
    "text_on_accent": "#FFFFFF",
    "text_hint": "#636366",

    # 输入框
    "input_bg": "#0E0E0F",
    "input_border": "rgba(255, 255, 255, 0.18)",
    "input_border_focus": ACCENT_DARK,
    "input_text": "#F5F5F7",

    # 强调与状态
    "accent": ACCENT_DARK,
    "accent_hover": ACCENT_HOVER_DARK,
    "accent_bg": "rgba(10, 132, 255, 0.22)",
    "accent_on": "#FFFFFF",
    "success": SUCCESS_DARK,
    "warning": WARNING_DARK,
    "error": ERROR_DARK,

    # 日志
    "log_bg": "rgba(0, 0, 0, 0.3)",
    "log_text": "#F5F5F7",

    # 阴影（深色漫射，非纯黑）
    "shadow_card": {"offset_y": 1, "blur": 8, "color": "rgba(0, 0, 0, 0.4)"},
    "shadow_card_elevated": {"offset_y": 10, "blur": 40, "color": "rgba(0, 0, 0, 0.55)"},
    "inset_highlight": "rgba(255, 255, 255, 0.08)",
}

MODE_TOKENS = {"light": _LIGHT, "dark": _DARK}


def tokens(page: ft.Page) -> dict:
    """根据 page 当前主题模式返回语义令牌 dict。

    page.theme_mode 为 SYSTEM 时，按平台实际亮度解析。
    """
    mode = page.theme_mode
    if mode == ft.ThemeMode.SYSTEM:
        # Flet 提供 platform_brightness 区分系统实际外观
        actual = getattr(page, "platform_brightness", "light")
        key = "dark" if actual == ft.Brightness.DARK else "light"
    elif mode == ft.ThemeMode.DARK:
        key = "dark"
    else:
        key = "light"
    return MODE_TOKENS[key]


def is_dark(page: ft.Page) -> bool:
    """当前是否处于深色（解析系统模式后）。"""
    return tokens(page) is _DARK


# ============================================================
# 兼容别名（指向浅色令牌，仅供极少数未迁移代码引用；
# 新代码一律用 tokens(page)[...]）
# ============================================================

PRIMARY = ACCENT_LIGHT
PRIMARY_LIGHT = ACCENT_LIGHT
PRIMARY_DARK = ACCENT_DARK
TEXT_PRIMARY = _LIGHT["text_primary"]
TEXT_LABEL = _LIGHT["text_primary"]
TEXT_DESC = _LIGHT["text_secondary"]
TEXT_HINT = _LIGHT["text_hint"]
TEXT_ON_PRIMARY = _LIGHT["text_on_accent"]
GLASS_BG_LIGHT = _LIGHT["glass_bg"]
GLASS_BG_MID = _LIGHT["glass_bg"]
GLASS_BG_DEEP = _LIGHT["glass_bg_elevated"]
GLASS_BORDER = _LIGHT["border"]
GLASS_BORDER_FOCUS = _LIGHT["border_focus"]
ACCENT = ACCENT_LIGHT
SUCCESS = SUCCESS_LIGHT
WARNING = WARNING_LIGHT
ERROR = ERROR_LIGHT
INPUT_BG = _LIGHT["input_bg"]
INPUT_BORDER = _LIGHT["input_border"]
INPUT_BORDER_FOCUS = _LIGHT["input_border_focus"]
INPUT_TEXT = _LIGHT["input_text"]
INPUT_HINT = _LIGHT["text_hint"]
DIVIDER_COLOR = _LIGHT["divider"]
LOG_BG = _LIGHT["log_bg"]
LOG_TEXT = _LIGHT["log_text"]
RADIUS = RADIUS_CARD
RADIUS_SM = RADIUS_GROUP
BTN_RADIUS = RADIUS_BTN  # 兼容别名
SHADOW_CARD = _LIGHT["shadow_card"]
SHADOW_CARD_DEEP = _LIGHT["shadow_card_elevated"]
BG_PAGE = _LIGHT["canvas"]
BG_GRADIENT_START = _LIGHT["canvas"]
BG_GRADIENT_END = _LIGHT["canvas_gradient_end"]
# 字号兼容
FONT_TITLE_COMPAT = FONT_DISPLAY
