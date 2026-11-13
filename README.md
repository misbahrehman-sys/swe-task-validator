# swe-task-validator

A small Python tool that checks whether bug-fix tasks are **valid**, the same idea used to build verifiable software-engineering tasks for evaluating coding models.

A task is a tiny repository with a bug, tests that expose it, and a reference fix. The validator runs the tests twice:

1. on the **buggy** code - the tests must **fail**
2. with the **reference solution** applied - the tests must **pass**

If either check does not hold, the task is invalid (for example, tests that already pass on the buggy code do not test anything). The same runner can also test a candidate fix, which makes it a simple way to see whether a proposed patch really fixes the bug.

Tasks can be in Python (`unittest`) or C++ (`g++`). No external Python packages are needed.

## Bundled tasks

| Task id | Language | Bug |
|---|---|---|
| `py_001_average_empty` | Python | `average([])` raises `ZeroDivisionError` |
| `py_002_palindrome_phrase` | Python | `is_palindrome` does not ignore case or punctuation |
| `py_003_chunk_last_group` | Python | `chunk()` drops the last group (off-by-one in `range`) |
| `cpp_001_sum_to_n` | C++ | `sum_to_n` loop stops one number early |

## Usage

```bash
python -m validator.cli list                      # show tasks
python -m validator.cli validate                  # check all tasks are valid
python -m validator.cli validate --task py_001_average_empty
python -m validator.cli run --task py_001_average_empty            # run on buggy code (fails)
python -m validator.cli run --task py_001_average_empty \
    --candidate tasks/py_001_average_empty/solution                # test a candidate fix
```

Example:

```
$ python -m validator.cli validate
[VALID  ] cpp_001_sum_to_n
[VALID  ] py_001_average_empty
[VALID  ] py_002_palindrome_phrase
[VALID  ] py_003_chunk_last_group
```

The `validate` command exits with code `1` if any task is invalid, so it can run in CI.

## Task layout

```
tasks/<task_id>/
  task.json     id, language, description, build_commands (optional), test_command
  src/          buggy code
  tests/        tests that expose the bug
  solution/     reference fix, using the same relative paths as src/
```

A candidate fix is a folder with replacement files using the same relative paths (for example `src/stats.py`). Tests always run in a temporary copy, so the original task files are never changed.

Note: `task.json` commands are run on your machine. Only run tasks you trust.

## Run the tests

```bash
python -m unittest discover -s tests -t . -v
```

## Run with Docker

```bash
docker build -t swe-task-validator .
docker run --rm swe-task-validator            # validates all tasks
```

## Project structure

```
validator/
  runner.py   runs tasks, applies candidate fixes, validates tasks
  cli.py      command line interface
tasks/        bundled example tasks
tests/        unit tests for the validator itself
.github/workflows/ci.yml   runs unit tests and validates tasks on every push
```

## Ideas for extending

- Add more tasks (other bug types, other languages)
- Report which individual tests failed (fail-to-pass and pass-to-pass lists)
- Run tasks inside Docker for isolation
- Add a `--json` flag to `validate`

## License

MIT
