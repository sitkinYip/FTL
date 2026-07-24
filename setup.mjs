#!/usr/bin/env node
/**
 * FTL 一键环境安装脚本(跨平台,Node 实现)
 *
 * 用法: node setup.mjs
 *
 * 检测并安装:
 *   1. Node.js + pnpm(前端依赖)
 *   2. Rust + cargo(Tauri 编译)
 *   3. Python 3 + venv + fontTools/brotli(sidecar)
 *
 * 缺少哪个会给出安装指引,已安装的跳过。
 * 全部就绪后自动安装项目依赖,然后可以直接 npm start 启动。
 */

import { execSync, spawnSync } from "child_process";
import { existsSync, readFileSync } from "fs";
import { join } from "path";
import { createInterface } from "readline";
import { platform, arch } from "os";

const OS = platform();
const IS_WIN = OS === "win32";
const IS_MAC = OS === "darwin";
const VENV_DIR = join(process.cwd(), ".venv-sidecar");

// ============================================================
// 工具函数
// ============================================================

function log(msg) {
  console.log(`\x1b[36m[setup]\x1b[0m ${msg}`);
}

function ok(msg) {
  console.log(`\x1b[32m  ✓\x1b[0m ${msg}`);
}

function warn(msg) {
  console.log(`\x1b[33m  !\x1b[0m ${msg}`);
}

function fail(msg) {
  console.log(`\x1b[31m  ✗\x1b[0m ${msg}`);
}

function header(msg) {
  console.log(`\n\x1b[1m${"-".repeat(50)}\n${msg}\n${"-".repeat(50)}\x1b[0m`);
}

/** 运行命令,返回 stdout 字符串(失败返回 null) */
function run(cmd, args = [], opts = {}) {
  try {
    const result = spawnSync(cmd, args, {
      encoding: "utf8",
      shell: IS_WIN,
      stdio: ["pipe", "pipe", "pipe"],
      ...opts,
    });
    if (result.status === 0 || result.status === null) {
      return result.stdout?.trim() || "";
    }
    return null;
  } catch {
    return null;
  }
}

/** 判断命令是否存在 */
function hasCommand(cmd) {
  const check = IS_WIN ? "where" : "which";
  return run(check, [cmd]) !== null;
}

/** 等待用户按回车 */
async function promptContinue(message) {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(`\x1b[33m  ${message} (按回车继续, Ctrl+C 跳过)\x1b[0m `, () => {
      rl.close();
      resolve();
    });
  });
}

// ============================================================
// 检测各工具链
// ============================================================

function checkNode() {
  header("1/4  检测 Node.js");
  const version = run("node", ["--version"]);
  if (version) {
    ok(`Node.js ${version}`);
    return true;
  }
  fail("未检测到 Node.js");
  console.log("    安装方式:");
  console.log("      macOS:   brew install node");
  console.log("      Windows: https://nodejs.org/ 下载安装");
  console.log("      Linux:   sudo apt install nodejs 或 https://nodejs.org/");
  return false;
}

function checkPnpm() {
  const version = run("pnpm", ["--version"]);
  if (version) {
    ok(`pnpm ${version}`);
    return true;
  }
  warn("未检测到 pnpm,正在安装...");
  const result = run("npm", ["install", "-g", "pnpm"]);
  if (result !== null && hasCommand("pnpm")) {
    ok(`pnpm 安装成功 (${run("pnpm", ["--version"])})`);
    return true;
  }
  fail("pnpm 安装失败,请手动运行: npm install -g pnpm");
  return false;
}

function checkRust() {
  header("2/4  检测 Rust / Cargo");
  const rustc = run("rustc", ["--version"]);
  const cargo = run("cargo", ["--version"]);
  if (rustc && cargo) {
    ok(`Rust ${rustc}`);
    ok(`Cargo ${cargo}`);
    return true;
  }
  fail("未检测到 Rust");
  console.log("    安装方式(所有平台通用):");
  console.log("      curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh");
  console.log("    Windows 也可访问 https://rustup.rs/ 下载安装器");
  console.log("    安装后重新运行本脚本。");
  return false;
}

function checkPython() {
  header("3/4  检测 Python 3");

  // 优先尝试 python3,然后 python
  let pyCmd = null;
  let pyVersion = null;
  for (const cmd of ["python3", "python"]) {
    const v = run(cmd, ["--version"]);
    if (v && v.includes("Python 3.")) {
      pyCmd = cmd;
      pyVersion = v;
      break;
    }
  }

  if (!pyCmd) {
    fail("未检测到 Python 3");
    console.log("    安装方式:");
    console.log("      macOS:   brew install python@3");
    console.log("      Windows: https://python.org/ 下载安装(勾选 Add to PATH)");
    console.log("      Linux:   sudo apt install python3 python3-venv");
    return { ok: false };
  }
  ok(`${pyVersion} (${pyCmd})`);
  return { ok: true, cmd: pyCmd };
}

// ============================================================
// 安装项目依赖
// ============================================================

function installFrontendDeps() {
  header("4a/4  安装前端依赖 (pnpm install)");
  if (existsSync("node_modules")) {
    ok("node_modules 已存在,跳过");
    return true;
  }
  log("运行 pnpm install...");
  const result = spawnSync("pnpm", ["install"], {
    stdio: "inherit",
    shell: IS_WIN,
  });
  if (result.status === 0) {
    ok("前端依赖安装完成");
    return true;
  }
  fail("pnpm install 失败");
  return false;
}

function installSidecarDeps(pyCmd) {
  header("4b/4  安装 Python sidecar 依赖");

  // venv 内的 python / pip 路径
  const venvPython = IS_WIN
    ? join(VENV_DIR, "Scripts", "python.exe")
    : join(VENV_DIR, "bin", "python");
  const pip = IS_WIN
    ? join(VENV_DIR, "Scripts", "pip.exe")
    : join(VENV_DIR, "bin", "pip");

  // 检查 venv 是否存在且可用(shebang 路径失效会导致 pip 不可用)
  let venvOk = false;
  if (existsSync(VENV_DIR)) {
    const testResult = spawnSync(venvPython, ["--version"], {
      encoding: "utf8",
      shell: IS_WIN,
    });
    venvOk = testResult.status === 0;
  }

  if (!venvOk) {
    if (existsSync(VENV_DIR)) {
      warn(".venv-sidecar 存在但已失效(可能是目录搬迁导致),重建中...");
    }
    log(`创建虚拟环境 (${pyCmd} -m venv .venv-sidecar)...`);
    // 先删旧的(如果存在但失效)
    if (existsSync(VENV_DIR)) {
      spawnSync(IS_WIN ? "rmdir" : "rm", IS_WIN ? ["/s", "/q", VENV_DIR] : ["-rf", VENV_DIR], {
        shell: IS_WIN,
      });
    }
    const result = spawnSync(pyCmd, ["-m", "venv", ".venv-sidecar"], {
      stdio: "inherit",
      shell: IS_WIN,
    });
    if (result.status !== 0) {
      fail("创建 venv 失败");
      console.log("    可能缺少 python3-venv(Linux: sudo apt install python3-venv)");
      return false;
    }
    ok("虚拟环境创建成功");
  } else {
    ok(".venv-sidecar 已存在且可用,跳过创建");
  }

  // 检查依赖是否已安装
  const depCheck = spawnSync(venvPython, ["-c", "import fontTools, brotli"], {
    encoding: "utf8",
    shell: IS_WIN,
  });
  if (depCheck.status === 0) {
    ok("fontTools + brotli 已安装,跳过");
    return true;
  }

  // 安装 fontTools + brotli
  log("安装 fontTools + brotli...");
  const result = spawnSync(pip, ["install", "-r", "sidecar/requirements.txt"], {
    stdio: "inherit",
    shell: IS_WIN,
  });
  if (result.status === 0) {
    ok("Python sidecar 依赖安装完成");
    return true;
  }
  fail("pip install 失败");
  return false;
}

// ============================================================
// 主流程
// ============================================================

async function main() {
  console.log("\n\x1b[1m╔══════════════════════════════════════════╗");
  console.log("║  FTL - Font Tool Lite 环境安装           ║");
  console.log("║  Tauri + Vue 3 + Python sidecar          ║");
  console.log("╚══════════════════════════════════════════╝\x1b[0m");
  console.log(`  系统: ${OS} ${arch()}`);

  let allOk = true;

  // 1. Node
  if (!checkNode()) allOk = false;
  if (!checkPnpm()) allOk = false;

  // 2. Rust
  if (!checkRust()) allOk = false;

  // 3. Python
  const pyResult = checkPython();
  if (!pyResult.ok) allOk = false;

  if (!allOk) {
    header("缺少必要环境");
    console.log("  请按上方提示安装缺失的工具,然后重新运行 \x1b[1mnode setup.mjs\x1b[0m");
    process.exit(1);
  }

  // 4. 安装项目依赖
  const frontendOk = installFrontendDeps();
  const sidecarOk = installSidecarDeps(pyResult.cmd);

  if (!frontendOk || !sidecarOk) {
    header("部分依赖安装失败");
    console.log("  请查看上方错误信息,修复后重新运行 \x1b[1mnode setup.mjs\x1b[0m");
    process.exit(1);
  }

  // 完成
  header("环境就绪!");
  console.log("  所有依赖已安装。现在可以启动应用:");
  console.log("");
  console.log("    \x1b[32m\x1b[1mnpm start\x1b[0m        # 启动开发模式");
  console.log("    \x1b[32m\x1b[1mnpm run build\x1b[0m    # 构建生产版本");
  console.log("");
  console.log("  首次启动会编译 Rust(约 1-2 分钟),请耐心等待。");
  console.log("");
}

main().catch((err) => {
  fail(`安装过程中出现意外错误: ${err.message}`);
  process.exit(1);
});
