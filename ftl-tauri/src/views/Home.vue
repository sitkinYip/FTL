<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { NButton, NText, useMessage } from "naive-ui";
import { useFontStore } from "../stores/fontStore";
import { onSidecarEvent, checkSidecarReady } from "../composables/useSidecar";
import type { UnlistenFn } from "@tauri-apps/api/event";
import FileDropZone from "../components/FileDropZone.vue";
import CharsetInput from "../components/CharsetInput.vue";
import FormatOptions from "../components/FormatOptions.vue";
import ProcessingDialog from "../components/ProcessingDialog.vue";

const store = useFontStore();
const message = useMessage();
const fileDropZone = ref();
let unlistenSidecar: UnlistenFn | null = null;

onMounted(async () => {
  // 监听 sidecar 事件,转发到 store
  unlistenSidecar = await onSidecarEvent((event) => {
    store.handleSidecarEvent(event);
  });

  // 主动查询 sidecar 状态(解决竞态:ready 可能在 listener 注册前已发出)
  const ready = await checkSidecarReady();
  if (ready) {
    store.sidecarReady = true;
  }

  // 全局键盘:⌘V / Ctrl+V 粘贴文件
  window.addEventListener("keydown", handlePaste);
});

onUnmounted(() => {
  unlistenSidecar?.();
  window.removeEventListener("keydown", handlePaste);
});

function handlePaste(e: KeyboardEvent) {
  const isPaste = (e.key === "v" || e.key === "V") && (e.metaKey || e.ctrlKey);
  if (isPaste && !store.isProcessing) {
    e.preventDefault();
    fileDropZone.value?.pasteFromClipboard();
  }
}

function handleStart() {
  if (!store.sidecarReady) {
    message.warning("后端尚未就绪,请稍候");
    return;
  }
  if (store.files.length === 0) {
    message.warning("请先选择至少一个字体文件");
    return;
  }
  if (store.charset.trim().length === 0) {
    message.warning("请输入需要保留的字符集");
    return;
  }
  if (store.selectedFormats.length === 0) {
    message.warning("请至少选择一种输出格式");
    return;
  }
  store.startProcessing();
}
</script>

<template>
  <div class="home">
    <div class="container">
      <!-- 品牌行 -->
      <header class="brand-row">
        <div class="brand">
          <h1 class="brand-title">FTL</h1>
          <span class="brand-name">Font Tool Lite</span>
        </div>
        <NText depth="3" class="brand-desc">字体子集压缩工具</NText>
      </header>

      <!-- 上传区(铺满) -->
      <section class="upload-section">
        <FileDropZone ref="fileDropZone" />
      </section>

      <!-- 双列:字符集 | 输出格式 -->
      <section class="config-row">
        <div class="config-col charset-col">
          <h2 class="section-title">字符集</h2>
          <CharsetInput />
        </div>
        <div class="config-col format-col">
          <h2 class="section-title">输出格式</h2>
          <FormatOptions />
        </div>
      </section>
    </div>

    <!-- 底部固定开始按钮 -->
    <footer class="start-bar">
      <NButton
        type="primary"
        size="large"
        round
        :disabled="!store.canStart"
        :loading="store.isProcessing"
        class="start-btn"
        @click="handleStart"
      >
        {{ store.isProcessing ? "处理中..." : "开始处理" }}
      </NButton>
    </footer>

    <!-- 处理进度弹窗 -->
    <ProcessingDialog />
  </div>
</template>

<style scoped>
.home {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px;
  overflow-y: auto;
}

/* 品牌行 */
.brand-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.brand {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--ftl-text-primary);
  margin: 0;
}

.brand-name {
  font-size: 20px;
  font-weight: 300;
  color: var(--ftl-text-secondary);
}

.brand-desc {
  font-size: 13px;
}

/* 配置双列 */
.config-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

.config-col {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--ftl-text-primary);
  margin: 0;
}

/* 底部按钮栏 */
.start-bar {
  display: flex;
  justify-content: center;
  padding: 12px 24px 16px;
  border-top: 1px solid var(--ftl-border);
  background: var(--ftl-canvas);
}

.start-btn {
  min-width: 200px;
}
</style>
