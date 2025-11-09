import shutil, zipfile, tarfile, stat, re, os
from pathlib import *



mv_from_path, rm_from_path = Path.cwd(), Path.cwd() # используется для сохранения изначального пути для команды undo
ROOT_DIR = Path(__file__).parent.resolve()
HISTORY_FILE = ROOT_DIR / '.history' # используется для корректной записи в history

def ls(args):
    """Реализация команды отображения файлов и папок в каталоге"""
    l_flag = '-l' in args # проверка наличия параметра -l
    paths = [arg for arg in args if arg != '-l']
    path = Path(paths[0]) if paths else Path.cwd() # создания путя, которой будет отображаться командой ls
    if not path.exists(): raise FileNotFoundError(f"ls: {path.name}: No such file or directory") # обработка ошибки отсутствия файла
    if not l_flag: return [entry.name for entry in path.iterdir()] # с этой строки и далее логика вывода всех файлов в папке
    else:
        res = []
        total = 0
        for entry in path.iterdir():
            info = entry.stat()
            res.append(f"{stat.filemode(info.st_mode)} {info.st_nlink} {info.st_uid} {info.st_gid} {info.st_size} {info.st_mtime} {entry.name}")
            total += 4*(info.st_size != 0)
        res.insert(0, f'total {total}')

        return [s for s in res]


def cd(args):
    """смена католога"""
    if len(args) > 1: raise ValueError("cd: too many arguments")
    path = Path(args[0]).expanduser().resolve()
    if not path.exists(): raise FileNotFoundError(f"cd: {path.name}: No such file or directory")
    if not path.is_dir(): raise IsADirectoryError(f"cd: Incorrect command")
    os.chdir(path)

    return ['']


def cat(args):
    """вывод содержимого файла с возможностью выводит содержимое сразу нескольких файлов"""
    info_from_files = []
    if not(args): raise ValueError("cat: Incorrect command")
    for file in args:
        path = Path(file).expanduser().resolve()
        if not path.exists(): info_from_files.append(f"cat: {path.name}: No such file or directory"); continue
        if path.is_dir(): info_from_files.append(f"cat: {path.name}: Is a directory"); continue
        inform = path.read_text(encoding="utf-8")
        info_from_files.append(inform)

    return info_from_files


def cp(args):
    """копирование файла с возможностью копировать сразу несколько файлов с сохранением изначального пути"""
    global cp_from_file
    if len(args) < 2: raise ValueError("cp: Incorrect command")
    copy_to = Path(args[-1]).expanduser().resolve()
    r_flag = args[0] == '-r'
    if copy_to.is_dir(): # копирование если копируем папки
        if r_flag:
            for odj in args[1:-1]:
                copy_from = Path(odj).expanduser().resolve()
                if copy_from.is_dir(): shutil.copytree(copy_from, copy_to, dirs_exist_ok=True)
                else: shutil.copy(copy_from, copy_to)
        else: # копирование если копируем файлы
            for odj in args[:-1]:
                copy_from = Path(odj).expanduser().resolve()
                if copy_from.is_dir(): raise ValueError(f"cp: -r not specified; omitting directory {copy_from.name}")
                else: shutil.copy(copy_from, copy_to)
    elif copy_to.is_file():
        for odj in args[:-1]:
            copy_from = Path(odj).expanduser().resolve()
            if copy_from.is_dir(): raise ValueError(f"cp: -r not specified; omitting directory {copy_from.name}")
            else: shutil.copy(copy_from, copy_to)
    else: raise ValueError(f'cp: {copy_to.name} not a file or a directory')

    return ['']


def mv(args):
    """Перемещение в другие каталоги с сохранением изначального пути файла"""
    global mv_from_path
    if len(args) < 2: raise ValueError(f"mv: missing destination file operand after '{args[0]}'")
    if len(args) >= 2:
        mv_to = args[-1]
        for i in args[:-1]:
            mv_from = i
            if not Path(mv_from).expanduser().resolve().exists(): raise FileNotFoundError(f"mv: '{Path(mv_from).name}': No such file or directory")
            try: shutil.move(str(mv_from), str(mv_to)); mv_from_path = Path.cwd()
            except PermissionError: raise PermissionError(f"mv: cannot move '{mv_from.name}' to '{Path(mv_to).name}': Permission denied")

    return ['']


def rm(args):
    """Удаление(перемещение в корзину) файла с сохранением изначального пути файла"""
    global rm_from_path
    if args[-1] in ['..', '/']:
        raise ValueError('you cannot del parents dir') # проверка на удаление корня
    r_flag = args[0] == '-r'
    trash_dir = Path(".trash").expanduser().resolve()
    if r_flag:
        for obj in args[1:]:
            path = Path(obj).expanduser().resolve()
            if not path.exists(): raise FileNotFoundError(f"rm: cannot remove '{path.name}': No such file or directory")
            if path.is_file():
                try: shutil.move(str(path.name), trash_dir); rm_from_path = Path.cwd()
                except Exception as e: raise e

            else:
                if input(f"rm: remove directory '{path.name}'? ").strip() == 'y':
                    shutil.move(str(path.name), trash_dir)
                    rm_from_path = Path.cwd()
                else: continue
    else:
        for obj in args:
            path = Path(obj).expanduser().resolve()
            if not path.exists(): raise FileNotFoundError(f"rm: cannot remove '{path.name}': No such file or directory"); continue
            if path.is_file(): shutil.move(str(path.name), trash_dir)
            else: raise IsADirectoryError(f"rm: cannot remove '{path.name}': Is a directory")

    return ['']


def zip(args):
    """Архивация через zip"""
    zip_from = Path(args[0]).expanduser().resolve()
    zip_to = Path(args[1]).expanduser().resolve()
    if not zip_from.exists(): raise FileNotFoundError(f"zip: cannot zip '{zip_from.name}': No such file or directory")
    if zip_to.suffix != '.zip': zip_to = zip_to.with_suffix('.zip')
    with zipfile.ZipFile(zip_to, 'w', zipfile.ZIP_DEFLATED) as bash_zip:
        if zip_from.is_dir():
            for file in zip_from.rglob('*'): bash_zip.write(file, file.relative_to(zip_from))
        elif zip_from.is_file(): bash_zip.write(zip_from, zip_from.name)
        else: raise ValueError(f'zip: {zip_from.name} not a file or a directory')

    return ['']

def unzip(args):
    """Открытие zip архива"""
    unzip_from = Path(args[0]).expanduser().resolve()
    unzip_to = Path.cwd()
    if not unzip_from: raise FileNotFoundError(f"unzip: cannot unzip '{unzip_from.name}': No such file or directory")
    with zipfile.ZipFile(unzip_from) as bash_zip:
        bash_zip.extractall(unzip_to)

    return ['']


def tar(args):
    """Архивация через tar"""
    tar_from = Path(args[0]).expanduser().resolve()
    tar_to = Path(args[1]).expanduser().resolve()
    if not tar_from.exists(): raise FileNotFoundError(f"tar: cannot tar '{tar_from.name}': No such file or directory")
    if not tar_to.name.endswith('.tar.gz'): tar_to = tar_to.with_suffix('.tar.gz')
    with tarfile.open(tar_to, 'w') as bash_tar: bash_tar.add(tar_from, arcname=tar_to.name)

    return ['']


def untar(args):
    """Открытие zip архива"""
    untar_from = Path(args[0]).expanduser().resolve()
    untar_to = Path.cwd()
    if not untar_from: raise FileNotFoundError(f"untar: cannot untar '{untar_from.name}': No such file or directory")
    with tarfile.open(untar_from, "r:*") as bash_tar: bash_tar.extractall(path=untar_to)

    return ['']

def grep(args):
    """Поиск подстроки в файле"""
    path = Path(args[-1]).expanduser().resolve()
    if not path.exists(): raise FileNotFoundError(f"grep: cannot grep '{path.name}': No such file or directory")
    r_flag = args[0] == '-r'
    if r_flag: args.remove('-r')
    i_flag = args[0] == '-i'
    if i_flag: args.remove('-i'); i_flag = re.IGNORECASE
    pattern = args[0]
    try: pattern = re.compile(pattern, i_flag)
    except Exception as e: raise ValueError(e)
    res = []
    if path.is_file(): files = [path]
    elif path.is_dir():
        if r_flag: files = path.rglob('*')
        else: files = path.glob('*')
    else: raise ValueError(f'grep: {path.name} not a file or a directory')

    for file in files:
        if file.is_file():
            with file.open('r', encoding='utf-8') as f:
                res = [line.strip() for line in f if pattern.search(line)]

    return res


def history(args):
    """Вспомогательная функция истории, которая записывает все выполненные команды в один файл"""
    num = int(args[0]) if args else 10**10
    res = []
    if len(args) > 1: raise ValueError('history: too many arguments')
    history_file = Path(".history").expanduser().resolve()
    if not history_file.exists(): raise FileNotFoundError(f"history: cannot history '{history_file.name}' is empty")
    with history_file.open('r', encoding='utf-8') as f: lines = f.readlines()
    lines = [line.strip() for line in lines if line]
    if not args or num > len(lines): num = len(lines)
    for i in lines[::-1][:num][::-1]:
        res.append(i)

    return res


def undo(args):
    """Выполнение обратной команды"""
    with HISTORY_FILE.open('r+', encoding='utf-8') as f:
        c = str(f.readlines()[-2])
        if 'cp' in c:
            command = c.split()[-1]
            if len(command[command.index('-r')+1:]) > 2: raise ValueError("undo: last command had too many arguments for undo")
            rm([command])
            f.seek(0, 2)
            pos = f.tell()
            while pos:
                pos -= 1
                f.seek(pos)
                char = f.read(1)
                if char == b'\n': break
            f.truncate(pos)
        elif 'mv' in c:
            lst = c.split()
            if len(lst) > 4: raise ValueError("undo: last command had too many arguments for undo")
            r_to_cwd = mv_from_path
            cd([lst[-1]])
            command = lst[2]
            mv([command, mv_from_path])
            cd([r_to_cwd])
            f.seek(0, 2)
            pos = f.tell()
            while pos:
                pos -= 1
                f.seek(pos)
                char = f.read(1)
                if char == b'\n': break
            f.truncate(pos)
        elif 'rm' in c:
            command = c.split()[-1]
            if len(command[command.index('-r')+1:]) > 2: raise ValueError("undo: last command had too many arguments for undo")
            cd(['.trash'])
            mv([Path(command), rm_from_path])
            cd(['..'])
            f.seek(0, 2)
            pos = f.tell()
            while pos:
                pos -= 1
                f.seek(pos)
                char = f.read(1)
                if char == b'\n': break
            f.truncate(pos)
        else: raise ValueError('last command not from [mv, rm, cp]')

    return ['']




command_dict ={
    'ls': ls,
    'cd': cd,
    'cat': cat,
    'cp': cp,
    'mv': mv,
    'rm': rm,
    'zip': zip,
    'unzip': unzip,
    'tar': tar,
    'untar': untar,
    'grep': grep,
    'history': history,
    'undo': undo
}


def solving(command):
    if command[0] not in command_dict: raise ValueError('incorrect command')
    if command[0] in ['cd', 'cat', 'cp', 'mv', 'rm', 'zip', 'tar', 'unzip', 'untar'] and len(command) == 1:
        raise ValueError(f'{command[0]}: missing file operand')
    args = command[1:]
    command = command[0]
    return command_dict[command](args)
