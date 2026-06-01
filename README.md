# FTL - Font Tool Lite

基于 Flet + fontTools 的桌面端字体子集压缩工具。

## 功能特性

- 字体子集化：仅保留指定字符，大幅缩小字体文件体积
- 多格式输出：支持 woff2、woff、ttf 格式
- 多文件批处理：一次选择多个字体文件并行处理
- 字符集预设：数字+小数点、英文+标点、常用中文 3500 等
- 字符集导入：支持从 txt 文件导入字符集

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

## 技术栈

- **GUI**: Flet (Python)
- **字体处理**: fontTools (subsetting)
- **压缩**: brotli (woff2)
- **平台**: macOS (主要)

## 项目结构

```
FTL/
├── main.py              # 入口文件
├── ui/                  # UI 组件层
├── font/                # 字体处理层
├── utils/               # 工具层
├── config/              # 配置
└── assets/              # 静态资源
```
