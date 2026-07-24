/**
 * sidecar 通信封装
 *
 * 职责:封装与 Rust 后端(sidecar 桥接)的通信:
 *   - send(command):invoke("send_to_sidecar") 写一行 NDJSON 到 sidecar stdin
 *   - onEvent(callback):监听 "sidecar://event" 事件(sidecar stdout 解析后转发)
 *
 * Rust 侧桥接见 src-tauri/src/lib.rs
 */

import { invoke } from "@tauri-apps/api/core";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";
import type { SidecarCommand, SidecarEvent } from "../types/messages";

/** 向 sidecar 发送命令(经 Rust invoke 转发到 stdin) */
export function sendCommand(command: SidecarCommand): Promise<void> {
  return invoke("send_to_sidecar", { command });
}

/** 查询 sidecar 是否已 ready(解决竞态:ready 可能在此函数调用前已发出) */
export function checkSidecarReady(): Promise<boolean> {
  return invoke<boolean>("check_sidecar_ready");
}

/** 监听 sidecar 事件(经 Rust 从 stdout 解析转发) */
export async function onSidecarEvent(
  callback: (event: SidecarEvent) => void
): Promise<UnlistenFn> {
  return listen<SidecarEvent>("sidecar://event", (event) => {
    callback(event.payload);
  });
}
