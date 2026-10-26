#!/usr/bin/python3
"""Nebula Files: first-party GTK file manager for NebulaForge OS."""
from __future__ import annotations
import os
import stat
import sys
from datetime import datetime
from pathlib import Path

from nebula_fileops import copy_item, delete_item, format_size, move_item, validate_name

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib

BG = "#10111b"
PANEL = "#1a1c2b"
ACCENT = "#8b7cff"
TEXT = "#f2f3ff"
CSS = f"""
window, .background {{ background: {BG}; color: {TEXT}; }}
headerbar, toolbar {{ background: {PANEL}; color: {TEXT}; border: 0; }}
button {{ background: #25283b; color: {TEXT}; border: 1px solid #343750; border-radius: 8px; padding: 6px 10px; }}
button:hover {{ border-color: {ACCENT}; }}
entry, treeview {{ background: #171927; color: {TEXT}; }}
"""

class NebulaFiles(Gtk.Window):
    def __init__(self, start: str | None = None):
        super().__init__(title="Nebula Files")
        self.set_default_size(1000, 650)
        self.set_border_width(12)
        provider = Gtk.CssProvider(); provider.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.current = Path(start or Path.home()).expanduser().resolve()
        if not self.current.is_dir(): self.current = Path.home()
        self.clipboard_paths: list[Path] = []
        self.clipboard_move = False
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8); self.add(root)
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        for label, callback in (("←", self.go_back), ("↑", self.go_parent), ("Home", self.go_home), ("New Folder", self.new_folder), ("Rename", self.rename_selected), ("Copy", self.copy_selected), ("Cut", self.cut_selected), ("Paste", self.paste), ("Delete", self.delete_selected), ("Properties", self.properties)):
            b = Gtk.Button(label=label); b.connect("clicked", lambda _b, fn=callback: fn()); bar.pack_start(b, False, False, 0)
        root.pack_start(bar, False, False, 0)
        nav = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.location = Gtk.Entry(); self.location.set_placeholder_text("Folder path…"); self.location.connect("activate", self.navigate_entry)
        nav.pack_start(self.location, True, True, 0)
        go = Gtk.Button(label="Go"); go.connect("clicked", self.navigate_entry); nav.pack_start(go, False, False, 0)
        self.hidden = Gtk.CheckButton(label="Show hidden files"); self.hidden.connect("toggled", lambda *_: self.refresh())
        nav.pack_start(self.hidden, False, False, 0); root.pack_start(nav, False, False, 0)
        self.store = Gtk.ListStore(str, str, str, str)
        self.view = Gtk.TreeView(model=self.store); self.view.set_headers_clickable(True)
        for idx, title in enumerate(("Name", "Type", "Size", "Modified")):
            renderer = Gtk.CellRendererText(); column = Gtk.TreeViewColumn(title, renderer, text=idx); column.set_resizable(True); column.set_sort_column_id(idx); self.view.append_column(column)
        self.view.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.view.connect("row-activated", self.activate_row)
        scroll = Gtk.ScrolledWindow(); scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC); scroll.add(self.view)
        root.pack_start(scroll, True, True, 0)
        self.status = Gtk.Label(); self.status.set_xalign(0); root.pack_start(self.status, False, False, 0)
        self.refresh()

    def error(self, title: str, message: str):
        dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.CLOSE, text=title)
        dialog.format_secondary_text(message); dialog.run(); dialog.destroy()

    def confirm(self, title: str, message: str) -> bool:
        dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.CANCEL, text=title)
        dialog.add_button("Continue", Gtk.ResponseType.OK); dialog.format_secondary_text(message)
        result = dialog.run() == Gtk.ResponseType.OK; dialog.destroy(); return result

    def refresh(self):
        self.store.clear(); self.location.set_text(str(self.current))
        try:
            entries = list(self.current.iterdir())
            entries.sort(key=lambda p: (not p.is_dir(), p.name.casefold()))
            for path in entries:
                if not self.hidden.get_active() and path.name.startswith("."): continue
                try:
                    st = path.lstat()
                    kind = "Symbolic link" if path.is_symlink() else ("Folder" if path.is_dir() else ("File" if path.is_file() else "Special file"))
                    size = "—" if path.is_dir() or path.is_symlink() else self.format_size(st.st_size)
                    modified = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
                except OSError: kind, size, modified = "Unavailable", "—", "—"
                self.store.append([path.name, kind, size, modified])
            self.status.set_text(f"{self.current}  ·  {len(self.store)} items")
        except OSError as exc: self.error("Cannot open folder", str(exc))


    def selected(self) -> list[Path]:
        model, paths = self.view.get_selection().get_selected_rows()
        return [self.current / model[path][0] for path in paths]

    def go(self, target: Path):
        try:
            target = target.expanduser().resolve(strict=True)
            if not target.is_dir(): raise NotADirectoryError(f"Not a folder: {target}")
            self.current = target; self.refresh()
        except (OSError, RuntimeError) as exc: self.error("Navigation failed", str(exc))

    def go_back(self): self.go(self.current.parent)
    def go_parent(self): self.go(self.current.parent)
    def go_home(self): self.go(Path.home())
    def navigate_entry(self, *_): self.go(Path(self.location.get_text()))

    def activate_row(self, _view, tree_path, _column):
        item = self.current / self.store[tree_path][0]
        try:
            if item.is_dir(): self.go(item)
            else: Gio.AppInfo.launch_default_for_uri(item.as_uri(), None)
        except (OSError, GLib.Error) as exc: self.error("Cannot open item", str(exc))

    def prompt(self, title: str, initial: str = "") -> str | None:
        dialog = Gtk.Dialog(title=title, transient_for=self, flags=0)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL); dialog.add_button("OK", Gtk.ResponseType.OK)
        entry = Gtk.Entry(); entry.set_text(initial); entry.set_activates_default(True); entry.set_hexpand(True)
        entry.set_margin_top(12); entry.set_margin_bottom(12); entry.set_margin_start(12); entry.set_margin_end(12)
        dialog.get_content_area().add(entry); dialog.set_default_response(Gtk.ResponseType.OK); dialog.show_all()
        result = entry.get_text() if dialog.run() == Gtk.ResponseType.OK else None; dialog.destroy()
        if result is not None:
            try: validate_name(result)
            except ValueError as exc: self.error("Invalid name", str(exc)); return None
        return result

    def new_folder(self):
        name = self.prompt("Create folder", "New Folder")
        if name is None: return
        try: (self.current / name).mkdir(); self.refresh()
        except OSError as exc: self.error("Cannot create folder", str(exc))

    def rename_selected(self):
        items = self.selected()
        if len(items) != 1: return self.error("Rename", "Select exactly one item.")
        name = self.prompt("Rename item", items[0].name)
        if name is None or name == items[0].name: return
        try:
            target = items[0].with_name(name)
            if target.exists() or target.is_symlink(): raise FileExistsError(f"Destination already exists: {target.name}")
            items[0].rename(target); self.refresh()
        except OSError as exc: self.error("Rename failed", str(exc))

    def copy_selected(self):
        self.clipboard_paths = self.selected(); self.clipboard_move = False
        self.status.set_text(f"Copied {len(self.clipboard_paths)} item(s). Navigate to a destination and choose Paste.")
    def cut_selected(self):
        self.clipboard_paths = self.selected(); self.clipboard_move = True
        self.status.set_text(f"Marked {len(self.clipboard_paths)} item(s) to move. Navigate to a destination and choose Paste.")

    def paste(self):
        if not self.clipboard_paths: return
        try:
            for src in self.clipboard_paths:
                dest = self.current / src.name
                if src.resolve() == dest.resolve(strict=False): continue
                if dest.exists() or dest.is_symlink(): raise FileExistsError(f"Destination already exists: {dest}")
                if self.clipboard_move: move_item(src, dest)
                else: copy_item(src, dest)
            if self.clipboard_move: self.clipboard_paths = []; self.clipboard_move = False
            self.refresh()
        except OSError as exc: self.error("Paste failed", f"{exc}\nCompleted items may already have been copied or moved."); self.refresh()

    def delete_selected(self):
        items = self.selected()
        if not items: return
        names = "\n".join(p.name for p in items[:8]) + ("\n…" if len(items) > 8 else "")
        if not self.confirm("Delete selected items?", f"This permanently deletes {len(items)} item(s); it does not use a trash folder.\n\n{names}"): return
        try:
            for path in items:
                delete_item(path)
            self.refresh()
        except OSError as exc: self.error("Delete failed", f"{exc}\nSome selected items may already have been deleted."); self.refresh()

    def properties(self):
        items = self.selected()
        if len(items) != 1: return self.error("Properties", "Select exactly one item.")
        path = items[0]
        try:
            st = path.lstat(); mode = stat.filemode(st.st_mode); owner = f"UID {st.st_uid}, GID {st.st_gid}"
            size = self.format_size(st.st_size); modified = datetime.fromtimestamp(st.st_mtime).isoformat(sep=" ", timespec="seconds")
            target = f"\nLink target: {os.readlink(path)}" if path.is_symlink() else ""
            msg = f"Path: {path}\nType: {'symlink' if path.is_symlink() else 'directory' if path.is_dir() else 'file'}\nSize: {size}\nPermissions: {mode} ({oct(stat.S_IMODE(st.st_mode))})\nOwner: {owner}\nModified: {modified}{target}"
            dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.CLOSE, text=path.name)
            dialog.format_secondary_text(msg); dialog.run(); dialog.destroy()
        except OSError as exc: self.error("Properties unavailable", str(exc))

if __name__ == "__main__":
    start = sys.argv[1] if len(sys.argv) > 1 else None
    win = NebulaFiles(start); win.connect("destroy", Gtk.main_quit); win.show_all(); Gtk.main()
