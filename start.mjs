#!/usr/bin/env node
/**
 * FTL 启动脚本
 *
 * 用法: npm start  或  node start.mjs
 *
 * 启动前快速检查环境是否就绪,然后运行 npx tauri dev。
 * 如果环境未安装,提示用户先运行 npm run setup。
 */

import { existsSync } from "fs";
import { spawnSync } from "child_process";
import { platform } from "os";

const IS_WIN = platform() === "win32";

function fail(msg) {
  console.error(`\x1b[31m[错误]\x1b[0m ${msg}`);
  process.exit(1);
}

function hasCmd(cmd) {
  const check = IS_WIN ? "where" : "which";
  const r = spawnSync(check, [cmd], { encoding: "utf8", shell: IS_WIN });
  return r.status === 0;
}

// ============================================================
// 环境检查
// ============================================================

console.log("\x1b[36m[start]\x1b[0m 检查运行环境...");

// Node 自身肯定有(否则这个脚本跑不起来)

// pnpm
if (!hasCmd("pnpm")) {
  fail("未检测到 pnpm。请先运行: npm run setup");
}

// 前端依赖
if (!existsSync("node_modules")) {
  fail("前端依赖未安装。请先运行: npm run setup");
}

// Rust
if (!hasCmd("cargo")) {
  fail("未检测到 Rust/Cargo。请先运行: npm run setup");
}

// Python venv
if (!existsSync(".venv-sidecar")) {
  fail("Python 虚拟环境未创建。请先运行: npm run setup");
}

// sidecar 依赖(fontTools)
const venvPython = IS_WIN
  ? ".venv-sidecar/Scripts/python.exe"
  : ".venv-sidecar/bin/python";
const checkDeps = spawnSync(venvPython, ["-c", "import fontTools, brotli"], {
  encoding: "utf8",
  shell: IS_WIN,
});
if (checkDeps.status !== 0) {
  fail("Python sidecar 依赖未安装(fontTools/brotli)。请先运行: npm run setup");
}

console.log("\x1b[32m  ✓\x1b[0m 环境就绪,正在启动...\n");

// ============================================================
// 启动 tauri dev
// ============================================================

console.log("\x1b[36m[start]\x1b[0m 运行 npx tauri dev");
console.log("  首次启动需编译 Rust(约 1-2 分钟),请耐心等待...\n");

const result = spawnSync("npx", ["tauri", "dev"], {
  stdio: "inherit",
  shell: IS_WIN,
  env: { ...process.env, RUST_LOG: process.env.RUST_LOG || "info" },
});

process.exit(result.status || 0);
