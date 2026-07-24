<script setup lang="ts">
import { ref } from "vue";
import { NCheckbox, NRadioGroup, NRadio, NButton, NText, NSpace } from "naive-ui";
import { useFontStore } from "../stores/fontStore";
import { open } from "@tauri-apps/plugin-dialog";
import AdvancedDialog from "./AdvancedDialog.vue";

const store = useFontStore();
const showAdvanced = ref(false);

async function pickCustomDir() {
  const selected = await open({ directory: true });
  if (selected && typeof selected === "string") {
    store.customDir = selected;
  }
}
</script>

<template>
  <div class="format-options">
    <!-- 格式 -->
    <div class="section">
      <NText depth="3" class="label">格式</NText>
      <NSpace :size="16">
        <NCheckbox v-model:checked="store.formats.woff2">WOFF2</NCheckbox>
        <NCheckbox v-model:checked="store.formats.woff">WOFF</NCheckbox>
        <NCheckbox v-model:checked="store.formats.ttf">TTF</NCheckbox>
      </NSpace>
    </div>

    <!-- 输出位置 -->
    <div class="section">
      <NText depth="3" class="label">输出位置</NText>
      <NRadioGroup v-model:value="store.outputMode" class="radio-group">
        <NRadio value="subdir">源文件同目录子文件夹</NRadio>
        <NRadio value="custom">自定义目录</NRadio>
      </NRadioGroup>
      <div v-if="store.outputMode === 'custom'" class="custom-dir">
        <NButton size="small" secondary @click="pickCustomDir">选择目录</NButton>
        <NText v-if="store.customDir" depth="2" class="dir-path mono">
          {{ store.customDir }}
        </NText>
      </div>
    </div>

    <!-- 高级选项按钮 -->
    <NButton size="small" quaternary @click="showAdvanced = true">
      高级选项
    </NButton>

    <!-- 高级选项弹窗 -->
    <AdvancedDialog v-model:show="showAdvanced" />
  </div>
</template>

<style scoped>
.format-options {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  font-size: 12px;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.custom-dir {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.dir-path {
  font-size: 11px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
