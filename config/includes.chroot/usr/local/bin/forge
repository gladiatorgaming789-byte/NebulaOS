#!/usr/bin/python3
"""NebulaForge's safe, first-party system CLI."""
from __future__ import annotations
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

VERSION = "0.1.0-dev"


def run_readonly(argv: list[str]) -> tuple[int, str]:
    try:
        p = subprocess.run(argv, check=False, text=True, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=15, env={**os.environ, "LC_ALL": "C"})
        return p.returncode, p.stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)


def system_info(_: argparse.Namespace) -> int:
    info = {"os": "NebulaForge OS", "version": VERSION,
            "kernel": platform.release(), "architecture": platform.machine(),
            "python": platform.python_version(), "uid": os.getuid()}
    for key, command in (("init", ["ps", "-p", "1", "-o", "comm="]),
                         ("disk_root", ["df", "-h", "/"]),
                         ("memory", ["free", "-h"])):
        code, output = run_readonly(command)
        info[key] = output if code == 0 else "unavailable"
    print(json.dumps(info, indent=2))
    return 0


def system_health(_: argparse.Namespace) -> int:
    checks = []
    for label, command in (("systemd", ["systemctl", "is-system-running"]),
                           ("network-manager", ["systemctl", "is-active", "NetworkManager"]),
                           ("disk", ["df", "-h", "/"]),
                           ("vulkan", ["sh", "-c", "command -v vulkaninfo >/dev/null 2>&1"])):
        code, output = run_readonly(command)
        checks.append({"check": label, "ok": code == 0, "details": output or ("available" if code == 0 else "not available")})
    print(json.dumps(checks, indent=2))
    # systemd and root-disk readability are required; network and Vulkan are optional
    # capabilities on some installs, so report them without failing overall health.
    required = {"systemd", "disk"}
    failed_required = [item["check"] for item in checks if item["check"] in required and not item["ok"]]
    return 1 if failed_required else 0


def game_list(_: argparse.Namespace) -> int:
    roots = [Path.home() / ".local/share/nebula/games", Path.home() / "Games"]
    found = []
    for root in roots:
        if root.is_dir():
            for p in sorted(root.glob("**/*.desktop")):
                found.append(str(p))
            for p in sorted(root.glob("**/*.exe")):
                found.append(str(p))
    print("\n".join(found) if found else "No imported games found. Import an existing game from Nebula Desktop.")
    return 0


def package_search(args: argparse.Namespace) -> int:
    if not args.query.strip() or len(args.query) > 120:
        print("forge: query must contain 1–120 characters", file=sys.stderr)
        return 2
    # The query is one argument, never shell-expanded. apt-cache is read-only.
    code, output = run_readonly(["apt-cache", "search", "--", args.query])
    print(output or "No package results (the package index may be unavailable).")
    return code


def logs(args: argparse.Namespace) -> int:
    if os.getuid() != 0 and args.system:
        print("forge: system logs may require administrator privileges; retry with sudo explicitly", file=sys.stderr)
        return 2
    command = ["journalctl", "--no-pager", "-n", str(args.lines)]
    if args.system:
        command.append("--system")
    else:
        command.append("--user")
    code, output = run_readonly(command)
    print(output)
    return code


def bounded_lines(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if not 1 <= number <= 1000:
        raise argparse.ArgumentTypeError("must be between 1 and 1000")
    return number


def unavailable(_: argparse.Namespace) -> int:
    print("This feature is not implemented in this development build. No changes were made.", file=sys.stderr)
    return 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forge", description="NebulaForge OS system tools")
    parser.add_argument("--version", action="version", version=f"forge {VERSION}")
    top = parser.add_subparsers(dest="area", required=True)
    system = top.add_parser("system", help="inspect system status")
    syscmd = system.add_subparsers(dest="action", required=True)
    p = syscmd.add_parser("info", help="show system information"); p.set_defaults(func=system_info)
    p = syscmd.add_parser("health", help="run read-only health checks"); p.set_defaults(func=system_health)
    game = top.add_parser("game", help="game library tools")
    gamecmd = game.add_subparsers(dest="action", required=True)
    p = gamecmd.add_parser("list", help="list imported game shortcuts and executables"); p.set_defaults(func=game_list)
    p = gamecmd.add_parser("launch", help="launch an imported game (not yet implemented)"); p.set_defaults(func=unavailable)
    p = gamecmd.add_parser("doctor", help="diagnose game compatibility (not yet implemented)"); p.set_defaults(func=unavailable)
    package = top.add_parser("package", help="native package tools")
    pkgcmd = package.add_subparsers(dest="action", required=True)
    p = pkgcmd.add_parser("search", help="search configured APT package indexes"); p.add_argument("query"); p.set_defaults(func=package_search)
    p = pkgcmd.add_parser("install", help="install packages (not yet implemented)"); p.set_defaults(func=unavailable)
    dev = top.add_parser("dev", help="developer toolchain tools")
    devcmd = dev.add_subparsers(dest="action", required=True)
    p = devcmd.add_parser("setup", help="configure development tools (not yet implemented)"); p.set_defaults(func=unavailable)
    p = top.add_parser("update", help="system updates (not yet implemented)"); p.set_defaults(func=unavailable)
    p = top.add_parser("recovery", help="recovery tools (not yet implemented)"); p.set_defaults(func=unavailable)
    p = top.add_parser("logs", help="inspect logs")
    p.add_argument("--system", action="store_true", help="read system rather than user journal")
    p.add_argument("--lines", type=bounded_lines, default=100)
    p.set_defaults(func=logs)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))

if __name__ == "__main__":
    raise SystemExit(main())
