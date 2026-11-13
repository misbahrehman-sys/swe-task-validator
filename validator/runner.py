"""Run a bug-fix task's tests, with or without a candidate fix.

A task directory looks like this:

    task.json      description + build/test commands
    src/           the buggy code
    tests/         tests that fail because of the bug
    solution/      reference fix (same relative paths as src/)

A task is VALID when its tests FAIL on the buggy code and PASS once the
reference solution is applied.
"""

import json
import os
import shutil
import subprocess
import tempfile

TAIL_CHARS = 1500


def load_task(task_dir):
    with open(os.path.join(task_dir, "task.json"), encoding="utf-8") as handle:
        task = json.load(handle)
    for key in ("id", "language", "description", "test_command"):
        if key not in task:
            raise ValueError(f"{task_dir}/task.json is missing '{key}'")
    return task


def list_tasks(tasks_root):
    """Return sorted task directories that contain a task.json file."""
    found = []
    for name in sorted(os.listdir(tasks_root)):
        path = os.path.join(tasks_root, name)
        if os.path.isfile(os.path.join(path, "task.json")):
            found.append(path)
    return found


def _overlay(source_dir, target_dir):
    """Copy every file under source_dir onto target_dir, keeping relative paths."""
    for folder, _, files in os.walk(source_dir):
        for filename in files:
            source = os.path.join(folder, filename)
            relative = os.path.relpath(source, source_dir)
            destination = os.path.join(target_dir, relative)
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copyfile(source, destination)


def _run(command, cwd, timeout):
    """Run one command (a list, no shell). Return (returncode, output)."""
    try:
        completed = subprocess.run(
            command, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
    except FileNotFoundError:
        return 127, f"command not found: {command[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout} seconds"
    return completed.returncode, completed.stdout + completed.stderr


def run_task(task_dir, candidate_dir=None, timeout=60):
    """Run the task's tests in a temporary copy and report the result.

    candidate_dir (optional) holds replacement files, using the same relative
    paths as the task (for example src/stats.py).
    """
    task = load_task(task_dir)
    with tempfile.TemporaryDirectory() as workdir:
        shutil.copytree(
            task_dir,
            workdir,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("solution", "__pycache__"),
        )
        if candidate_dir:
            _overlay(candidate_dir, workdir)

        stage = "build"
        output = ""
        for command in task.get("build_commands", []):
            code, output = _run(command, workdir, timeout)
            if code != 0:
                return _result(task, False, stage, code, output)

        stage = "test"
        code, output = _run(task["test_command"], workdir, timeout)
        return _result(task, code == 0, stage, code, output)


def _result(task, passed, stage, returncode, output):
    return {
        "task_id": task["id"],
        "passed": passed,
        "stage": stage,
        "returncode": returncode,
        "output_tail": output[-TAIL_CHARS:],
    }


def validate_task(task_dir, timeout=60):
    """A task is valid if tests fail on the bug and pass with the reference fix."""
    task = load_task(task_dir)
    before = run_task(task_dir, timeout=timeout)
    solution_dir = os.path.join(task_dir, "solution")
    after = run_task(task_dir, candidate_dir=solution_dir, timeout=timeout)

    problems = []
    if before["passed"]:
        problems.append("tests already pass on the buggy code")
    if before["stage"] == "build" and not before["passed"]:
        problems.append("buggy code does not build (it should build but fail tests)")
    if not after["passed"]:
        problems.append("tests still fail with the reference solution")

    return {
        "task_id": task["id"],
        "valid": not problems,
        "problems": problems,
        "fails_before_fix": not before["passed"],
        "passes_after_fix": after["passed"],
    }
