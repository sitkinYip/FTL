<script setup lang="ts">
import { NModal, NCard, NSwitch, NButton, NSpace } from "naive-ui";
import { useFontStore } from "../stores/fontStore";

const show = defineModel<boolean>("show", { default: false });
const store = useFontStore();

const switches: { key: keyof typeof store.advanced; label: string }[] = [
  { key: "keep_layout", label: "保留布局特性表(GPOS/GSUB)" },
  { key: "keep_names", label: "保留完整 name 表" },
  { key: "notdef_glyph", label: "保留 .notdef 字形" },
  { key: "glyph_names", label: "保留字形名称(glyph names)" },
  { key: "keep_hinting", label: "保留 hinting 信息" },
];
</script>

<template>
  <NModal v-model:show="show">
    <NCard
      title="高级选项"
      style="width: 400px"
      :bordered="false"
      size="huge"
      role="dialog"
    >
      <NSpace vertical :size="16">
        <div v-for="item in switches" :key="item.key" class="switch-row">
          <span class="switch-label">{{ item.label }}</span>
          <NSwitch v-model:value="store.advanced[item.key]" />
        </div>
      </NSpace>
      <template #footer>
        <div class="dialog-footer">
          <NButton type="primary" @click="show = false">完成</NButton>
        </div>
      </template>
    </NCard>
  </NModal>
</template>

<style scoped>
.switch-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.switch-label {
  font-size: 14px;
  color: var(--ftl-text-primary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>
