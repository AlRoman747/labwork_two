import shutil
from os import *
from pathlib import *
import stat

def ls(args):
    long_flag = '-l' in args
    paths = [arg for arg in args if arg != '-l']
    path = Path(paths[0]) if paths else Path.cwd()
    if not path.exists():
        raise FileNotFoundError(f"ls: {args[0]}: No such file or directory")
    if not long_flag:
        return [entry.name for entry in path.iterdir()]
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
    if len(args) > 1: raise ValueError("cd: too many arguments")
    path = Path(args[0]).expanduser().resolve()
    if not path.exists(): raise FileNotFoundError(f"cd: {args[0]}: No such file or directory")
    chdir(path)
    return ['']

def cat(args):
    info_from_files = []
    if not(args): raise ValueError("cat: Incorrect command")
    for file in args:
        path = Path(file).expanduser().resolve()
        if not path.exists(): info_from_files.append(f"cat: {file}: No such file or directory"); continue
        if path.is_dir(): info_from_files.append(f"cat: {file}: Is a directory"); continue
        inform = path.read_text(encoding="utf-8")
        info_from_files.append(inform)
    return info_from_files


def cp(args):
    if len(args) < 2: raise ValueError("cp: Incorrect command")
    copy_to = Path(args[-1]).expanduser().resolve()
    r_flag = args[0] == '-r'
    if copy_to.is_dir():
        if r_flag:
            for odj in args[1:-1]:
                copy_from = Path(odj).expanduser().resolve()
                if copy_from.is_dir(): shutil.copytree(copy_from, copy_to, dirs_exist_ok=True)
                else: shutil.copy(copy_from, copy_to)
        else:
            for odj in args[:-1]:
                copy_from = Path(odj).expanduser().resolve()
                if copy_from.is_dir(): raise ValueError(f"cp: -r not specified; omitting directory {copy_from}")
                else: shutil.copy(copy_from, copy_to)
    return ['']



def mv(args):
    if len(args) < 2: raise ValueError(f"mv: missing destination file operand after '{args[0]}'")
    if len(args) == 2:
        mv_from = args[0]
        mv_to = args[1]
        if not Path(mv_from).expanduser().resolve().exists(): raise FileNotFoundError(f"mv: {mv_from}: No such file or directory")
        try: shutil.move(str(mv_from), str(mv_to))
        except PermissionError: raise PermissionError(f"mv: cannot move '{mv_from}' to '{mv_to}': Permission denied")
        except Exception: raise ValueError('some error with command mv')
    return ['']

def rm(args):
    r_flag = args[0] == '-r'
    if r_flag:
        for obj in args[1:]:
            path = Path(obj).expanduser().resolve()
            if not path.exists(): raise FileNotFoundError(f"rm: cannot remove '{args[0]}': No such file or directory")
            if path.is_file(): path.unlink()
            else:
                if input(f"rm: remove directory '{obj}'? ") == 'y': shutil.rmtree(path)
                else: continue
    else:
        for obj in args:
            path = Path(obj).expanduser().resolve()
            if not path.exists(): raise FileNotFoundError(f"rm: cannot remove '{args[0]}': No such file or directory"); continue
            if path.is_file(): path.unlink()
            else: raise IsADirectoryError(f"rm: cannot remove '{obj}': Is a directory")

    return ['']



command_dict ={
    'ls': ls,
    'cd': cd,
    'cat': cat,
    'cp': cp,
    'mv': mv,
    'rm': rm
}


def solving(commands):
    args = commands[1:]
    command = commands[0]
    return command_dict[command](args)
