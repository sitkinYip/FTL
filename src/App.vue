<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { NConfigProvider, NMessageProvider, NDialogProvider, darkTheme } from "naive-ui";
import Home from "./views/Home.vue";

// 跟随系统外观
const prefersDark = ref(false);
const updateTheme = () => {
  prefersDark.value = window.matchMedia("(prefers-color-scheme: dark)").matches;
};

// naive-ui 主题覆盖:Apple 系统蓝
const themeOverrides = {
  common: {
    primaryColor: "#0071E3",
    primaryColorHover: "#0077ED",
    primaryColorPressed: "#0062C4",
    primaryColorSuppl: "#0071E3",
    borderRadius: "8px",
  },
};

const currentTheme = computed(() => (prefersDark.value ? darkTheme : null));

onMounted(() => {
  updateTheme();
  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", updateTheme);
});
</script>

<template>
  <NConfigProvider :theme="currentTheme" :theme-overrides="themeOverrides">
    <NMessageProvider>
      <NDialogProvider>
        <Home />
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>
