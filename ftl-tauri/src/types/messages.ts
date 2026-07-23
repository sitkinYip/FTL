/**
 * FTL sidecar 通信协议类型定义
 *
 * 协议:NDJSON over stdio
 *   前端 → sidecar (stdin):一行一个 JSON 命令
 *   sidecar → 前端 (stdout):一行一个 JSON 事件
 *
 * 所有消息带 `id`(批次号),支持并发批次与取消。
 */

// ============================================================
// 共享类型
// ============================================================

/** 输出格式 */
export type FontFormat = "woff2" | "woff" | "ttf";

/** 高级处理选项(对应 fontTools Options 字段映射) */
export interface AdvancedOptions {
  /** 保留布局特性表 GPOS/GSUB(layout_features) */
  keep_layout: boolean;
  /** 保留完整 name 表(name_IDs) */
  keep_names: boolean;
  /** 保留 .notdef 字形(notdef_glyph / notdef_outline) */
  notdef_glyph: boolean;
  /** 保留字形名称 glyph names */
  glyph_names: boolean;
  /** 保留 hinting 信息 */
  keep_hinting: boolean;
}

/** 输出位置模式 */
export type OutputMode = "subdir" | "custom";

/** 单个格式转换结果 */
export interface FormatResult {
  format: FontFormat;
  path: string;
  size: number;
  success: boolean;
  error?: string;
}

// ============================================================
// 前端 → sidecar (stdin 命令)
// ============================================================

/** 开始处理命令 */
export interface ProcessCommand {
  type: "process";
  id: string;
  files: string[];
  characters: string;
  formats: FontFormat[];
  options: AdvancedOptions;
  output_mode: OutputMode;
  custom_dir: string | null;
}

/** 取消命令 */
export interface CancelCommand {
  type: "cancel";
  id: string;
}

export type SidecarCommand = ProcessCommand | CancelCommand;

// ============================================================
// sidecar → 前端 (stdout 事件)
// ============================================================

/** 进度更新 */
export interface ProgressEvent {
  type: "progress";
  id: string;
  completed: number;
  total: number;
  current_file: string;
  progress: number;
}

/** 单个文件处理完成 */
export interface FileDoneEvent {
  type: "file_done";
  id: string;
  file: string;
  success: boolean;
  outputs?: FormatResult[];
  error?: string;
}

/** 整批处理完成 */
export interface CompleteEvent {
  type: "complete";
  id: string;
  ok: number;
  fail: number;
  elapsed: number;
}

/** 错误(致命) */
export interface ErrorEvent {
  type: "error";
  id: string;
  message: string;
}

/** sidecar 就绪(启动后发出) */
export interface ReadyEvent {
  type: "ready";
  version: string;
}

export type SidecarEvent =
  | ProgressEvent
  | FileDoneEvent
  | CompleteEvent
  | ErrorEvent
  | ReadyEvent;

// ============================================================
// 默认值(与 Flet 版 AdvancedOptions 默认一致)
// ============================================================

export const DEFAULT_ADVANCED_OPTIONS: AdvancedOptions = {
  keep_layout: true,
  keep_names: true,
  notdef_glyph: true,
  glyph_names: false,
  keep_hinting: false,
};
