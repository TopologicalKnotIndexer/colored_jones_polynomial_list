"""Run all colored-Jones checkpoints with bounded parallel subprocesses."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
import subprocess
import sys
import time


TIME_LIMIT_SEC = 60
HERE = Path(__file__).resolve().parent
WORKER = HERE / "get_colored_jones_2_and_3.py"
LOG_DIR = HERE / "log"
KNOT_COUNT = 1783


def _run_task(color: int, knot_index: int, timeout: float = TIME_LIMIT_SEC) -> dict:
    started = time.monotonic()
    command = [sys.executable, str(WORKER), str(color), str(knot_index)]
    try:
        result = subprocess.run(
            command,
            cwd=HERE,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        return {
            "color": color,
            "knot_index": knot_index,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "elapsed_seconds": time.monotonic() - started,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "color": color,
            "knot_index": knot_index,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "elapsed_seconds": time.monotonic() - started,
            "timed_out": True,
        }


def main(process_count: int = 10) -> int:
    if process_count < 1:
        raise ValueError("process_count must be positive")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    tasks = [(color, index) for index in range(KNOT_COUNT) for color in (2, 3)]
    failures = 0
    with ThreadPoolExecutor(max_workers=process_count) as executor:
        futures = {executor.submit(_run_task, *task): task for task in tasks}
        for completed, future in enumerate(as_completed(futures), start=1):
            record = future.result()
            if record["returncode"] != 0:
                failures += 1
            log_path = LOG_DIR / f"n{record['color']}_k{record['knot_index']:04d}.json"
            log_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
            if completed % 100 == 0 or completed == len(tasks):
                print(f"completed {completed}/{len(tasks)}; failures={failures}", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    raise SystemExit(main(workers))
