"""Compatibility process wrapper with non-blocking pipe collection."""

from pathlib import Path
import shlex
import subprocess
import threading
import time
import uuid


def generate_random_string(length: int) -> str:
    value = ""
    while len(value) < length:
        value += uuid.uuid4().hex
    return value[:length]


global_process_wrap_dict: dict[str, "ProcessWrap"] = {}


class ProcessWrap:
    """Track one subprocess through `INIT`, `RUN`, and `TERM` states."""

    def __init__(self, cmd: list[str], cwd: str):
        if not cmd or not all(isinstance(item, str) for item in cmd):
            raise TypeError("cmd must be a non-empty list of strings")
        if not Path(cwd).is_dir():
            raise NotADirectoryError(cwd)
        self.obj_uuid = "ProcessWrap_" + generate_random_string(128)
        global_process_wrap_dict[self.obj_uuid] = self
        self.cmd = list(cmd)
        self.cwd = cwd
        self.begin_time = time.monotonic()
        self.pobj: subprocess.Popen | None = None
        self.stdout: bytes | None = None
        self.stderr: bytes | None = None
        self.run_time: float | None = None
        self.aux_info = ""
        self.lock = threading.RLock()
        self._completed = threading.Event()

    def _collect(self) -> None:
        assert self.pobj is not None
        stdout, stderr = self.pobj.communicate()
        with self.lock:
            self.stdout = stdout
            self.stderr = stderr
            self.run_time = time.monotonic() - self.begin_time
            self._completed.set()

    def get_status_time_now(self) -> float:
        with self.lock:
            return self.run_time if self.run_time is not None else time.monotonic() - self.begin_time

    def get_status(self) -> dict:
        with self.lock:
            common = {
                "obj_uuid": self.obj_uuid,
                "begin_time": self.begin_time,
                "cmd": self.cmd,
                "cwd": self.cwd,
                "info": None,
            }
            if self.pobj is None:
                common["status"] = "INIT"
            elif not self._completed.is_set():
                common["status"] = "RUN"
            else:
                common.update(
                    {
                        "status": "TERM",
                        "info": {
                            "returncode": self.pobj.returncode,
                            "stdout": (self.stdout or b"").decode("utf-8", errors="replace"),
                            "stderr": (self.stderr or b"").decode("utf-8", errors="replace"),
                            "run_time": self.run_time,
                        },
                    }
                )
            return common

    def run_task(self) -> None:
        with self.lock:
            if self.pobj is not None:
                return
            self.begin_time = time.monotonic()
            self.pobj = subprocess.Popen(
                self.cmd,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            threading.Thread(target=self._collect, daemon=True).start()

    def wait(self, timeout: float | None = None) -> dict:
        if self.pobj is None:
            raise RuntimeError("task has not been started")
        if not self._completed.wait(timeout):
            raise TimeoutError("process did not finish before timeout")
        return self.get_status()

    def kill_task(self, timeout: float = 5) -> None:
        with self.lock:
            process = self.pobj
            if process is None or self._completed.is_set():
                return
            process.terminate()
            self.aux_info = "KILLED"
        if not self._completed.wait(timeout):
            process.kill()
            if not self._completed.wait(timeout):
                raise TimeoutError("could not collect terminated process")


if __name__ == "__main__":
    wrapper = ProcessWrap(shlex.split("python -c \"print('hello')\""), str(Path.cwd()))
    print(wrapper.get_status())
    wrapper.run_task()
    print(wrapper.wait(timeout=10))
