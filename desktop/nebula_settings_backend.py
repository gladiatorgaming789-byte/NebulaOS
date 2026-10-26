"""Read-only backend helpers for Nebula Settings; no GTK dependency."""
from __future__ import annotations
import os
import shutil
import subprocess

COMMANDS = [
    ("Kernel", ["uname", "-r"]),
    ("Architecture", ["uname", "-m"]),
    ("Root filesystem", ["df", "-h", "/"]),
    ("Memory", ["free", "-h"]),
    ("Network", ["nmcli", "-t", "-f", "STATE", "general"]),
]


def system_summary(which=shutil.which, run=subprocess.run) -> str:
    """Return bounded read-only host diagnostics, gracefully handling missing tools."""
    lines = []
    for label, command in COMMANDS:
        if not which(command[0]):
            lines.append(f"{label}: unavailable (missing {command[0]})")
            continue
        try:
            result = run(command, check=False, text=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, timeout=4,
                         env={**os.environ, "LC_ALL": "C"})
            output = result.stdout.strip().splitlines()
            if result.returncode != 0:
                lines.append(f"{label}: unavailable")
            else:
                lines.append(f"{label}: {(output[0] if output else 'no data')[:180]}")
        except (OSError, subprocess.TimeoutExpired):
            lines.append(f"{label}: unavailable")
    return "\n".join(lines)
