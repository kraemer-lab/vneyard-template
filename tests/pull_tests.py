import sys
import subprocess
from enum import Enum
from pathlib import Path


class Status(Enum):
    PASSED = 0
    FAILED = 1
    SKIPPED = 2


def get_module_list(main_commit_hash, fork_commit_hash):
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", main_commit_hash, fork_commit_hash],
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        print(e)
        exit(1)
    modules = result.stdout.decode("utf-8").split("\n")
    module_list = [module for module in modules if module.startswith("workflows")]
    module_list = ['/'.join(module.split("/", 4)[:4]) for module in module_list]
    return list(set(module_list))


def test_module(module_path):
    # Check if file exists
    if not Path(module_path + "/.test.sh").exists():
        print(f"Test script for module {module_path} does not exist.")
        return Status.SKIPPED
    try:
        result = subprocess.run(["bash", ".test.sh"], cwd=module_path)
    except Exception as e:
        print(e)
        return Status.FAILED
    if result.returncode == 0:
        print(f"Module {module_path} passed.")
        return Status.PASSED
    else:
        print(f"Module {module_path} failed.")
        return Status.FAILED


def run_tests(module_list):
    passed_modules = []
    failed_modules = []
    skipped_modules = []
    for module in module_list:
        test_status = test_module(module)
        if test_status == Status.PASSED:
            passed_modules.append(module)
        elif test_status == Status.SKIPPED:
            skipped_modules.append(module)
        else:
            failed_modules.append(module)

    print("Passed modules: ", passed_modules)
    if skipped_modules:
        print("Skipped modules: ", skipped_modules)
    if failed_modules:
        print("Failed modules: ", failed_modules)
        exit(1)
    # No failed modules
    print("All modules passed.")
    exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: script.py <main_commit_hash> <pr_commit_hash>")
        sys.exit(1)
    main_commit_hash = sys.argv[1]
    fork_commit_hash = sys.argv[2]
    module_list = get_module_list(main_commit_hash, fork_commit_hash)
    print(f"Modules to test: {module_list}")
    run_tests(module_list)
