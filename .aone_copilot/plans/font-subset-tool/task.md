### font-subset-tool ###
# FTL 字体子集压缩工具 - 任务清单

## MVP 阶段

- [x] 创建项目结构（目录、__init__.py、requirements.txt、README.md）
- [x] 实现 ui/theme.py - 主题常量定义
- [x] 实现 ui/glass_panel.py - GlassPanel 可复用毛玻璃组件
- [x] 实现 utils/charset_presets.py - 预设字符集定义
- [x] 实现 font/subsetter.py - fontTools subset 核心封装
- [x] 实现 font/converter.py - 格式转换与保存逻辑
- [x] 实现 utils/file_utils.py - 路径管理与输出目录处理
- [x] 实现 utils/async_worker.py - 线程池异步任务封装
- [x] 实现 ui/file_picker.py - 文件选择区组件
- [x] 实现 ui/charset_input.py - 字符集输入区组件（含预设、txt导入）
- [x] 实现 ui/format_options.py - 输出格式与路径选项组件
- [x] 实现 ui/advanced_options.py - 高级处理选项组件
- [x] 实现 ui/progress_log.py - 进度条与日志区组件
- [x] 实现 ui/main_view.py - 主界面布局整合
- [x] 实现 main.py - 应用入口
- [x] 集成测试：安装依赖并运行，验证完整流程

## 增强阶段

- [ ] 多文件批处理逻辑完善（并行处理、独立进度）
- [ ] zip 打包输出功能
- [ ] 毛玻璃效果细化（背景图叠层、动态模糊）
- [ ] 错误处理完善（空输入、不支持格式、目录不可写等）
- [ ] PyInstaller 打包配置


updateAtTime: 2026/5/13 14:53:30

planId: 3feaadf8-a0a4-4ae1-9308-938ffec90c9c