"""
A simple auto-test runner
    
"""
import os
import pytest
from tqdm import tqdm
from colorama import Fore, Style
from typing import List
import time

import glob


def find_python_files(root_dir: str) -> List[str]:
    python_files = []
    pattern = os.path.join(root_dir, "**", "*.py")
    for python_file in tqdm(
        glob.iglob(pattern, recursive=True),
        desc="Searching for Python Files",
        unit="file",
        leave=False,
    ):
        python_files.append(python_file)
    return python_files


def run_pytest_on_python_files(python_files: List[str]) -> List[str]:
    failed_tests = []
    for python_file in python_files:
        result = pytest.main([python_file])
        if result != 0:
            failed_tests.append(python_file)
    return failed_tests


if __name__ == "__main__":
    current_directory = os.getcwd()
    python_files = find_python_files(current_directory)

    # Initialize a dictionary to store file modification times
    file_modification_times = {
        python_file: os.path.getmtime(python_file) for python_file in python_files
    }

    while True:
        os.system("clear")
        print("Monitoring for file changes...")

        for python_file in python_files:
            mtime = os.path.getmtime(python_file)
            if mtime > file_modification_times.get(python_file, 0):
                # File has been modified, run tests
                file_modification_times[python_file] = mtime
                os.system("clear")
                print(f"Running tests for {python_file}...")

                failed_tests = run_pytest_on_python_files([python_file])

                if failed_tests:
                    print(f"\n{Fore.RED}Failed Tests:{Style.RESET_ALL}")
                    for failed_test in failed_tests:
                        print(f"  {failed_test}")
                else:
                    print(f"\n{Fore.CYAN}All Tests Passed{Style.RESET_ALL}")

        # Sleep for a while before checking again (adjust the interval as needed)
        time.sleep(0.100)
