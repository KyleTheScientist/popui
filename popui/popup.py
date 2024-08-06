from ahk import AHK
from ahk.directives import NoTrayIcon
from dearpygui import dearpygui as dpg
from time import time
from typing import Callable
import tkinter as tk
import threading
from . import keys


class Popup:

    ON_MOUSE = 0
    ON_APP = 1
    ON_SCREEN = 2

    KEY_PRESS = 0
    KEY_DOWN = 1
    KEY_UP = 2

    def __init__(self,
                 hotkey: str,
                 build: Callable[['Popup', any], None],
                 *,
                 anchor: int = ON_MOUSE,
                 appplication: str = None,
                 **viewport_args: any):
        self.ahk = AHK(directives=[NoTrayIcon(apply_to_hotkeys_process=True)])
        self.ahk.add_hotkey(hotkey, callback=self.toggle)
        self.gui = dpg
        self.viewport_args = viewport_args
        self.application = appplication
        self.anchor_point = anchor
        self.build = build
        self.cooldown = 0
        self.open = False
        self.toggle_event = threading.Event()
        self.quit_event = threading.Event()
        self.scheduled_action = None

    def __enter__(self):
        dpg.push_container_stack(self.root)
        return dpg

    def __exit__(self, exc_type, exc_val, exc_tb):
        dpg.pop_container_stack()

    def show(self):
        dpg.create_context()
        dpg.setup_dearpygui()

        with dpg.window() as window:
            self.root = window
            dpg.set_primary_window(window, True)
        dpg.create_viewport(**self.viewport_args)
        dpg.set_viewport_always_top(True)
        with dpg.handler_registry():
            dpg.add_key_press_handler(key=keys.ESCAPE, callback=self.toggle)

        self.anchor()
        self.build(self) # Add user content
        dpg.show_viewport()
        dpg.set_frame_callback(dpg.get_frame_count() + 1, callback=self.focus)
        self.open = True
        dpg.start_dearpygui()
        dpg.destroy_context()

    def hide(self):
        dpg.stop_dearpygui()
        self.open = False

    def focus(self):
        title = dpg.get_viewport_title()
        self.ahk.find_window_by_class(title).activate()

    def anchor(self):
        viewport_width = dpg.get_viewport_width()
        viewport_height = dpg.get_viewport_height()
        if self.anchor_point == self.ON_MOUSE:
            x, y = self.ahk.get_mouse_position()
            off_x, off_y = viewport_width / 2, viewport_height / 2
            dpg.set_viewport_pos((x - off_x, y - off_y))
        elif self.anchor_point == self.ON_APP:
            active_window = self.ahk.get_active_window()
            x, y, w, h = active_window.get_position()
            off_x, off_y = viewport_width / 2, viewport_height / 2
            dpg.set_viewport_pos((x + w/2 - off_x, y + h/2 - off_y))
        elif self.anchor_point == self.ON_SCREEN:
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

            x = int(screen_width / 2 - viewport_width / 2)
            y = int(screen_height / 2 - viewport_height / 2)
            dpg.set_viewport_pos((x, y))

    def application_match(self):
        if not self.application:
            return True
        active_window = self.ahk.get_active_window()
        if ' ' not in self.application:
            value = active_window.title
            application = self.application
        else:
            type_, application = self.application.split(' ')
            if type_ == 'ahk_class':
                value = active_window.get_class()
            elif type_ == 'ahk_exe':
                value = active_window.get_exe()
            else:
                raise ValueError(f"Invalid application type: {self.application}")
        return application == value

    def toggle(self):
        if time() < self.cooldown:
            return
        self.cooldown = time() + 0.1

        if self.open:
            self.hide()
        elif self.application_match():
            self.show()

    def block(self):
        self.ahk.start_hotkeys()
        while True:
            try:
                self.ahk.get_mouse_position()
                if self.toggle_event.is_set():
                    self.toggle_event.clear()
                    self.toggle()
                if self.scheduled_action:
                    self.scheduled_action()
                    self.scheduled_action = None
                if self.quit_event.is_set():
                    break
            except KeyboardInterrupt:
                break
        self.ahk.stop_hotkeys()

    def quit(self):
        if self.open:
            self.hide()
        self.quit_event.set()

    def schedule_toggle(self):
        self.toggle_event.set()

    def schedule(self, callback):
        def callback_():
            self.schedule_toggle()
            self.scheduled_action = callback
        return callback_

    def if_active(self, element: int, callback):
        def callback_():
            if dpg.is_item_visible(element):
                print('Shortcut pressed')
                callback()
        return callback_

    def add_button(self, label: str, callback: Callable, close=True, **kwargs):
        if close:
            callback = self.schedule(callback)

        shortcut = kwargs.pop('shortcut', None)
        button = dpg.add_button(label=label,
                                callback=callback,
                                **kwargs)

        if shortcut:
            callback = self.if_active(button, callback)
            with dpg.handler_registry():
                dpg.add_key_press_handler(key=keys.KEY_CODES[str(shortcut)], callback=callback)

        return button

    def add_keybind(self, key: str|int, callback: Callable, action: int = KEY_PRESS):
        if action == self.KEY_PRESS:
            handler = dpg.add_key_press_handler
        elif action == self.KEY_DOWN:
            handler = dpg.add_key_down_handler
        elif action == self.KEY_UP:
            handler = dpg.add_key_release_handler
        else:
            raise ValueError(f"Invalid action: {action}")

        with dpg.handler_registry():
            if isinstance(key, str):
                key = keys.KEY_CODES[key.lower()]
            handler(key=key, callback=callback)

if __name__ == '__main__':
    def build(popup: Popup):
        dpg.add_button(label='Close', callback=popup.toggle, parent=popup.root)
    Popup('^Space', build).block()
