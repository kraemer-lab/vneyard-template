import sys
import logging
import subprocess
from enum import Enum
from pathlib import Path

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("report.txt")
logger.addHandler(console_handler)
logger.addHandler(file_handler)


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
        return Status.PASSED
    else:
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

    for module in passed_modules:
        logger.info(f"✅ {module}: Passed")
    for module in skipped_modules:
        logger.info(f"🟡 {module}: Skipped")
    for module in failed_modules:
        logger.info(f"❌ {module}: Failed")
    if failed_modules:
        logger.info("❌ Some modules failed.")
        exit(1)
    if not skipped_modules and not passed_modules:
        logger.info("🟡 There were no modules to test.")
        exit(0)
    if skipped_modules:
        logger.info("🟡 Some modules were skipped.")
        exit(0)
    logger.info("✅ All modules passed.")
    exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: script.py <main_commit_hash> <pr_commit_hash>")
        sys.exit(1)
    main_commit_hash = sys.argv[1]
    fork_commit_hash = sys.argv[2]
    module_list = get_module_list(main_commit_hash, fork_commit_hash)
    logger.info(f"Modules to test: {module_list}")
    run_tests(module_list)
