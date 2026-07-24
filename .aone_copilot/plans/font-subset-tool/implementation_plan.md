### font-subset-tool ###
基于 Flet + fontTools 开发一个 macOS 桌面端字体子集压缩工具，支持多文件批处理、多格式输出（woff2/woff/ttf）、字符集输入/预设/文件导入，UI 采用 iOS 18 毛玻璃风格。

# 字体子集压缩工具（FTL - Font Tool Lite）

基于 Flet（Python GUI）+ fontTools 开发一个 macOS 桌面端字体子集压缩与格式输出工具。UI 采用 iOS 18 毛玻璃风格（半透明面板、圆角、柔和阴影、玻璃层次），支持多文件批处理、多格式输出。

## Proposed Changes

### 项目结构

```
FTL/
├── main.py                  # 入口文件
├── requirements.txt         # 依赖清单
├── README.md               # 项目说明
├── assets/
│   └── bg.jpg              # 毛玻璃背景图（可选）
├── ui/
│   ├── __init__.py
│   ├── glass_panel.py      # GlassPanel 可复用组件
│   ├── theme.py            # 主题色/样式常量
│   ├── main_view.py        # 主界面布局
│   ├── file_picker.py      # 文件选择区组件
│   ├── charset_input.py    # 字符集输入区组件
│   ├── format_options.py   # 输出格式选项组件
│   ├── advanced_options.py # 高级处理选项组件
│   └── progress_log.py     # 进度条与日志区组件
├── font/
│   ├── __init__.py
│   ├── subsetter.py        # fontTools subset 封装
│   └── converter.py        # 格式转换逻辑（ttf→woff/woff2）
├── utils/
│   ├── __init__.py
│   ├── charset_presets.py  # 预设字符集定义
│   ├── file_utils.py       # 路径管理、zip 打包
│   └── async_worker.py     # 线程池/异步任务封装
└── config/
    └── presets.json        # 预设字符集配置文件（可选）
```

---

### 核心依赖（requirements.txt）

```
flet>=0.25.0
fonttools[woff]>=4.47.0
brotli>=1.1.0
```

---

### UI 层 - 毛玻璃组件

#### [NEW] [glass_panel.py](file:///Users/sitkin/my_code/FTL/ui/glass_panel.py)

可复用的 GlassPanel 组件，模拟 iOS 18 毛玻璃效果：
- 使用 `ft.Container` 叠层实现：底层背景色 + 半透明白色覆盖层 + 边框高光
- `border_radius=16`，`shadow` 柔和投影
- `bgcolor` 使用 `ft.Colors.with_opacity(0.6, ft.Colors.WHITE)` 模拟磨砂
- 暴露 `content`、`padding`、`width`、`height` 等参数

#### [NEW] [theme.py](file:///Users/sitkin/my_code/FTL/ui/theme.py)

定义全局主题常量：
- 主色调：蓝紫渐变
- 面板背景：半透明白 `rgba(255,255,255,0.55)`
- 边框：`rgba(255,255,255,0.3)` 1px
- 圆角：16px
- 阴影：`offset=(0,8), blur=24, color=rgba(0,0,0,0.08)`
- 字体大小、间距等规范

---

### UI 层 - 主界面

#### [NEW] [main_view.py](file:///Users/sitkin/my_code/FTL/ui/main_view.py)

主界面布局，包含以下区域（纵向排列）：
1. **标题栏**：应用名称 + 简短说明
2. **文件选择区**：选择单个/多个字体文件（.ttf/.otf/.woff）
3. **字符集输入区**：TextField 多行输入 + 预设按钮 + 从 txt 导入按钮
4. **输出格式区**：Checkbox 勾选 woff2/woff/ttf（默认全选）
5. **输出路径区**：默认同目录子文件夹，可切换为自定义目录
6. **高级选项区**：保留表选项、remapping 等
7. **操作按钮**：「开始处理」大按钮
8. **进度/日志区**：ProgressBar + 滚动日志

#### [NEW] [file_picker.py](file:///Users/sitkin/my_code/FTL/ui/file_picker.py)

- 使用 `ft.FilePicker` 支持多文件选择
- 显示已选文件列表（可删除单个）
- 支持 .ttf/.otf/.woff/.woff2 格式过滤

#### [NEW] [charset_input.py](file:///Users/sitkin/my_code/FTL/ui/charset_input.py)

- 多行 TextField 手动输入/粘贴字符
- 预设 Dropdown/Chips：「数字+小数点」「英文+标点」「常用中文3500」
- 「从文件导入」按钮：读取 .txt 文件内容作为字符集
- 实时显示"当前字符数"统计

#### [NEW] [format_options.py](file:///Users/sitkin/my_code/FTL/ui/format_options.py)

- 三个 Checkbox：woff2 / woff / ttf，默认全选
- 输出路径模式切换：同目录子文件夹 / 自定义目录

#### [NEW] [advanced_options.py](file:///Users/sitkin/my_code/FTL/ui/advanced_options.py)

- 保留布局表开关（name/OS2/cmap 等）
- glyph-names 保留开关
- notdef-glyph 保留开关

#### [NEW] [progress_log.py](file:///Users/sitkin/my_code/FTL/ui/progress_log.py)

- ProgressBar 显示总体进度
- ListView 滚动日志：时间戳 + 消息 + 状态颜色
- 耗时统计

---

### 字体处理层

#### [NEW] [subsetter.py](file:///Users/sitkin/my_code/FTL/font/subsetter.py)

核心子集化逻辑封装：
```python
from fontTools.subset import Subsetter, Options
from fontTools.ttLib import TTFont

def subset_font(input_path, characters, options_dict) -> TTFont:
    """对字体进行子集化，返回处理后的 TTFont 对象"""
    font = TTFont(input_path)
    options = Options()
    # 配置选项
    options.layout_features = ['*'] if options_dict.get('keep_layout') else []
    options.name_IDs = ['*'] if options_dict.get('keep_names') else [0,1,2]
    options.notdef_glyph = options_dict.get('notdef_glyph', True)
    options.glyph_names = options_dict.get('glyph_names', False)
    
    subsetter = Subsetter(options=options)
    subsetter.populate(text=characters)
    subsetter.subset(font)
    return font
```

#### [NEW] [converter.py](file:///Users/sitkin/my_code/FTL/font/converter.py)

格式转换与保存：
```python
def save_font(font: TTFont, output_path: Path, fmt: str):
    """将 TTFont 保存为指定格式"""
    if fmt == 'woff2':
        font.flavor = 'woff2'
    elif fmt == 'woff':
        font.flavor = 'woff'
    else:  # ttf
        font.flavor = None
    font.save(str(output_path))
```

---

### 工具层

#### [NEW] [charset_presets.py](file:///Users/sitkin/my_code/FTL/utils/charset_presets.py)

预设字符集定义：
- `DIGITS`: `0123456789.,-+`
- `ASCII_PRINTABLE`: 所有可打印 ASCII
- `ENGLISH_PUNCT`: 英文字母 + 常用标点
- `COMMON_CJK_3500`: 常用汉字 3500 字

#### [NEW] [file_utils.py](file:///Users/sitkin/my_code/FTL/utils/file_utils.py)

- `ensure_output_dir()`: 创建输出目录
- `zip_results()`: 将多文件结果打包为 zip
- `get_output_path()`: 根据模式计算输出路径

#### [NEW] [async_worker.py](file:///Users/sitkin/my_code/FTL/utils/async_worker.py)

- 使用 `concurrent.futures.ThreadPoolExecutor` 封装
- 提供 `run_in_thread(fn, callback)` 方法
- 任务完成后通过回调更新 UI 进度

---

### 入口文件

#### [NEW] [main.py](file:///Users/sitkin/my_code/FTL/main.py)

```python
import flet as ft
from ui.main_view import MainView

def main(page: ft.Page):
    page.title = "FTL - Font Tool Lite"
    page.window.width = 900
    page.window.height = 720
    page.bgcolor = ft.Colors.TRANSPARENT
    page.window.bgcolor = ft.Colors.TRANSPARENT
    page.padding = 0
    
    main_view = MainView(page)
    page.add(main_view)

ft.app(target=main)
```

---

## Verification Plan

### Automated Tests

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py

# 验证子集化核心逻辑（可单独测试）
python -c "from font.subsetter import subset_font; print('subsetter OK')"
```

### Manual Verification

1. 启动应用，确认 UI 正常渲染毛玻璃效果
2. 选择一个 .ttf 字体文件
3. 输入字符 `0123456789.`
4. 勾选 woff2 + ttf 输出
5. 点击「开始处理」，确认输出目录生成对应文件
6. 验证输出文件大小明显小于原文件
7. 测试预设按钮、从 txt 导入功能
8. 测试多文件批处理 + zip 打包


updateAtTime: 2026/5/13 14:53:30

planId: 3feaadf8-a0a4-4ae1-9308-938ffec90c9c