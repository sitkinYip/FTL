<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { open } from "@tauri-apps/plugin-dialog";
import { NText } from "naive-ui";
import { useFontStore } from "../stores/fontStore";
import { formatFileSize } from "../data/charsetPresets";
import { listenFileDrop } from "../composables/useFileDrop";
import { readClipboardFiles } from "../composables/useClipboard";
import type { UnlistenFn } from "@tauri-apps/api/event";

const store = useFontStore();
const isDragHover = ref(false);
let unlistenDrop: UnlistenFn | null = null;

onMounted(async () => {
  // 监听原生文件拖放
  unlistenDrop = await listenFileDrop((paths) => {
    store.addFiles(paths);
  });

  // 监听拖拽悬停状态(由 useFileDrop 派发自定义事件)
  window.addEventListener("ftl:drag-hover", handleDragHover);
});

onUnmounted(() => {
  unlistenDrop?.();
  window.removeEventListener("ftl:drag-hover", handleDragHover);
});

function handleDragHover(e: Event) {
  isDragHover.value = (e as CustomEvent).detail;
}

/** 点击打开文件选择对话框 */
async function pickFiles() {
  const selected = await open({
    multiple: true,
    filters: [{ name: "字体文件", extensions: ["ttf", "otf", "woff", "woff2"] }],
  });
  if (selected) {
    const paths = Array.isArray(selected) ? selected : [selected];
    store.addFiles(paths);
  }
}

/** 从剪贴板导入(⌘V/Ctrl+V 或按钮触发) */
async function pasteFromClipboard() {
  const paths = await readClipboardFiles();
  if (paths.length > 0) {
    store.addFiles(paths);
  }
}

// 暴露给父组件(用于全局 ⌘V 监听)
defineExpose({ pasteFromClipboard });
</script>

<template>
  <div class="file-zone">
    <!-- 投放区 -->
    <div
      class="drop-zone"
      :class="{ hover: isDragHover }"
      @click="pickFiles"
    >
      <div class="drop-content">
        <svg class="upload-icon" viewBox="0 0 24 24" width="40" height="40">
          <path
            fill="currentColor"
            d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z"
          />
        </svg>
        <div class="drop-title">点击选择字体文件,或拖拽到此处</div>
        <div class="drop-hint">支持 .ttf .otf .woff .woff2</div>
        <NText class="paste-hint" depth="3">
          也可在 Finder 复制后按 ⌘V / Ctrl+V 粘贴
        </NText>
      </div>
    </div>

    <!-- 文件列表 -->
    <div v-if="store.files.length > 0" class="file-list">
      <div class="file-list-header">
        <span class="file-count">已选 {{ store.files.length }} 个文件</span>
        <button class="clear-btn" @click="store.clearFiles">清空</button>
      </div>
      <div class="file-items">
        <div v-for="file in store.files" :key="file.path" class="file-item">
          <svg class="file-icon" viewBox="0 0 24 24" width="16" height="16">
            <path
              fill="currentColor"
              d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8zm-2 8V3.5L18.5 9H12z"
            />
          </svg>
          <span class="file-name" :title="file.path">{{ file.name }}</span>
          <span v-if="file.size" class="file-size mono">{{ formatFileSize(file.size) }}</span>
          <button class="remove-btn" @click="store.removeFile(file.path)">×</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.file-zone {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.drop-zone {
  border: 2px dashed var(--ftl-border);
  border-radius: 16px;
  background: var(--ftl-surface);
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.drop-zone:hover {
  border-color: var(--ftl-accent);
  background: rgba(0, 113, 227, 0.04);
}

.drop-zone.hover {
  border-color: var(--ftl-accent);
  background: rgba(0, 113, 227, 0.08);
  transform: scale(1.01);
}

.drop-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.upload-icon {
  color: var(--ftl-accent);
  opacity: 0.8;
}

.drop-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--ftl-text-primary);
}

.drop-hint {
  font-size: 13px;
  color: var(--ftl-text-secondary);
}

.paste-hint {
  font-size: 12px;
  margin-top: 2px;
}

/* 文件列表 */
.file-list {
  border: 1px solid var(--ftl-border);
  border-radius: 12px;
  overflow: hidden;
}

.file-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--ftl-surface);
  border-bottom: 1px solid var(--ftl-border);
}

.file-count {
  font-size: 13px;
  color: var(--ftl-text-secondary);
  font-weight: 500;
}

.clear-btn {
  font-size: 12px;
  color: var(--ftl-text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 8px;
  border-radius: 4px;
}

.clear-btn:hover {
  color: var(--ftl-accent);
  background: rgba(0, 113, 227, 0.06);
}

.file-items {
  max-height: 120px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-bottom: 1px solid var(--ftl-border);
}

.file-item:last-child {
  border-bottom: none;
}

.file-icon {
  color: var(--ftl-accent);
  flex-shrink: 0;
}

.file-name {
  flex: 1;
  font-size: 13px;
  color: var(--ftl-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 11px;
  color: var(--ftl-text-secondary);
  flex-shrink: 0;
}

.remove-btn {
  width: 20px;
  height: 20px;
  border: none;
  background: none;
  color: var(--ftl-text-tertiary);
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  border-radius: 4px;
  flex-shrink: 0;
}

.remove-btn:hover {
  color: #ff453a;
  background: rgba(255, 69, 58, 0.1);
}
</style>
