"""Command line interface.

    python -m validator.cli list
    python -m validator.cli validate [--task ID]
    python -m validator.cli run --task ID [--candidate DIR]
"""

import argparse
import json
import os
import sys

from .runner import list_tasks, load_task, run_task, validate_task

DEFAULT_TASKS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tasks")


def build_parser():
    parser = argparse.ArgumentParser(description="Validate and run small bug-fix tasks.")
    parser.add_argument("--tasks-dir", default=DEFAULT_TASKS_DIR, help="Folder that holds the tasks")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List available tasks")

    validate = sub.add_parser("validate", help="Check tasks fail before the fix and pass after it")
    validate.add_argument("--task", help="Task id (default: all tasks)")

    run = sub.add_parser("run", help="Run one task's tests, optionally with a candidate fix")
    run.add_argument("--task", required=True, help="Task id")
    run.add_argument("--candidate", help="Folder with replacement files (same relative paths)")
    run.add_argument("--json", action="store_true", help="Print the result as JSON")
    return parser


def find_task_dir(tasks_dir, task_id):
    for task_dir in list_tasks(tasks_dir):
        if load_task(task_dir)["id"] == task_id:
            return task_dir
    raise SystemExit(f"Unknown task id: {task_id}")


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.command == "list":
        for task_dir in list_tasks(args.tasks_dir):
            task = load_task(task_dir)
            print(f"{task['id']:<28} [{task['language']}] {task['description']}")
        return 0

    if args.command == "validate":
        task_dirs = (
            [find_task_dir(args.tasks_dir, args.task)] if args.task else list_tasks(args.tasks_dir)
        )
        all_valid = True
        for task_dir in task_dirs:
            result = validate_task(task_dir)
            status = "VALID  " if result["valid"] else "INVALID"
            print(f"[{status}] {result['task_id']}")
            for problem in result["problems"]:
                print(f"          - {problem}")
            all_valid = all_valid and result["valid"]
        return 0 if all_valid else 1

    if args.command == "run":
        task_dir = find_task_dir(args.tasks_dir, args.task)
        result = run_task(task_dir, candidate_dir=args.candidate)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"{result['task_id']}: {'PASSED' if result['passed'] else 'FAILED'} (stage: {result['stage']})")
            if not result["passed"]:
                print(result["output_tail"])
        return 0 if result["passed"] else 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
