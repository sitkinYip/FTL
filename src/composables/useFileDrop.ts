/**
 * 原生文件拖拽封装(Tauri onDragDropEvent)
 *
 * 关键:不用 HTML5 的 dataTransfer(在 Tauri webview 里拿不到绝对路径),
 * 而用 Tauri 原生拖拽事件,直接拿到文件系统路径数组。
 *
 * dragDropEnabled: true 已在 tauri.conf.json 配置,
 * Tauri 会在窗口级拦截 OS 文件拖放并派发 onDragDropEvent。
 */

import { getCurrentWindow } from "@tauri-apps/api/window";
import type { UnlistenFn } from "@tauri-apps/api/event";

export interface DragDropState {
  /** 是否有文件正在悬停(用于高亮拖拽区) */
  isHovering: boolean;
}

export type FileDropCallback = (paths: string[]) => void;

/**
 * 监听原生文件拖放。
 *
 * @param onDrop 文件被放下时的回调,参数是文件路径数组
 * @returns 取消监听函数
 */
export async function listenFileDrop(onDrop: FileDropCallback): Promise<UnlistenFn> {
  const appWindow = getCurrentWindow();
  return appWindow.onDragDropEvent((event) => {
    if (event.payload.type === "enter" || event.payload.type === "over") {
      // 拖拽进入/悬停 - 可用于高亮(通过自定义事件或状态)
      window.dispatchEvent(
        new CustomEvent("ftl:drag-hover", { detail: true })
      );
    } else if (event.payload.type === "leave") {
      // 拖拽离开
      window.dispatchEvent(
        new CustomEvent("ftl:drag-hover", { detail: false })
      );
    } else if (event.payload.type === "drop") {
      // 放下 - 拿到路径数组
      window.dispatchEvent(
        new CustomEvent("ftl:drag-hover", { detail: false })
      );
      const paths = event.payload.paths;
      if (paths && paths.length > 0) {
        onDrop(paths);
      }
    }
  });
}
