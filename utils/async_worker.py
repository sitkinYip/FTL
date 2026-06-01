"""
线程池异步任务封装

避免字体处理阻塞 UI 线程，使用 ThreadPoolExecutor 进行后台处理。
"""

import time
import traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from typing import Callable, Any


@dataclass
class TaskResult:
    """单个任务处理结果"""
    input_file: str = ""
    success: bool = False
    outputs: list = field(default_factory=list)
    error: str = ""
    elapsed: float = 0.0


@dataclass
class BatchProgress:
    """批处理进度"""
    total: int = 0
    completed: int = 0
    current_file: str = ""
    results: list = field(default_factory=list)

    @property
    def progress(self) -> float:
        """当前进度比例 0.0 ~ 1.0"""
        if self.total == 0:
            return 0.0
        return self.completed / self.total


class AsyncWorker:
    """
    异步任务工作器

    使用线程池执行字体处理任务，通过回调更新 UI。
    """

    def __init__(self, max_workers: int = 2):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._futures: list[Future] = []
        self._cancelled = False

    def submit_task(
        self,
        fn: Callable,
        args: tuple = (),
        kwargs: dict = None,
        on_complete: Callable[[TaskResult], None] = None,
        on_error: Callable[[str], None] = None,
    ) -> Future:
        """
        提交单个任务到线程池

        Args:
            fn: 要执行的函数
            args: 位置参数
            kwargs: 关键字参数
            on_complete: 完成回调
            on_error: 错误回调

        Returns:
            Future 对象
        """
        if kwargs is None:
            kwargs = {}

        def wrapped():
            start = time.time()
            try:
                result = fn(*args, **kwargs)
                elapsed = time.time() - start
                task_result = TaskResult(
                    success=True,
                    outputs=result if isinstance(result, list) else [result],
                    elapsed=elapsed,
                )
                if on_complete:
                    on_complete(task_result)
                return task_result
            except Exception as e:
                elapsed = time.time() - start
                error_msg = f"{type(e).__name__}: {str(e)}"
                task_result = TaskResult(
                    success=False,
                    error=error_msg,
                    elapsed=elapsed,
                )
                if on_error:
                    on_error(error_msg)
                return task_result

        future = self._executor.submit(wrapped)
        self._futures.append(future)
        return future

    def submit_batch(
        self,
        tasks: list[dict],
        on_progress: Callable[[BatchProgress], None] = None,
        on_all_complete: Callable[[BatchProgress], None] = None,
    ):
        """
        提交批量任务

        Args:
            tasks: 任务列表，每项包含 {"fn", "args", "kwargs", "file_name"}
            on_progress: 进度更新回调
            on_all_complete: 全部完成回调
        """
        progress = BatchProgress(total=len(tasks))

        def run_batch():
            for task in tasks:
                if self._cancelled:
                    break

                file_name = task.get("file_name", "")
                progress.current_file = file_name

                start = time.time()
                try:
                    fn = task["fn"]
                    args = task.get("args", ())
                    kwargs = task.get("kwargs", {})
                    result = fn(*args, **kwargs)
                    elapsed = time.time() - start

                    task_result = TaskResult(
                        input_file=file_name,
                        success=True,
                        outputs=result if isinstance(result, list) else [result],
                        elapsed=elapsed,
                    )
                except Exception as e:
                    elapsed = time.time() - start
                    task_result = TaskResult(
                        input_file=file_name,
                        success=False,
                        error=f"{type(e).__name__}: {str(e)}",
                        elapsed=elapsed,
                    )

                progress.completed += 1
                progress.results.append(task_result)

                if on_progress:
                    on_progress(progress)

            if on_all_complete:
                on_all_complete(progress)

        self._cancelled = False
        self._executor.submit(run_batch)

    def cancel(self):
        """取消当前批处理"""
        self._cancelled = True

    def shutdown(self):
        """关闭线程池"""
        self._cancelled = True
        self._executor.shutdown(wait=False)
