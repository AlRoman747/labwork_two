import pytest, os
from pathlib import Path

@pytest.fixture(scope="function")
def env(tmp_path):
    """Создаёт изолированное файловое окружение для тестов команд bash"""

    old_cwd = Path.cwd()
    os.chdir(tmp_path)

    # Создаём тестовую структуру
    (tmp_path / "test").write_text("test labwork file test", encoding="utf-8")
    (tmp_path / "test2").write_text("M8O-103BH-25" + '\n' + "Al-Tahir Roman", encoding="utf-8")
    (tmp_path / "test5").write_text("", encoding="utf-8") # пустой файл

    (tmp_path / "test_dir").mkdir(exist_ok=True)
    (tmp_path / "test_dir2/test_dir3").mkdir(parents=True, exist_ok=True)
    (tmp_path / "test_dir4").mkdir(parents=True, exist_ok=True) # пустая папка
    (tmp_path / ".trash").mkdir(exist_ok=True)

    (tmp_path / "test_dir/test3").write_text("test test test", encoding="utf-8")
    (tmp_path / "test_dir2/test_dir3/test4").write_text("".join('qwertyuiop[]asdfghjkl;'), encoding="utf-8")
    yield tmp_path
    os.chdir(old_cwd)


