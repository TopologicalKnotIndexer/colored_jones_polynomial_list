from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import unittest
from unittest.mock import patch

from data import get_colored_jones_2_and_3 as colored
from data.ProcessWrap import ProcessWrap
from data.run_all import _run_task


class ColoredJonesToolingTests(unittest.TestCase):
    def tearDown(self):
        colored.get_com_pd_code_list.cache_clear()
        colored.get_com_pd_code_dict.cache_clear()
        colored.get_colored_jones_for_knotname.cache_clear()
        colored.get_colored_jones_for_pd_code.cache_clear()

    def test_record_parser_does_not_execute_code(self):
        self.assertEqual(colored._parse_record("[K0a1|[]]"), ("K0a1", []))
        with self.assertRaises((ValueError, SyntaxError)):
            colored._parse_record("[K0a1|__import__('os').getcwd()]" )

    def test_composite_value_is_product_of_prime_values(self):
        with patch.object(colored, "get_com_pd_code_dict", return_value={"A": [], "B": []}), patch.object(
            colored, "get_colored_jones_for_pd_code", side_effect=[2, 3]
        ):
            self.assertEqual(colored.get_colored_jones_for_knotname("A,B", 2), 6)

    def test_empty_checkpoint_is_recomputed(self):
        with TemporaryDirectory() as directory:
            target = Path(directory)
            path = target / "n2_k0000.txt"
            path.write_text("", encoding="utf-8")
            with patch.object(colored, "SUB_DATA_DIR", target), patch.object(
                colored, "get_com_pd_code_list", return_value=[("K0a1", [])]
            ), patch.object(colored, "get_colored_jones_for_knotname", return_value=1):
                self.assertEqual(colored.get_colored_jones_for_index(2, 0), path)
            self.assertEqual(path.read_text(encoding="utf-8"), "[1|K0a1]\n")

    def test_process_wrap_honors_working_directory(self):
        with TemporaryDirectory() as directory:
            process = ProcessWrap(
                ["python", "-c", "import os; print(os.getcwd())"], directory
            )
            process.run_task()
            status = process.wait(timeout=10)
            self.assertEqual(status["status"], "TERM")
            self.assertEqual(Path(status["info"]["stdout"].strip()), Path(directory))

    def test_process_wrap_drains_large_output_without_deadlock(self):
        with TemporaryDirectory() as directory:
            process = ProcessWrap(
                ["python", "-c", "print('x' * 1000000)"], directory
            )
            process.run_task()
            status = process.wait(timeout=10)
            self.assertEqual(status["info"]["returncode"], 0)
            self.assertEqual(len(status["info"]["stdout"].strip()), 1_000_000)

    def test_run_task_reports_timeout(self):
        with patch("data.run_all.subprocess.run", side_effect=subprocess.TimeoutExpired(["x"], 1)):
            result = _run_task(2, 0, timeout=1)
        self.assertTrue(result["timed_out"])
        self.assertIsNone(result["returncode"])


if __name__ == "__main__":
    unittest.main()
