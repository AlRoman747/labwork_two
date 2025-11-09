import pytest

from src.bash import *


@pytest.mark.usefixtures("env")
class TestCommandFunctions:
    def test_ls(self, env):
        """Проверка отображения файлов в папке"""
        res = ls([env])
        assert "test" in res; assert "test2" in res; assert "test_dir" in res # проверка корректности

        res = ls(['-l', env])
        assert "test" in res[2]; assert 'drw' in res[1]

        env = env / "test_dir"
        res = ls([env])
        assert "test3" in res
        assert "sxjnkc" not in res

    def test_cd(self, env):
        """Проверка функции смены католога"""
        start = Path.cwd()
        src = env / "test_dir2"
        cd([src])
        assert Path.cwd() == src.resolve()
        os.chdir(start)

    def test_cat(self, env):
        """Проверка корректного вывода содержимого файла"""
        file1 = env / "test"; file2 = env / "test2"; file9 = env / "test9"
        res = cat([file1, file2, file9])
        assert "test labwork file test" in res; assert "Al-Tahir Roman" in res[1]; assert "No such file or directory" in res[2]
    def test_cp(self, env):
        """Проверка копирования обычного файла."""
        cp_from = env / "test"
        cp_to = env / "test5"
        cp([cp_from, cp_to])
        assert cp_from.exists(); assert cp_to.read_text() == cp_from.read_text()

        """Проверка копирования директории."""
        cp_from = env / "test_dir"
        cp_to = env / "test_dir4"
        cp(['-r', cp_from, cp_to])
        assert cp_to.is_dir(); assert (cp_to / "test3").exists()

    def test_mv_file(self, env):
        """Перемещение файла в другую директорию."""
        mv_from = env / "test"
        mv_to = env / "test_dir2/test_dir3"
        dst = mv_to / "test4"
        mv([mv_from, dst])
        assert not mv_from.exists(); assert dst.exists()

    def test_rm_file(self, env):
        """Удаление файла в .trash."""
        src = env / "test"
        trash_dir = env / ".trash"
        assert '/' != str(src); assert '..' != str(src)
        rm([src])
        trashed = next(trash_dir.glob("test*"), None)
        assert trashed and trashed.exists()

    def test_grep(self, env):
        """Поиск строки в файле."""
        file = env / "test2"
        res = grep(["Roman", file])
        assert len(res) == 1
        assert "Roman" in res[0]



