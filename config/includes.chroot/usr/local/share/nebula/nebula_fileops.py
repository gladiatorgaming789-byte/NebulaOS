"""Filesystem operations shared by Nebula Files and its offline tests.

These helpers never follow a symlink while copying/deleting the link itself.
They do not elevate privileges and never overwrite an existing destination.
"""
from __future__ import annotations
import os
import shutil
from pathlib import Path


def validate_name(name: str) -> str:
    if not name or name in {".", ".."} or "/" in name or "\x00" in name or "\\" in name:
        raise ValueError("Name must be non-empty and cannot contain path separators.")
    return name


def copy_item(source: Path, destination: Path) -> None:
    source, destination = Path(source), Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Destination already exists: {destination}")
    if source.is_symlink():
        os.symlink(os.readlink(source), destination)
    elif source.is_dir():
        shutil.copytree(source, destination, symlinks=True)
    else:
        shutil.copy2(source, destination, follow_symlinks=False)


def move_item(source: Path, destination: Path) -> None:
    source, destination = Path(source), Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Destination already exists: {destination}")
    shutil.move(str(source), str(destination))


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
