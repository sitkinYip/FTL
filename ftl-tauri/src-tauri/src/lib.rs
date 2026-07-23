// FTL Tauri 后端 - sidecar 桥接
//
// 职责:
//   1. spawn Python sidecar 进程(stdio 通信)
//   2. 转发前端命令到 sidecar stdin(NDJSON)
//   3. 读 sidecar stdout,逐行解析后转发为 Tauri event 给前端
//
// 开发阶段:sidecar 用系统 Python 跑 sidecar/ftl_worker.py
// 打包阶段:sidecar 是 PyInstaller 打包的 binaries/ftl-worker(externalBin)

use std::io::{BufRead, BufReader};
use std::sync::{Mutex, OnceLock};
use std::thread;
use tauri::Emitter;
use tauri_plugin_shell::process::{CommandChild, CommandEvent};
use tauri_plugin_shell::ShellExt;

// 全局持有 sidecar 子进程,供 cancel 用
static SIDECAR_CHILD: OnceLock<Mutex<Option<CommandChild>>> = OnceLock::new();

fn sidecar_lock() -> &'static Mutex<Option<CommandChild>> {
    SIDECAR_CHILD.get_or_init(|| Mutex::new(None))
}

/// 启动 sidecar 并持续读 stdout,转发为 `sidecar://event` 给前端。
fn spawn_sidecar(app: tauri::AppHandle) {
    let shell = app.shell();

    // 开发模式:用项目 venv 的 Python(系统 python3 无 fontTools)
    // 路径相对于 src-tauri/(cargo run 的工作目录)
    let python = "../.venv-sidecar/bin/python";
    let worker_path = "../sidecar/ftl_worker.py";

    let (mut rx, child) =
        match shell.command(python).args([worker_path]).spawn() {
            Ok(result) => result,
            Err(e) => {
                log::error!("failed to spawn sidecar: {}", e);
                let _ = app.emit(
                    "sidecar://event",
                    serde_json::json!({"type": "error", "id": "", "message": format!("无法启动 sidecar: {}", e)}),
                );
                return;
            }
        };

    // 保存子进程句柄
    *sidecar_lock().lock().unwrap() = Some(child);

    // 读 stdout/stderr 事件流,转发给前端
    let app_clone = app.clone();
    thread::spawn(move || {
        while let Some(event) = rx.blocking_recv() {
            match event {
                CommandEvent::Stdout(bytes) => {
                    // sidecar 输出是 NDJSON,逐行解析转发
                    let reader = BufReader::new(bytes.as_slice());
                    for line in reader.lines().flatten() {
                        if line.trim().is_empty() {
                            continue;
                        }
                        match serde_json::from_str::<serde_json::Value>(&line) {
                            Ok(msg) => {
                                let _ = app_clone.emit("sidecar://event", msg);
                            }
                            Err(e) => {
                                log::warn!("sidecar stdout 非 JSON: {} | {}", e, line);
                            }
                        }
                    }
                }
                CommandEvent::Stderr(bytes) => {
                    let text = String::from_utf8_lossy(&bytes);
                    log::info!("[sidecar] {}", text.trim());
                }
                CommandEvent::Terminated(payload) => {
                    log::warn!("sidecar terminated: {:?}", payload);
                    let _ = app_clone.emit(
                        "sidecar://event",
                        serde_json::json!({"type": "error", "id": "", "message": "sidecar 已退出"}),
                    );
                }
                CommandEvent::Error(err) => {
                    log::error!("sidecar error: {}", err);
                }
                _ => {}
            }
        }
    });
}

#[tauri::command]
/// 发送命令到 sidecar(stdin 写一行 NDJSON)。
fn send_to_sidecar(command: serde_json::Value) -> Result<(), String> {
    let mut child_guard = sidecar_lock().lock().unwrap();
    if let Some(child) = child_guard.as_mut() {
        let mut line = serde_json::to_string(&command).map_err(|e| e.to_string())?;
        line.push('\n');
        child.write(line.as_bytes()).map_err(|e| e.to_string())?;
        Ok(())
    } else {
        Err("sidecar 未启动".to_string())
    }
}

#[tauri::command]
/// 终止 sidecar(应用退出时调用)。
fn kill_sidecar() {
    let mut child_guard = sidecar_lock().lock().unwrap();
    if let Some(child) = child_guard.take() {
        let _ = child.kill();
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    env_logger::init();
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .setup(|app| {
            spawn_sidecar(app.handle().clone());
            Ok(())
        })
        .on_window_event(|_window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                kill_sidecar();
            }
        })
        .invoke_handler(tauri::generate_handler![send_to_sidecar, kill_sidecar])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
