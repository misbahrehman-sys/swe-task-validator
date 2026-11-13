import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest

from validator import runner
from validator.cli import DEFAULT_TASKS_DIR, main

HAS_GPP = shutil.which("g++") is not None


def task_path(task_id):
    return os.path.join(DEFAULT_TASKS_DIR, task_id)


def make_task(root, test_command, src_text="VALUE = 1\n", extra=None):
    """Create a tiny throwaway task directory for testing the runner itself."""
    os.makedirs(os.path.join(root, "src"))
    with open(os.path.join(root, "src", "code.py"), "w", encoding="utf-8") as handle:
        handle.write(src_text)
    task = {
        "id": "temp_task",
        "language": "python",
        "description": "temporary task",
        "test_command": test_command,
    }
    task.update(extra or {})
    with open(os.path.join(root, "task.json"), "w", encoding="utf-8") as handle:
        json.dump(task, handle)
    return root


class ListAndLoadTests(unittest.TestCase):
    def test_lists_all_bundled_tasks(self):
        ids = [runner.load_task(path)["id"] for path in runner.list_tasks(DEFAULT_TASKS_DIR)]
        self.assertIn("py_001_average_empty", ids)
        self.assertIn("cpp_001_sum_to_n", ids)
        self.assertGreaterEqual(len(ids), 4)

    def test_missing_field_is_reported(self):
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, "task.json"), "w", encoding="utf-8") as handle:
                json.dump({"id": "x"}, handle)
            with self.assertRaises(ValueError):
                runner.load_task(root)


class RunTaskTests(unittest.TestCase):
    def test_buggy_code_fails(self):
        result = runner.run_task(task_path("py_001_average_empty"))
        self.assertFalse(result["passed"])
        self.assertIn("ZeroDivisionError", result["output_tail"])

    def test_reference_solution_passes(self):
        task_dir = task_path("py_001_average_empty")
        result = runner.run_task(task_dir, candidate_dir=os.path.join(task_dir, "solution"))
        self.assertTrue(result["passed"])

    def test_wrong_candidate_fix_still_fails(self):
        with tempfile.TemporaryDirectory() as candidate:
            os.makedirs(os.path.join(candidate, "src"))
            with open(os.path.join(candidate, "src", "stats.py"), "w", encoding="utf-8") as handle:
                handle.write("def average(numbers):\n    return -1\n")
            result = runner.run_task(task_path("py_001_average_empty"), candidate_dir=candidate)
        self.assertFalse(result["passed"])

    def test_missing_command_returns_127(self):
        with tempfile.TemporaryDirectory() as root:
            make_task(root, ["definitely-not-a-real-command"])
            result = runner.run_task(root)
        self.assertFalse(result["passed"])
        self.assertEqual(result["returncode"], 127)

    def test_timeout_returns_124(self):
        with tempfile.TemporaryDirectory() as root:
            make_task(root, ["python3", "-c", "import time; time.sleep(5)"])
            result = runner.run_task(root, timeout=1)
        self.assertFalse(result["passed"])
        self.assertEqual(result["returncode"], 124)


class ValidateTaskTests(unittest.TestCase):
    def test_python_tasks_are_valid(self):
        for task_id in (
            "py_001_average_empty",
            "py_002_palindrome_phrase",
            "py_003_chunk_last_group",
        ):
            with self.subTest(task=task_id):
                result = runner.validate_task(task_path(task_id))
                self.assertTrue(result["valid"], result["problems"])

    @unittest.skipUnless(HAS_GPP, "g++ is not installed")
    def test_cpp_task_is_valid(self):
        result = runner.validate_task(task_path("cpp_001_sum_to_n"))
        self.assertTrue(result["valid"], result["problems"])

    def test_task_whose_tests_already_pass_is_invalid(self):
        with tempfile.TemporaryDirectory() as root:
            make_task(root, ["python3", "-c", "print('always passes')"])
            os.makedirs(os.path.join(root, "solution", "src"))
            with open(os.path.join(root, "solution", "src", "code.py"), "w", encoding="utf-8") as handle:
                handle.write("VALUE = 2\n")
            result = runner.validate_task(root)
        self.assertFalse(result["valid"])
        self.assertIn("tests already pass on the buggy code", result["problems"])


class CliTests(unittest.TestCase):
    def run_cli(self, argv):
        """Run the CLI with its printed output hidden, and return the exit code."""
        with contextlib.redirect_stdout(io.StringIO()):
            return main(argv)

    def test_list_command(self):
        self.assertEqual(self.run_cli(["list"]), 0)

    def test_validate_single_task(self):
        self.assertEqual(self.run_cli(["validate", "--task", "py_003_chunk_last_group"]), 0)

    def test_run_buggy_task_exits_with_one(self):
        self.assertEqual(self.run_cli(["run", "--task", "py_002_palindrome_phrase"]), 1)

    def test_run_with_solution_exits_with_zero(self):
        solution = os.path.join(task_path("py_002_palindrome_phrase"), "solution")
        argv = ["run", "--task", "py_002_palindrome_phrase", "--candidate", solution]
        self.assertEqual(self.run_cli(argv), 0)


if __name__ == "__main__":
    unittest.main()
