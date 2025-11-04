import shutil
from os import *
from pathlib import *
import stat
import zipfile
import tarfile


def ls(args):
    l_flag = '-l' in args
    paths = [arg for arg in args if arg != '-l']
    path = Path(paths[0]) if paths else Path.cwd()
    if not path.exists(): raise FileNotFoundError(f"ls: {path.name}: No such file or directory")
    if not l_flag: return [entry.name for entry in path.iterdir()]
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
    if not path.exists(): raise FileNotFoundError(f"cd: {path.name}: No such file or directory")
    if not path.is_dir(): raise IsADirectoryError(f"cd: Incorrect command")
    chdir(path)
    return ['']


def cat(args):
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
                if copy_from.is_dir(): raise ValueError(f"cp: -r not specified; omitting directory {copy_from.name}")
                else: shutil.copy(copy_from, copy_to)
    return ['']


def mv(args):
    if len(args) < 2: raise ValueError(f"mv: missing destination file operand after '{args[0]}'")
    if len(args) >= 2:
        mv_to = args[-1]
        for i in args[:-1]:
            mv_from = i
            if not Path(mv_from).expanduser().resolve().exists(): raise FileNotFoundError(f"mv: {mv_from.name}: No such file or directory")
            try: shutil.move(str(mv_from), str(mv_to))
            except PermissionError: raise PermissionError(f"mv: cannot move '{mv_from.name}' to '{mv_to.name}': Permission denied")
            except Exception: raise ValueError('some error with command mv')
    return ['']


def rm(args):
    r_flag = args[0] == '-r'
    if r_flag:
        for obj in args[1:]:
            path = Path(obj).expanduser().resolve()
            if not path.exists(): raise FileNotFoundError(f"rm: cannot remove '{path.name}': No such file or directory")
            if path.is_file(): path.unlink()
            else:
                if input(f"rm: remove directory '{path.name}'? ") == 'y': shutil.rmtree(path)
                else: continue
    else:
        for obj in args:
            path = Path(obj).expanduser().resolve()
            if not path.exists(): raise FileNotFoundError(f"rm: cannot remove '{path.name}': No such file or directory"); continue
            if path.is_file(): path.unlink()
            else: raise IsADirectoryError(f"rm: cannot remove '{path.name}': Is a directory")

    return ['']


def zip(args):
    zip_from = Path(args[0]).expanduser().resolve()
    zip_to = Path(args[1]).expanduser().resolve()
    if not zip_from.exists(): raise FileNotFoundError(f"zip: cannot zip '{zip_from.name}': No such file or directory")
    if zip_to.suffix != '.zip': zip_to = zip_to.with_suffix('.zip')
    with zipfile.ZipFile(zip_to, 'w', zipfile.ZIP_DEFLATED) as bash_zip:
        if zip_from.is_dir():
            for file in zip_from.rglob('*'): bash_zip.write(file, file.relative_to(zip_from))
        else: bash_zip.write(zip_from, zip_from.name)
    return ['']

def unzip(args):
    unzip_from = Path(args[0]).expanduser().resolve()
    unzip_to = Path.cwd()
    if not unzip_from: raise FileNotFoundError(f"unzip: cannot unzip '{unzip_from.name}': No such file or directory")
    with zipfile.ZipFile(unzip_from) as bash_zip:
        bash_zip.extractall(unzip_to)
    return ['']


def tar(args):
    tar_from = Path(args[0]).expanduser().resolve()
    tar_to = Path(args[1]).expanduser().resolve()
    if not tar_from.exists(): raise FileNotFoundError(f"tar: cannot tar '{tar_from.name}': No such file or directory")
    if not tar_to.name.endswith('.tar.gz'): tar_to = tar_to.with_suffix('.tar.gz')
    with tarfile.open(tar_to, 'w') as bash_tar: bash_tar.add(tar_from, arcname=tar_to.name)
    return ['']


def untar(args):
    untar_from = Path(args[0]).expanduser().resolve()
    untar_to = Path.cwd()
    if not untar_from: raise FileNotFoundError(f"untar: cannot untar '{untar_from.name}': No such file or directory")
    with tarfile.open(untar_from, "r:*") as bash_tar: bash_tar.extractall(path=untar_to)
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
    'untar': untar
}


def solving(command):
    if command[0] not in command_dict: raise ValueError('incorrect command')
    if command[0] in ['cd', 'cat', 'cp', 'mv', 'rm', 'zip', 'tar', 'unzip', 'untar'] and len(command) == 1: raise ValueError(f'{command[0]}: missing file operand')
    args = command[1:]
    command = command[0]
    return command_dict[command](args)
