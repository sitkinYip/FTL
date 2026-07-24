/**
 * 跨平台剪贴板文件读取
 *
 * macOS: osascript 读 Finder ⌘C 复制的文件路径(«class furl»)
 * Windows: PowerShell Get-Clipboard 读文件路径
 * Linux: xclip / xsel 读剪贴板
 *
 * 注意:AppleScript 的换行用多个 -e 参数传递(而非字面 \n),
 * 避免转义问题。«» 在 UTF-8 下通过 shell 传递是安全的。
 */

import { Command } from "@tauri-apps/plugin-shell";

/** 支持的字体扩展名 */
const FONT_EXTENSIONS = [".ttf", ".otf", ".woff", ".woff2"];

function isFontFile(path: string): boolean {
  const lower = path.toLowerCase();
  return FONT_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

/** 从剪贴板读取字体文件路径(跨平台) */
export async function readClipboardFiles(): Promise<string[]> {
  const platform = detectPlatform();
  try {
    const rawPaths = await readClipboardRaw(platform);
    const paths = rawPaths
      .map((p) => p.trim().replace(/^["']|["']$/g, ""))
      .filter((p) => p.length > 0 && isFontFile(p));
    // 去重
    return [...new Set(paths)];
  } catch {
    return [];
  }
}

type Platform = "macos" | "windows" | "linux";

function detectPlatform(): Platform {
  const ua = navigator.userAgent.toLowerCase();
  if (ua.includes("mac")) return "macos";
  if (ua.includes("win")) return "windows";
  return "linux";
}

async function readClipboardRaw(platform: Platform): Promise<string[]> {
  switch (platform) {
    case "macos":
      return readMacClipboard();
    case "windows":
      return readWindowsClipboard();
    case "linux":
      return readLinuxClipboard();
  }
}

/** macOS:osascript 读 Finder 文件,用多个 -e 传脚本(避免换行转义问题) */
async function readMacClipboard(): Promise<string[]> {
  // 尝试单文件:clipboard as «class furl»
  try {
    const output = await runShell("osascript", [
      "-e",
      'set theFiles to (the clipboard as \u00abclass furl\u00bb) as text',
      "-e",
      "set posixPath to POSIX path of theFiles",
      "-e",
      "return posixPath",
    ]);
    if (output.trim()) return [output.trim()];
  } catch {
    // 不是单文件或剪贴板无文件,继续
  }

  // 尝试多文件:alias list
  try {
    const output = await runShell("osascript", [
      "-e",
      'set fileList to (the clipboard as \u00abclass furl\u00bb)',
      "-e",
      'set output to ""',
      "-e",
      "repeat with f in fileList",
      "-e",
      '  set output to output & (POSIX path of (f as text)) & linefeed',
      "-e",
      "end repeat",
      "-e",
      "return output",
    ]);
    if (output.trim()) {
      return output.trim().split("\n").filter((l) => l.trim());
    }
  } catch {
    // 继续 fallback
  }

  // fallback:pbpaste(用户可能用 ⌥⌘C 复制了路径文本)
  try {
    const output = await runShell("pbpaste", []);
    if (output.trim()) {
      return output.trim().split("\n").filter((l) => l.trim());
    }
  } catch {
    // 放弃
  }
  return [];
}

/** Windows:PowerShell Get-Clipboard */
async function readWindowsClipboard(): Promise<string[]> {
  try {
    const output = await runShell("powershell", [
      "-NoProfile",
      "-Command",
      "Get-Clipboard -Format FileDropList",
    ]);
    if (output.trim()) {
      return output.trim().split("\n").filter((l) => l.trim());
    }
  } catch {
    // fallback:纯文本
    try {
      const text = await runShell("powershell", [
        "-NoProfile",
        "-Command",
        "Get-Clipboard",
      ]);
      if (text.trim()) {
        return text.trim().split("\n").filter((l) => l.trim());
      }
    } catch {
      // 放弃
    }
  }
  return [];
}

/** Linux:xclip / xsel */
async function readLinuxClipboard(): Promise<string[]> {
  // xclip
  try {
    const output = await runShell("xclip", [
      "-selection",
      "clipboard",
      "-o",
    ]);
    if (output.trim()) {
      return output.trim().split("\n").filter((l) => l.trim());
    }
  } catch {
    // 试 xsel
  }
  try {
    const output = await runShell("xsel", ["--clipboard", "--output"]);
    if (output.trim()) {
      return output.trim().split("\n").filter((l) => l.trim());
    }
  } catch {
    // 放弃
  }
  return [];
}

/** 执行 shell 命令并返回 stdout(通过 Tauri shell 插件) */
async function runShell(program: string, args: string[]): Promise<string> {
  const command = Command.create(program, args);
  const output = await command.execute();
  if (output.code !== 0) {
    throw new Error(output.stderr || `exit code ${output.code}`);
  }
  return output.stdout;
}
