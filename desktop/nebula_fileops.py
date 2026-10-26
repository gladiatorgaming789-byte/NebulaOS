"""Filesystem operations shared by Nebula Files and its offline tests.

Operations refuse overwrites and reject directory destinations inside their source.
They never elevate privileges and preserve symlinks instead of following them.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path


def validate_name(name: str) -> str:
    if not name or name in {".", ".."} or "/" in name or "\x00" in name or "\\" in name:
        raise ValueError("Name must be non-empty and cannot contain path separators.")
    return name


def _reject_self_nesting(source: Path, destination: Path) -> None:
    """Reject copying/moving a directory into itself or any descendant."""
    if source.is_symlink() or not source.is_dir():
        return
    source_real = source.resolve(strict=True)
    destination_real = destination.resolve(strict=False)
    try:
        destination_real.relative_to(source_real)
    except ValueError:
        return
    raise ValueError(f"Destination must not be inside source directory: {destination}")


def _copy_regular_file_no_overwrite(source: Path, destination: Path) -> None:
    """Copy to a temporary sibling, then atomically publish without overwriting."""
    destination.parent.mkdir(parents=False, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".copy-tmp",
                                          dir=str(destination.parent))
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        shutil.copy2(source, temporary, follow_symlinks=False)
        # Hard-link creation fails atomically if another process created destination.
        os.link(temporary, destination, follow_symlinks=False)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def copy_item(source: Path, destination: Path) -> None:
    source, destination = Path(source), Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Destination already exists: {destination}")
    if not source.exists() and not source.is_symlink():
        raise FileNotFoundError(source)
    _reject_self_nesting(source, destination)
    if source.is_symlink():
        # symlink() itself atomically refuses an already-existing destination.
        os.symlink(os.readlink(source), destination)
    elif source.is_dir():
        # copytree creates the destination directory exclusively; it fails if it
        # already exists, including when a concurrent process wins the race.
        shutil.copytree(source, destination, symlinks=True)
    else:
        _copy_regular_file_no_overwrite(source, destination)


def _rename_no_replace(source: Path, destination: Path) -> bool:
    """Use Linux renameat2(RENAME_NOREPLACE) when available; return False otherwise."""
    try:
        import ctypes
        libc = ctypes.CDLL(None, use_errno=True)
        renameat2 = libc.renameat2
    except (AttributeError, OSError):
        return False
    renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    renameat2.restype = ctypes.c_int
    result = renameat2(-100, os.fsencode(source), -100, os.fsencode(destination), 1)  # AT_FDCWD, RENAME_NOREPLACE
    if result == 0:
        return True
    error = ctypes.get_errno()
    if error in (17,):  # EEXIST
        raise FileExistsError(error, os.strerror(error), str(destination))
    if error in (38, 22, 95):  # ENOSYS, EINVAL, EOPNOTSUPP
        return False
    if error == 18:  # EXDEV
        return False
    raise OSError(error, os.strerror(error), str(destination))


def move_item(source: Path, destination: Path) -> None:
    source, destination = Path(source), Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Destination already exists: {destination}")
    if not source.exists() and not source.is_symlink():
        raise FileNotFoundError(source)
    _reject_self_nesting(source, destination)
    if _rename_no_replace(source, destination):
        return
    # Cross-filesystem fallback is copy-then-delete. copy_item has exclusive
    # destination creation; the source remains intact if copying fails.
    copy_item(source, destination)
    delete_item(source)


def delete_item(path: Path) -> None:
    path = Path(path)
    if path.is_symlink() or not path.is_dir():
        path.unlink()
    else:
        shutil.rmtree(path)


def format_size(n: int) -> str:
    value = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return str(n)
