"""Compute and checkpoint color-2/color-3 Jones polynomials with SageMath."""

from ast import literal_eval
from functools import cache
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PD_CODE_FILE = HERE / "com_pd_code_list.txt"
SUB_DATA_DIR = HERE / "sub_data"


def _parse_record(line: str) -> tuple[str, list[list[int]]]:
    stripped = line.strip()
    if not (stripped.startswith("[") and stripped.endswith("]")):
        raise ValueError(f"malformed record: {line!r}")
    knot_name, raw_pd_code = stripped[1:-1].split("|", 1)
    value = literal_eval(raw_pd_code)
    if not isinstance(value, list):
        raise ValueError("PD code field is not a list")
    return knot_name, value


@cache
def get_com_pd_code_list() -> list[tuple[str, list[list[int]]]]:
    return [
        _parse_record(line)
        for line in PD_CODE_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


@cache
def get_com_pd_code_dict() -> dict[str, list[list[int]]]:
    return dict(get_com_pd_code_list())


@cache
def get_colored_jones_for_pd_code(pd_code: str, color: int):
    if isinstance(color, bool) or not isinstance(color, int) or color < 1:
        raise ValueError("color must be a positive integer")
    value = literal_eval(pd_code)
    if not isinstance(value, list):
        raise ValueError("PD code must be a list")
    if not value:
        return 1
    from sage.all import Knot  # Imported lazily so data tooling remains testable without Sage.

    return Knot(value).colored_jones_polynomial(color)


@cache
def get_colored_jones_for_knotname(knot_name: str, color: int):
    components = [component.strip() for component in knot_name.split(",")]
    if not components or any(not component for component in components):
        raise ValueError("knot name contains an empty prime component")
    database = get_com_pd_code_dict()
    result = 1
    for component in components:
        result *= get_colored_jones_for_pd_code(str(database[component]), color)
    return result


def get_colored_jones_for_index(color: int, knot_index: int) -> Path:
    records = get_com_pd_code_list()
    if knot_index < 0 or knot_index >= len(records):
        raise IndexError(f"knot index out of range: {knot_index}")
    SUB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = SUB_DATA_DIR / f"n{color}_k{knot_index:04d}.txt"
    if path.is_file() and not path.read_text(encoding="utf-8").strip():
        path.unlink()
    if not path.is_file():
        knot_name, _ = records[knot_index]
        polynomial = get_colored_jones_for_knotname(knot_name, color)
        path.write_text(f"[{polynomial}|{knot_name}]\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 2:
        raise SystemExit("usage: get_colored_jones_2_and_3.py COLOR KNOT_INDEX")
    get_colored_jones_for_index(int(arguments[0]), int(arguments[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
