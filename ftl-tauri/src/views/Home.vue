<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { invoke } from "@tauri-apps/api/core";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";

// 临时:验证 sidecar 桥接是否通畅
const sidecarStatus = ref("等待 sidecar...");
const lastEvent = ref("");
let unlisten: UnlistenFn | null = null;

onMounted(async () => {
  try {
    unlisten = await listen("sidecar://event", (event) => {
      lastEvent.value = JSON.stringify(event.payload);
      const payload = event.payload as { type: string };
      if (payload.type === "ready") {
        sidecarStatus.value = "sidecar 已连接 ✓";
      } else if (payload.type === "error") {
        sidecarStatus.value = "sidecar 错误";
      }
    });
    sidecarStatus.value = "正在监听 sidecar 事件...";
  } catch (e) {
    sidecarStatus.value = `监听失败: ${e}`;
  }
});

onUnmounted(() => {
  unlisten?.();
});

// 临时测试按钮:发一个处理命令
const testProcess = async () => {
  try {
    await invoke("send_to_sidecar", {
      command: {
        type: "process",
        id: "test-from-ui",
        files: [],
        characters: "test",
        formats: ["woff2"],
        options: {
          keep_layout: true,
          keep_names: true,
          notdef_glyph: true,
          glyph_names: false,
          keep_hinting: false,
        },
        output_mode: "subdir",
        custom_dir: null,
      },
    });
    sidecarStatus.value = "命令已发送";
  } catch (e) {
    sidecarStatus.value = `发送失败: ${e}`;
  }
};
</script>

<template>
  <div class="home">
    <div class="placeholder">
      <h1>FTL</h1>
      <p>Font Tool Lite (Tauri 版)</p>
      <p class="status">{{ sidecarStatus }}</p>
      <p v-if="lastEvent" class="event mono">{{ lastEvent }}</p>
      <button class="test-btn" @click="testProcess">测试发送命令</button>
    </div>
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.placeholder {
  text-align: center;
}
.placeholder h1 {
  font-size: 48px;
  font-weight: 700;
  margin: 0;
}
.placeholder p {
  color: #6e6e73;
  margin: 8px 0;
}
.status {
  font-weight: 500;
}
.event {
  font-size: 11px;
  opacity: 0.7;
  max-width: 600px;
  word-break: break-all;
  padding: 8px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 6px;
}
.test-btn {
  margin-top: 16px;
  padding: 8px 24px;
  background: #0071e3;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}
.test-btn:hover {
  background: #0077ed;
}
</style>
