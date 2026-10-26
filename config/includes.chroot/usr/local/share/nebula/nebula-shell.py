#!/usr/bin/python3
"""Small original Nebula Desktop launch surface (GTK 3, Wayland-capable)."""
import os
import subprocess
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib

ACCENT = "#8b7cff"
BG = "#10111b"
PANEL = "#1a1c2b"
TEXT = "#f2f3ff"
MUTED = "#a4a8c2"

CSS = f"""
window, .background {{ background: {BG}; color: {TEXT}; }}
headerbar, .panel {{ background: {PANEL}; color: {TEXT}; border: 0; }}
button {{ background: #25283b; color: {TEXT}; border: 1px solid #343750; border-radius: 10px; padding: 9px 12px; }}
button:hover {{ background: #34314f; border-color: {ACCENT}; }}
.title {{ font-size: 22px; font-weight: 700; color: {TEXT}; }}
.subtitle {{ color: {MUTED}; }}
"""

class NebulaShell(Gtk.Window):
    def __init__(self):
        super().__init__(title="Nebula Desktop")
        self.set_default_size(880, 560)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(18)
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.add(root)
        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title = Gtk.Label(); title.set_markup('<span size="x-large" weight="bold">✦ Nebula Desktop</span>'); title.set_xalign(0)
        top.pack_start(title, True, True, 0)
        clock = Gtk.Label(label="NebulaForge OS · Live session")
        clock.get_style_context().add_class("subtitle")
        top.pack_end(clock, False, False, 0)
        root.pack_start(top, False, False, 0)

        search = Gtk.SearchEntry()
        search.set_placeholder_text("Search applications…")
        search.connect("search-changed", self.on_search)
        root.pack_start(search, False, False, 0)

        self.apps_box = Gtk.FlowBox()
        self.apps_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.apps_box.set_max_children_per_line(4)
        self.apps_box.set_min_children_per_line(2)
        self.apps_box.set_column_spacing(12)
        self.apps_box.set_row_spacing(12)
        scroll = Gtk.ScrolledWindow(); scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.apps_box)
        root.pack_start(scroll, True, True, 0)

        quick = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        for label, command in (("Files", ["nebula-files"]), ("Terminal", ["x-terminal-emulator"]),
                               ("Settings", ["nebula-settings"]), ("Gaming", ["forge", "game", "list"]),
                               ("Developer", ["x-terminal-emulator"])):
            b = Gtk.Button(label=label); b.connect("clicked", self.launch_command, command)
            quick.pack_start(b, True, True, 0)
        root.pack_end(quick, False, False, 0)
        self.app_buttons = []
        self.populate_apps()

    def populate_apps(self):
        for child in self.apps_box.get_children(): self.apps_box.remove(child)
        self.app_buttons.clear()
        apps = Gio.AppInfo.get_all()
        apps = sorted((a for a in apps if a.should_show()), key=lambda a: a.get_display_name().lower())
        for app in apps[:160]:
            button = Gtk.Button()
            button.set_size_request(165, 74)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            name = Gtk.Label(label=app.get_display_name()); name.set_line_wrap(True)
            box.pack_start(name, True, True, 0)
            button.add(box)
            button.connect("clicked", lambda _b, item=app: self.launch_app(item))
            self.apps_box.add(button)
            self.app_buttons.append((button, app.get_display_name().lower()))
        self.show_all()

    def on_search(self, entry):
        query = entry.get_text().strip().lower()
        for button, name in self.app_buttons:
            button.set_visible(not query or query in name)

    def launch_app(self, app):
        try:
            app.launch([], None)
        except GLib.Error as exc:
            self.show_error(f"Could not launch {app.get_display_name()}: {exc.message}")

    def launch_command(self, _button, command):
        try:
            subprocess.Popen(command, close_fds=True, start_new_session=True)
        except OSError as exc:
            self.show_error(f"Could not start {command[0]}: {exc}")

    def show_error(self, message):
        dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.ERROR,
                                   buttons=Gtk.ButtonsType.CLOSE, text="Nebula Desktop")
        dialog.format_secondary_text(message); dialog.run(); dialog.destroy()

if __name__ == "__main__":
    win = NebulaShell(); win.connect("destroy", Gtk.main_quit); win.show_all(); Gtk.main()
