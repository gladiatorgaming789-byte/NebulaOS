#!/usr/bin/python3
"""Nebula Settings: original control-center surface backed by installed tools."""
from __future__ import annotations
import os
import shutil
import subprocess
import gi
from nebula_settings_backend import system_summary

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

BG = "#10111b"
PANEL = "#1a1c2b"
ACCENT = "#8b7cff"
TEXT = "#f2f3ff"
MUTED = "#a4a8c2"
CSS = f"""
window, .background {{ background: {BG}; color: {TEXT}; }}
headerbar, .panel {{ background: {PANEL}; color: {TEXT}; border: 0; }}
button {{ background: #25283b; color: {TEXT}; border: 1px solid #343750; border-radius: 9px; padding: 9px 12px; }}
button:hover {{ background: #34314f; border-color: {ACCENT}; }}
.title {{ font-size: 22px; font-weight: 700; }}
.subtitle {{ color: {MUTED}; }}
"""

# These actions launch established configuration tools; they do not pretend to
# edit settings when a backend is absent. Arguments are fixed, never user-built.
ACTIONS = [
    ("Network", "Manage wired and Wi-Fi connections", "nm-connection-editor"),
    ("Audio", "Select output/input devices and adjust volume", "pavucontrol"),
    ("Display", "Resolution, scaling, and monitor layout", "xfce4-display-settings"),
    ("Appearance", "Themes, fonts, and interface appearance", "xfce4-appearance-settings"),
    ("Power", "Power behavior and idle settings", "xfce4-power-manager-settings"),
    ("Bluetooth", "Pair and manage Bluetooth devices", "blueman-manager"),
    ("File associations", "Choose default applications", "exo-preferred-applications"),
]



class SettingsWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Nebula Settings")
        self.set_default_size(760, 620)
        self.set_border_width(20)
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(), provider,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.add(root)
        heading = Gtk.Label()
        heading.set_markup('<span size="x-large" weight="bold">⚙ Nebula Settings</span>')
        heading.set_xalign(0)
        root.pack_start(heading, False, False, 0)
        intro = Gtk.Label(label="Control center · settings open the real system tools available on this device")
        intro.set_xalign(0)
        intro.get_style_context().add_class("subtitle")
        intro.set_line_wrap(True)
        root.pack_start(intro, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        grid = Gtk.Grid(column_spacing=12, row_spacing=12)
        scroll.add(grid)
        root.pack_start(scroll, True, True, 0)
        for index, (name, description, executable) in enumerate(ACTIONS):
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            card.set_border_width(12)
            card.get_style_context().add_class("panel")
            title = Gtk.Label(label=name)
            title.set_xalign(0)
            title.get_style_context().add_class("title")
            detail = Gtk.Label(label=description)
            detail.set_xalign(0)
            detail.set_line_wrap(True)
            detail.set_max_width_chars(30)
            detail.get_style_context().add_class("subtitle")
            button = Gtk.Button(label="Open settings" if shutil.which(executable) else "Unavailable")
            button.set_sensitive(bool(shutil.which(executable)))
            button.connect("clicked", self.launch_action, executable, name)
            card.pack_start(title, False, False, 0)
            card.pack_start(detail, True, True, 0)
            card.pack_end(button, False, False, 0)
            grid.attach(card, index % 2, index // 2, 1, 1)

        system_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        system_card.set_border_width(12)
        system_card.get_style_context().add_class("panel")
        sys_title = Gtk.Label(label="System information")
        sys_title.set_xalign(0)
        sys_title.get_style_context().add_class("title")
        self.summary = Gtk.Label(label=system_summary())
        self.summary.set_xalign(0)
        self.summary.set_selectable(True)
        self.summary.set_line_wrap(False)
        refresh = Gtk.Button(label="Refresh system information")
        refresh.connect("clicked", lambda _b: self.summary.set_text(system_summary()))
        system_card.pack_start(sys_title, False, False, 0)
        system_card.pack_start(self.summary, False, False, 0)
        system_card.pack_start(refresh, False, False, 0)
        root.pack_start(system_card, False, False, 0)

    def launch_action(self, _button, executable, name):
        if not shutil.which(executable):
            self.show_error(f"{name} settings are unavailable because {executable} is not installed.")
            return
        try:
            subprocess.Popen([executable], close_fds=True, start_new_session=True)
        except OSError as exc:
            self.show_error(f"Could not open {name} settings: {exc}")

    def show_error(self, message):
        dialog = Gtk.MessageDialog(transient_for=self, flags=0,
                                   message_type=Gtk.MessageType.ERROR,
                                   buttons=Gtk.ButtonsType.CLOSE,
                                   text="Nebula Settings")
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()


if __name__ == "__main__":
    window = SettingsWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
