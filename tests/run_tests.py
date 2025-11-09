from pathlib import *
import sys, pytest

def main():
    """Запуск всех тестов проекта."""
    project_root = Path(__file__).resolve().parent.parent
    tests_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root))

    test_files = sorted(str(p) for p in tests_dir.glob("test*.py"))

    pytest_args = [
        *test_files,
        "-v",
        "--tb=short",
        "--color=yes",
        "--maxfail=1",
    ]

    # Запуск pytest
    exit_code = pytest.main(pytest_args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()