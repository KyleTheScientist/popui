import tkinter as tk
import threading
import faulthandler

from . import keys
from ahk import AHK
from ahk.directives import NoTrayIcon
from dearpygui import dearpygui as dpg
from time import time
from typing import Callable, Iterable


faulthandler.enable()


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
        '''
        :param hotkey: The keybind that toggles the popup window
        :param build: The function that builds the popup window
        :param anchor: The anchor point for the popup window (Popup.ON_MOUSE, Popup.ON_APP, Popup.ON_SCREEN)
        :param appplication: The application to anchor the popup window to, as an AHK title
        :param viewport_args: Additional arguments for the Dear PyGUI viewport
        '''
        self.ahk = AHK(directives=[NoTrayIcon(apply_to_hotkeys_process=True)])
        self.ahk.add_hotkey(hotkey, callback=self.toggle)
        self.gui = dpg
        self.application = appplication
        self.anchor_point = anchor

        # Dimensions
        self.width = viewport_args.pop('width', 400)
        self.height = viewport_args.pop('height', 300)
        viewport_args['width'] = self.width
        viewport_args['height'] = self.height
        self.viewport_args = viewport_args

        self.build = build
        self.cooldown = 0
        self.built = False
        self.open = False
        self.quit_event = threading.Event()
        self.scheduled_action = None
        self.scheduled_keybinds = []

    def setup(self):
        '''
        Builds the popup window for the first time
        '''
        dpg.create_context()
        dpg.setup_dearpygui()

        with dpg.window() as window:
            self.root = window
            dpg.set_primary_window(window, True)
        dpg.create_viewport(**self.viewport_args)
        dpg.set_viewport_always_top(True)
        with dpg.handler_registry():
            dpg.add_key_press_handler(key=keys.ESCAPE, callback=self.hide)

        self.build(self) # Add user content
        dpg.show_viewport()
        dpg.set_frame_callback(dpg.get_frame_count() + 1, callback=self.focus)
        title = dpg.get_viewport_title()
        self.window = self.ahk.find_window_by_class(title)
        self.open = True
        self.built = True
        self.anchor()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def close(self):
        '''
        Closes the popup window
        '''
        dpg.stop_dearpygui()
        self.open = False

    def focus(self):
        '''
        Focuses the popup window
        '''
        self.window.activate()

    def anchor(self):
        '''
        Anchors the popup window to the mouse, the active application, or the screen center
        depending on the selected anchor point.
        '''
        viewport_width = dpg.get_viewport_width()
        viewport_height = dpg.get_viewport_height()
        if self.anchor_point == self.ON_MOUSE:
            x, y = self.ahk.get_mouse_position(coord_mode='Screen')
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

    def hide(self):
        '''
        Hides the popup window
        '''
        self.open = False
        self.window.hide()
        for window in self.ahk.list_windows():
            if window.title:
                window.activate()
                break

    def show(self):
        '''
        Shows the popup window
        '''
        self.open = True
        self.anchor()
        self.window.show()
        self.focus()

    def toggle(self):
        '''
        Toggles the popup window visibility
        '''
        if time() < self.cooldown:
            return
        self.cooldown = time() + 0.01

        if self.open:
            self.hide()
        elif self._application_match():
            if self.built:
                self.show()
            else:
                self.setup()


    def block(self):
        '''
        Blocks the main thread and starts the main loop,
        which listens for the keybinding that toggles the popup window
        '''
        self.ahk.start_hotkeys()
        while True:
            try:
                self.ahk.get_mouse_position()
                if self.scheduled_action:
                    self.scheduled_action()
                    self.scheduled_action = None
                if self.scheduled_keybinds:
                    self._evaluate_keybinds()
                if self.quit_event.is_set():
                    break
            except KeyboardInterrupt:
                break
        self.ahk.stop_hotkeys()

    def quit(self):
        '''
        Closes the popup window and breaks the main blocking loop
        '''
        self.close()
        self.quit_event.set()

    def add_button(self, label: str, callback: Callable, close=True, keybind: str|int = None, **kwargs):
        '''
        Adds a button to the popup window

        :param label: The button label
        :param callback: The function to call when the button is pressed
        :param close: Whether to close the window after pressing the button
        :param keybind: A keybind to associate with the button. If the button is visible,
                        the keybind will run the callback
        :param kwargs: Additional Dear PyGUI arguments to pass to the button

        :return: The button ID
        '''
        if close:
            callback = self._hide_before_calling(callback)

        keybind = kwargs.pop('keybind', None)
        parent = kwargs.pop('parent', None) or dpg.top_container_stack() or self.root
        button = dpg.add_button(label=label,
                                callback=callback,
                                parent=parent,
                                **kwargs)

        if keybind:
            callback = self._if_active(button, callback)
            with dpg.handler_registry():
                dpg.add_key_press_handler(key=keys.KEY_CODES[str(keybind)], callback=callback)

        return button

    def add_button_row(self, definitions: list[tuple[str, Callable]], **kwargs):
        '''
        Creates a row of buttons from the list of label-callback pairs

        :param definitions: A list of tuples containing the button label and the callback function
        :param kwargs: Additional Dear PyGUI arguments to pass to the buttons
        '''
        result = []
        width = kwargs.pop('width', -1)
        with dpg.table(header_row=False):
            for _ in range(len(definitions)):
                dpg.add_table_column()
            with dpg.table_row():
                for label, callback in definitions:
                    with dpg.table_cell():
                        button = self.add_button(label, callback, width=width, **kwargs)
                        result.append(button)
        return result

    def _application_match(self):
        if not self.application:
            return True
        active_window = self.ahk.get_active_window()
        if not active_window:
            return False
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

    # Keybinds
    def _convert_to_keycodes(self, key_input: str|int|Iterable[str|int]):
        if isinstance(key_input, str):
            key_input = [keys.KEY_CODES[key_input.lower()]]
        elif isinstance(key_input, int):
            key_input = [key_input]
        elif isinstance(key_input, Iterable):
            key_input = list(key_input)
            for i, modifier in enumerate(key_input):
                if isinstance(modifier, str):
                    key_input[i] = keys.KEY_CODES[modifier.lower()]
        return key_input

    def _evaluate_keybinds(self):
        sorted_keybinds = sorted(self.scheduled_keybinds, key=lambda x: len(x[0]))
        sorted_keybinds.pop()[1]()
        self.scheduled_keybinds.clear()

    def _keybind_callback(self, modifiers: list[int], callback: Callable):
        def callback_():
            if modifiers:
                for modifier in modifiers:
                    if not dpg.is_key_down(modifier):
                        return
            self.scheduled_keybinds.append((modifiers, callback))
        return callback_

    def add_keybind(self, key: str|int, callback: Callable, modifiers: str|int|tuple[str|int] = (), action: int = KEY_PRESS):
        '''
        Adds a keybind to the popup window

        :param key: The key to bind
        :param callback: The function to call when the key is pressed
        :param modifiers: The modifiers to use with the key
        :param action: The key action to listen for (Popup.KEY_PRESS, Popup.KEY_DOWN, Popup.KEY_UP)
        '''
        if action == self.KEY_PRESS:
            handler = dpg.add_key_press_handler
        elif action == self.KEY_DOWN:
            handler = dpg.add_key_down_handler
        elif action == self.KEY_UP:
            handler = dpg.add_key_release_handler
        else:
            raise ValueError(f"Invalid action: {action}")

        modifiers = self._convert_to_keycodes(modifiers)
        with dpg.handler_registry():
            if isinstance(key, str):
                key = keys.KEY_CODES[key.lower()]
            handler(key=key, callback=self._keybind_callback(modifiers, callback))

    # Callbacks and callback wrappers
    def no_op(self):
        '''Does nothing'''
        pass

    def _hide_before_calling(self, callback):
        def callback_():
            self.hide()
            callback()
        return callback_

    def _if_active(self, element: int, callback):
        def callback_():
            if dpg.is_item_visible(element):
                print('Shortcut pressed')
                callback()
        return callback_

    def __enter__(self):
        dpg.push_container_stack(self.root)
        return dpg

    def __exit__(self, exc_type, exc_val, exc_tb):
        dpg.pop_container_stack()
