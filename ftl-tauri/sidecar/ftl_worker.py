"""
FTL Sidecar Worker - NDJSON over stdio 主循环

协议:
  stdin  (每行一个 JSON): {"type":"process",...} | {"type":"cancel",...}
  stdout (每行一个 JSON): {"type":"ready",...} | {"type":"progress",...} |
                          {"type":"file_done",...} | {"type":"complete",...} |
                          {"type":"error",...}

业务逻辑复用 font/ + utils/(与 Flet 版完全一致):
  - subset_font:fontTools Subsetter 子集化
  - convert_and_save:woff2(brotli)/ woff(zlib)/ ttf
  - get_output_dir / get_output_basename:输出目录与命名规则

设计要点:
  - 单文件顺序处理(与 Flet 版 AsyncWorker 行为一致,保证进度回调有序)
  - 取消是协作式的:在文件边界检查 _cancelled 标志
  - stdout 仅输出协议消息;所有诊断日志走 stderr(不污染协议通道)
"""

import json
import sys
import time
import threading
from pathlib import Path

from font.subsetter import subset_font
from font.converter import convert_and_save
from utils.file_utils import (
    get_output_dir, ensure_output_dir, get_output_basename,
)
from utils.charset_presets import deduplicate_chars

VERSION = "1.0.0"

# 取消标志:batch_id -> 是否取消
_cancelled: dict[str, bool] = {}
_cancel_lock = threading.Lock()


def emit(event: dict) -> None:
    """向 stdout 输出一行 JSON(协议事件)。"""
    try:
        sys.stdout.write(json.dumps(event, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    except Exception as e:
        # 输出通道异常是致命的,只能记 stderr
        sys.stderr.write(f"[emit error] {e}\n")


def log(msg: str) -> None:
    """诊断日志走 stderr(不干扰 stdout 协议)。"""
    sys.stderr.write(f"[ftl_worker] {msg}\n")
    sys.stderr.flush()


def handle_process(cmd: dict) -> None:
    """处理一批字体文件子集化。

    对应 Flet 版 MainView._on_start + _process_single_file + AsyncWorker.run_batch。
    """
    batch_id = cmd.get("id", "")
    files = cmd.get("files", [])
    characters = cmd.get("characters", "")
    formats = cmd.get("formats", [])
    options_dict = cmd.get("options", {})
    output_mode = cmd.get("output_mode", "subdir")
    custom_dir = cmd.get("custom_dir")

    total = len(files)
    results = []
    ok = 0
    fail = 0
    batch_start = time.time()

    # 去重字符(与 UI 层 deduplicate_chars 一致,保序)
    characters = deduplicate_chars(characters)

    with _cancel_lock:
        _cancelled[batch_id] = False

    for i, file_path in enumerate(files):
        # 协作式取消:在文件边界检查
        with _cancel_lock:
            if _cancelled.get(batch_id, False):
                log(f"batch {batch_id} cancelled at file {i}")
                break

        file_name = Path(file_path).name

        # 进度事件(处理前)
        emit({
            "type": "progress",
            "id": batch_id,
            "completed": i,
            "total": total,
            "current_file": file_name,
            "progress": round(i / total, 4) if total else 0,
        })

        # 处理单个文件(对应 _process_single_file)
        try:
            input_path = Path(file_path)
            output_dir = get_output_dir(
                input_path, mode=output_mode, custom_dir=custom_dir,
            )
            ensure_output_dir(output_dir)

            font = subset_font(input_path, characters, options_dict)
            base_name = get_output_basename(input_path)
            outputs = convert_and_save(font, output_dir, base_name, formats)
            font.close()

            results.append(outputs)
            ok += 1
            emit({
                "type": "file_done",
                "id": batch_id,
                "file": file_name,
                "success": True,
                "outputs": [_serialize_result(r) for r in outputs],
            })
        except Exception as e:
            fail += 1
            error_msg = f"{type(e).__name__}: {e}"
            results.append(None)
            emit({
                "type": "file_done",
                "id": batch_id,
                "file": file_name,
                "success": False,
                "error": error_msg,
            })
            log(f"file {file_name} failed: {error_msg}")

    # 最终进度(100% 或取消时的位置)
    completed = ok + fail
    emit({
        "type": "progress",
        "id": batch_id,
        "completed": completed,
        "total": total,
        "current_file": "",
        "progress": round(completed / total, 4) if total else 1,
    })

    elapsed = round(time.time() - batch_start, 4)
    emit({
        "type": "complete",
        "id": batch_id,
        "ok": ok,
        "fail": fail,
        "elapsed": elapsed,
    })


def handle_cancel(cmd: dict) -> None:
    """标记某个批次为取消(在下个文件边界生效)。"""
    batch_id = cmd.get("id", "")
    with _cancel_lock:
        _cancelled[batch_id] = True
    log(f"cancel requested for batch {batch_id}")


def _serialize_result(r: dict) -> dict:
    """把 convert_and_save 的结果 dict 转成 JSON 友好格式(Path → str)。"""
    out = dict(r)
    if "path" in out and out["path"] is not None:
        out["path"] = str(out["path"])
    return out


def main() -> None:
    """NDJSON stdio 主循环。"""
    # 发送就绪信号
    emit({"type": "ready", "version": VERSION})
    log(f"ftl_worker {VERSION} ready, reading stdin...")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            cmd = json.loads(line)
        except json.JSONDecodeError as e:
            log(f"invalid JSON: {e} | line: {line[:100]}")
            emit({"type": "error", "id": "", "message": f"invalid JSON: {e}"})
            continue

        cmd_type = cmd.get("type")
        if cmd_type == "process":
            handle_process(cmd)
        elif cmd_type == "cancel":
            handle_cancel(cmd)
        else:
            emit({
                "type": "error", "id": cmd.get("id", ""),
                "message": f"unknown command type: {cmd_type}",
            })

    log("stdin closed, exiting")


if __name__ == "__main__":
    main()
