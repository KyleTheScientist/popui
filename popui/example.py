from popui.popup import Popup

def do_something():
    print('Doing something')

def build(popup: Popup):
    popup.add_button('Do something', callback=do_something)
    popup.add_button("Do something (Keep window open)", callback=do_something, close=False)

    with popup as gui:
        gui.add_checkbox(label='Box', callback=do_something)

    popup.add_keybind('tab', lambda: print('Tabbing'))

if __name__ == '__main__':
    popup = Popup('^e',
                  build,
                  width=1000,
                  height=300,
                  anchor=Popup.ON_MOUSE)

    popup.block()
