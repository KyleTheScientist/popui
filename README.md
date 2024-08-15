# popui

A Python module for creating GUI popups with Dear PyGui and AutoHotkey on Windows

## Installation

```bash
pip install popui
```

## Usage

To create a popup, first define a function that builds the GUI.

```python
from popui import Popup

def build(popup: Popup):
    popup.add_button('Do something', callback=lambda: print('Doing something'))
    popup.add_button("Do Nothing (Keep window open)", popup.no_op, close=False)
    popup.add_keybind('tab', lambda: print('Tabbing'))
```
The `popup.add_button()` method is a convenience method that creates a button that will close the popup window after the callback function is called by default.
The `add_keybind()` method is a convenience method that causes the provided callback to be called when the specified keybind is pressed while the window is active.


Then, create a `Popup` object with the function and any additional options that
you would typically pass to as arguments to a dearpygui viewport.

```python
if __name__ == '__main__':
    popup = Popup('^space', build, width=200, height=200) # Control + Space will toggle the popup
    popup.block()
```

The `block` method will block the current thread indefinitely. Pressing the hotkey
will toggle the popup window.


## Dear PyGui elements

For more complex GUIs, you can use the `gui` attribute of the popup to create a GUI with the same syntax as Dear PyGui. (See more at https://dearpygui.readthedocs.io/en/latest/index.html). If used as a context manager, any elements created within the context will be parented to the popup window automatically.

```python

popup.gui.add_text(label='Hello, world!', parent=popup.root)

with popup as gui:
    gui.add_checkbox(label='Box', callback=lambda: print('Box checked'))
    with gui.tab_bar():
        gui.add_tab(label='Tab 1')
        gui.add_tab(label='Tab 2')
```


## Application specific popups

You can create a popup that is specific to an application by using the `application`
parameter of the `Popup` class. This will ensure that the popup is only shown when
the specified application is in focus.

The application argument should be in autohotkey title format. For example, to create
a popup that is only shown when Notepad is in focus, you would use the following:


```python
popup = Popup('~!e',
              build,
              anchor=Popup.ON_APP,
              application='ahk_exe notepad.exe',
              decorated=False, # Removes the title bar and border from the viewport (much better looking imo)
              width=200,
              height=200).build()
```

