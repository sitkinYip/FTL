<script setup lang="ts">
import { computed } from "vue";
import { NModal, NCard, NProgress, NButton, NText, NScrollbar } from "naive-ui";
import { useFontStore } from "../stores/fontStore";
import { formatFileSize } from "../data/charsetPresets";

const store = useFontStore();

const show = computed(() => store.isProcessing || store.results.length > 0);

const statusText = computed(() => {
  if (store.processingError) return "处理出错";
  if (store.isProcessing) return "正在处理";
  if (store.progress >= 1) return "处理完成";
  return "就绪";
});

const statusType = computed(() => {
  if (store.processingError) return "error";
  if (store.progress >= 1) return "success";
  return "info";
});

const okCount = computed(() => store.results.filter((r) => r.success).length);
const failCount = computed(() => store.results.filter((r) => !r.success).length);

function close() {
  store.resetProcessing();
}
</script>

<template>
  <NModal :show="show">
    <NCard
      style="width: 480px"
      :bordered="false"
      size="huge"
      role="dialog"
      :closable="!store.isProcessing"
      @close="close"
    >
      <!-- 标题行 -->
      <template #header>
        <div class="dialog-title">
          <span>{{ statusText }}</span>
          <NText v-if="store.isProcessing" depth="3" class="subtitle">
            共 {{ store.files.length }} 个文件
          </NText>
          <NText v-else-if="store.progress >= 1" depth="3" class="subtitle">
            成功 {{ okCount }} · 失败 {{ failCount }}
          </NText>
        </div>
      </template>

      <!-- 进度 -->
      <div class="progress-section">
        <NProgress
          :percentage="Math.round(store.progress * 100)"
          :type="'line'"
          :status="statusType"
          :show-indicator="true"
          :height="8"
          :border-radius="4"
        />
        <div v-if="store.currentFile && store.isProcessing" class="current-file mono">
          {{ store.currentFile }}
        </div>
      </div>

      <!-- 错误 -->
      <div v-if="store.processingError" class="error-msg">
        {{ store.processingError }}
      </div>

      <!-- 结果列表 -->
      <div v-if="store.results.length > 0" class="results">
        <NScrollbar style="max-height: 160px">
          <div
            v-for="(result, idx) in store.results"
            :key="idx"
            class="result-row"
            :class="{ fail: !result.success }"
          >
            <span class="result-icon">{{ result.success ? "✓" : "✗" }}</span>
            <span class="result-file">{{ result.file }}</span>
            <template v-if="result.success && result.outputs">
              <span
                v-for="out in result.outputs"
                :key="out.format"
                class="result-format mono"
              >
                {{ out.format }} · {{ formatFileSize(out.size) }}
              </span>
            </template>
            <span v-else-if="result.error" class="result-error">
              {{ result.error }}
            </span>
          </div>
        </NScrollbar>
      </div>

      <!-- 关闭按钮 -->
      <template v-if="!store.isProcessing" #footer>
        <div class="dialog-footer">
          <NButton type="primary" @click="close">完成</NButton>
        </div>
      </template>
    </NCard>
  </NModal>
</template>

<style scoped>
.dialog-title {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.subtitle {
  font-size: 13px;
  font-weight: 400;
}

.progress-section {
  margin-bottom: 16px;
}

.current-file {
  font-size: 12px;
  color: var(--ftl-text-secondary);
  margin-top: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.error-msg {
  color: #ff453a;
  font-size: 13px;
  padding: 8px 12px;
  background: rgba(255, 69, 58, 0.08);
  border-radius: 8px;
  margin-bottom: 12px;
}

.results {
  border: 1px solid var(--ftl-border);
  border-radius: 8px;
  padding: 4px 0;
}

.result-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  font-size: 12px;
  border-bottom: 1px solid var(--ftl-border);
}

.result-row:last-child {
  border-bottom: none;
}

.result-icon {
  flex-shrink: 0;
  width: 16px;
  text-align: center;
  font-weight: 700;
}

.result-row:not(.fail) .result-icon {
  color: #30d158;
}

.result-row.fail .result-icon {
  color: #ff453a;
}

.result-file {
  flex: 1;
  color: var(--ftl-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-format {
  color: var(--ftl-text-secondary);
  font-size: 11px;
  flex-shrink: 0;
  padding: 1px 6px;
  background: var(--ftl-border);
  border-radius: 3px;
}

.result-error {
  color: #ff453a;
  font-size: 11px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>
