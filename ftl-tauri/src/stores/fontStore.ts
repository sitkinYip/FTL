/**
 * 全局状态(Pinia)
 *
 * 管理:文件列表 / 字符集 / 格式 / 高级选项 / 处理进度
 * 对应 Flet 版各组件分散持有的状态,这里集中。
 */

import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type {
  FontFormat,
  AdvancedOptions,
  OutputMode,
  FormatResult,
  SidecarEvent,
} from "../types/messages";
import { DEFAULT_ADVANCED_OPTIONS } from "../types/messages";
import { deduplicateChars } from "../data/charsetPresets";
import { sendCommand } from "../composables/useSidecar";

const FONT_EXTENSIONS = [".ttf", ".otf", ".woff", ".woff2"];

export interface SelectedFile {
  path: string;
  name: string;
  size: number;
}

export interface FileResult {
  file: string;
  success: boolean;
  outputs?: FormatResult[];
  error?: string;
}

export const useFontStore = defineStore("font", () => {
  // —— 文件列表 ——
  const files = ref<SelectedFile[]>([]);

  // —— 字符集 ——
  const charset = ref("");

  // —— 输出格式 ——
  const formats = ref<Record<FontFormat, boolean>>({
    woff2: true,
    woff: true,
    ttf: true,
  });

  // —— 输出位置 ——
  const outputMode = ref<OutputMode>("subdir");
  const customDir = ref<string>("");

  // —— 高级选项 ——
  const advanced = ref<AdvancedOptions>({ ...DEFAULT_ADVANCED_OPTIONS });

  // —— 处理状态 ——
  const isProcessing = ref(false);
  const progress = ref(0);
  const progressText = ref("就绪");
  const currentFile = ref("");
  const results = ref<FileResult[]>([]);
  const processingError = ref("");

  // —— sidecar 连接 ——
  const sidecarReady = ref(false);

  // ============================================================
  // 计算属性
  // ============================================================
  const selectedFormats = computed(() =>
    (Object.keys(formats.value) as FontFormat[]).filter((f) => formats.value[f])
  );

  const deduplicatedCount = computed(() => deduplicateChars(charset.value).length);

  const canStart = computed(
    () =>
      files.value.length > 0 &&
      charset.value.trim().length > 0 &&
      selectedFormats.value.length > 0 &&
      !isProcessing.value &&
      sidecarReady.value
  );

  // ============================================================
  // 文件操作
  // ============================================================
  function isFontPath(path: string): boolean {
    const lower = path.toLowerCase();
    return FONT_EXTENSIONS.some((ext) => lower.endsWith(ext));
  }

  function addFiles(paths: string[]) {
    for (const path of paths) {
      if (isFontPath(path) && !files.value.some((f) => f.path === path)) {
        const name = path.split(/[/\\]/).pop() || path;
        files.value.push({ path, name, size: 0 });
      }
    }
  }

  function removeFile(path: string) {
    files.value = files.value.filter((f) => f.path !== path);
  }

  function clearFiles() {
    files.value = [];
  }

  // ============================================================
  // 字符集操作
  // ============================================================
  function appendCharset(chars: string) {
    charset.value += chars;
  }

  function deduplicateCharset() {
    charset.value = deduplicateChars(charset.value);
  }

  function clearCharset() {
    charset.value = "";
  }

  // ============================================================
  // 处理流程
  // ============================================================
  async function startProcessing() {
    if (!canStart.value) return;

    isProcessing.value = true;
    progress.value = 0;
    results.value = [];
    processingError.value = "";
    progressText.value = "正在处理...";
    currentFile.value = "";

    const batchId = `batch-${Date.now()}`;
    await sendCommand({
      type: "process",
      id: batchId,
      files: files.value.map((f) => f.path),
      characters: charset.value,
      formats: selectedFormats.value,
      options: { ...advanced.value },
      output_mode: outputMode.value,
      custom_dir: outputMode.value === "custom" ? customDir.value : null,
    });
  }

  async function cancelProcessing() {
    // 发取消命令(当前批次 ID 需要记录,这里简化)
    // TODO: 记录当前 batchId 以便精确取消
  }

  /** 处理 sidecar 事件(由组件调用) */
  function handleSidecarEvent(event: SidecarEvent) {
    switch (event.type) {
      case "ready":
        sidecarReady.value = true;
        break;
      case "progress":
        progress.value = event.progress;
        currentFile.value = event.current_file;
        progressText.value = `${event.completed}/${event.total}`;
        break;
      case "file_done":
        results.value.push({
          file: event.file,
          success: event.success,
          outputs: event.outputs,
          error: event.error,
        });
        break;
      case "complete":
        progress.value = 1;
        progressText.value = `完成:成功 ${event.ok},失败 ${event.fail}`;
        isProcessing.value = false;
        break;
      case "error":
        processingError.value = event.message;
        isProcessing.value = false;
        break;
    }
  }

  function resetProcessing() {
    progress.value = 0;
    progressText.value = "就绪";
    currentFile.value = "";
    results.value = [];
    processingError.value = "";
  }

  return {
    // 状态
    files,
    charset,
    formats,
    outputMode,
    customDir,
    advanced,
    isProcessing,
    progress,
    progressText,
    currentFile,
    results,
    processingError,
    sidecarReady,
    // 计算
    selectedFormats,
    deduplicatedCount,
    canStart,
    // 文件
    addFiles,
    removeFile,
    clearFiles,
    // 字符集
    appendCharset,
    deduplicateCharset,
    clearCharset,
    // 处理
    startProcessing,
    cancelProcessing,
    handleSidecarEvent,
    resetProcessing,
  };
});
