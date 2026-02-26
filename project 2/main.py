import arcade
from settings import SCREEN_W, SCREEN_H, TITLE
from ui import MenuView

def main():
    window = arcade.Window(
        SCREEN_W, SCREEN_H, TITLE,
        resizable=False,
        antialiasing=False,
        update_rate=1/60
    )
    window.show_view(MenuView())
    arcade.run()

if __name__ == "__main__":
    main()
