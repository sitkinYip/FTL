<script setup lang="ts">
import { computed } from "vue";
import { NInput, NButton, NText, NSpace } from "naive-ui";
import { useFontStore } from "../stores/fontStore";
import { PRESETS, deduplicateChars } from "../data/charsetPresets";
import { open } from "@tauri-apps/plugin-dialog";
import { readTextFile } from "@tauri-apps/plugin-fs";

const store = useFontStore();

const charCount = computed(() => {
  const raw = store.charset.length;
  const deduped = deduplicateChars(store.charset).length;
  return `${raw} 个字符(去重后 ${deduped} 个)`;
});

function applyPreset(chars: string) {
  store.appendCharset(chars);
}

async function importFromTxt() {
  const selected = await open({
    multiple: false,
    filters: [{ name: "文本文件", extensions: ["txt"] }],
  });
  if (selected && typeof selected === "string") {
    try {
      const content = await readTextFile(selected);
      store.appendCharset(content);
    } catch (e) {
      console.error("读取 TXT 失败:", e);
    }
  }
}
</script>

<template>
  <div class="charset-input">
    <!-- 计数 -->
    <div class="charset-header">
      <NText depth="3" class="count mono">{{ charCount }}</NText>
    </div>

    <!-- 文本域 -->
    <NInput
      v-model:value="store.charset"
      type="textarea"
      placeholder="输入或粘贴需要保留的字符,例如:0123456789."
      :autosize="{ minRows: 3, maxRows: 6 }"
      class="charset-field"
    />

    <!-- 预设 -->
    <div class="preset-section">
      <NText depth="3" class="preset-label">预设</NText>
      <NSpace :size="8" wrap>
        <NButton
          v-for="preset in PRESETS"
          :key="preset.id"
          size="small"
          round
          secondary
          @click="applyPreset(preset.chars)"
        >
          {{ preset.name }}
        </NButton>
      </NSpace>
    </div>

    <!-- 操作 -->
    <NSpace :size="12">
      <NButton size="small" quaternary @click="importFromTxt">从 TXT 导入</NButton>
      <NButton size="small" quaternary @click="store.deduplicateCharset()">去重</NButton>
      <NButton size="small" quaternary @click="store.clearCharset()">清空</NButton>
    </NSpace>
  </div>
</template>

<style scoped>
.charset-input {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.charset-header {
  display: flex;
  justify-content: flex-end;
}

.count {
  font-size: 12px;
}

.preset-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.preset-label {
  font-size: 12px;
}
</style>
