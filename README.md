# popui

A Python module for creating GUI popups with Dear PyGui and AutoHotkey on Windows

## Installation

```bash
pip install popui
```

## Usage

To create a popup, first define a function that builds the GUI:

```python
from popui import Popup

def build(popup: Popup):
    # The add_button method creates a button that will close the popup
    # after the callback function is called, by default.
    popup.add_button('Do something', callback=do_something)
    popup.add_button("Do something (Keep window open)",
                        callback=do_something,
                        close=False)

    # The add_keybind method is a convenience method that adds a keybind
    # to the popup window
    popup.add_keybind('tab', lambda: print('Tabbing'))

    # For more complex GUIs, you can use the `gui` attribute of the popup
    # to create a GUI with the same syntax as Dear PyGui.
    # (See more at https://dearpygui.readthedocs.io/en/latest/index.html)
    with popup as gui:
        gui.add_checkbox(label='Box', callback=do_something)
```

Then, create a `Popup` object with the function and any additional options that
you would typically pass to as arguments to a dearpygui viewport.

```python
popup = Popup('^space', # Control + Space will toggle the popup
              build,
              width=1000,
              height=300,
              decorated=False, # Removes the title bar and close/minimize buttons
              anchor=Popup.ON_MOUSE)

popup.block()
```

The `block` method will block the current thread indefinitely. Pressing the hotkey
will toggle the popup window.


## Application specific popups

You can create a popup that is specific to an application by using the `application`
parameter of the `Popup` class. This will ensure that the popup is only shown when
the specified application is in focus.

The application argument should be in autohotkey title format. For example, to create
a popup that is only shown when Notepad is in focus, you would use the following:


```python
popup = Popup('^space', # Control + Space will toggle the popup
              build,
              width=200,
              height=200,
              anchor=Popup.ON_APP,
              application='ahk_exe notepad.exe')
```

