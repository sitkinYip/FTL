# FTL - Font Tool Lite (Tauri 版)

字体子集压缩工具。从 Flet 版本迁移到 **Tauri v2 + Vue 3 + naive-ui** 架构。

## 为什么迁移

Flet 桌面端不支持**原生文件拖拽**(从 Finder 拖文件进窗口),这是字体工具的核心交互。
Tauri 的 `onDragDropEvent` 是一等公民,能拿到完整文件路径。详见 [调研结论](../docs/migration-research.md)。

## 架构

```
┌─────────────────────────────────────────────────────┐
│  Tauri Window (Vue 3 + naive-ui)                    │
│  ┌───────────────────────────────────────────────┐  │
│  │  前端 UI(文件拖拽 / 字符集 / 格式 / 进度)      │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │ invoke() / event               │
│  ┌──────────────────▼────────────────────────────┐  │
│  │  Rust 后端(src-tauri)                          │  │
│  │  sidecar 桥接:spawn / stdin / stdout / event  │  │
│  └──────────────────┬────────────────────────────┘  │
└─────────────────────┼───────────────────────────────┘
                      │ NDJSON over stdio
┌─────────────────────▼───────────────────────────────┐
│  Python Sidecar(sidecar/ftl_worker.py)             │
│  fontTools 子集化 + brotli/zlib 压缩                 │
│  (复用 Flet 版 font/ + utils/,零业务改动)            │
└─────────────────────────────────────────────────────┘
```

**为什么用 Python sidecar**:fontTools 的 subsetter(GPOS/GSUB 特性过滤、字形闭包、CFF desubroutinize)无等价的纯 Rust/JS 实现,重写不现实。现有后端 ~400 行零 UI 耦合,直接复用。

## 开发

### 前置要求
- Node.js 18+ / pnpm
- Rust 1.75+ (cargo)
- Python 3.10+

### 安装
```bash
# 前端依赖
pnpm install

# Python sidecar 依赖(单独 venv)
python3 -m venv .venv-sidecar
.venv-sidecar/bin/pip install -r sidecar/requirements.txt
```

### 运行
```bash
# 启动整个应用(Tauri + Vue dev server + Python sidecar)
npx tauri dev

# 或单独测试 sidecar(命令行手动喂数据)
echo '{"type":"process","id":"t1","files":["/path/to/font.ttf"],"characters":"ABC","formats":["woff2"],"options":{"keep_layout":true,"keep_names":true,"notdef_glyph":true,"glyph_names":false,"keep_hinting":false},"output_mode":"subdir","custom_dir":null}' | .venv-sidecar/bin/python sidecar/ftl_worker.py
```

## 通信协议

NDJSON over stdio(每行一个 JSON):

| 方向 | 类型 | 说明 |
|---|---|---|
| 前端→sidecar | `process` | 开始处理(files/characters/formats/options) |
| 前端→sidecar | `cancel` | 取消批次 |
| sidecar→前端 | `ready` | sidecar 启动就绪 |
| sidecar→前端 | `progress` | 进度更新(completed/total/current_file) |
| sidecar→前端 | `file_done` | 单文件完成(outputs 或 error) |
| sidecar→前端 | `complete` | 整批完成(ok/fail/elapsed) |
| sidecar→前端 | `error` | 致命错误 |

类型定义见 [`src/types/messages.ts`](src/types/messages.ts)。

## 目录结构
```
ftl-tauri/
├── src/              # Vue 前端
├── src-tauri/        # Tauri 壳(Rust sidecar 桥接)
├── sidecar/          # Python 后端(fontTools 子集化)
│   ├── ftl_worker.py # NDJSON stdio 主循环
│   ├── font/         # 复用:subsetter / converter
│   └── utils/        # 复用:file_utils / charset_presets
└── package.json
```

## 进度

- [x] 阶段 1:脚手架 + sidecar 协议(验证通过)
- [x] 阶段 2:Rust sidecar 桥接(验证通过)
- [ ] 阶段 3:前端 UI 组件
- [ ] 阶段 4:跨平台剪贴板 + 三端测试
- [ ] 阶段 5:PyInstaller 打包 + 发布
