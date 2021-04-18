import os
import sys

import numpy as np
from pynput.keyboard import Key, Listener
from colorama import init, Back, Style

from util import map_to_colour, MaxAndMin, Vector, Screen


def clear():
    os.system("cls" if os.name == "nt" else "clear")


init()
clear()

width, height = os.get_terminal_size()
screen = Screen(width, height - 1, 30, 30, 5)

iterations = 100  # iterations to perform until it is decided if z belongs to the set
threshold = 10  # iterations for pixel not in the set to be coloured
cursor = True  # shows a black square in the middle of the console, useful for zooming
colour_modulo = 10  # controls how often colours are repeated
cursor_colour = Back.BLACK
clear_on_exit = True
colours = (Back.CYAN, Back.BLUE, Back.MAGENTA, Back.GREEN, Back.YELLOW, Back.RED)


def calculate():
    # python lists are needed because the list will contain both numbers and strings later on
    output = np.full((screen.width, screen.height), " ").tolist()
    index_max_and_min = MaxAndMin()

    for y in range(screen.height):
        for x in range(screen.width):

            c = complex((x - screen.center.x), (y - screen.center.y)) / screen.zoom
            z = complex(0)

            for i in range(iterations):
                z = z ** 2 + c
                if abs(z) > 2:
                    if i > threshold:
                        i_modulo = i % colour_modulo
                        output[x][y] = i_modulo

                        # MaxAndMin will store the boundaries so they can then be mapped to the colour array
                        if i_modulo > index_max_and_min.max:
                            index_max_and_min.max = i_modulo
                        if i_modulo < index_max_and_min.min:
                            index_max_and_min.min = i_modulo
                    break
            else:
                output[x][y] = Back.WHITE + " "

    return output, index_max_and_min


# Also removes repeated colour codes to optimize printing
def generate_string(output, index_max_and_min):
    string = ""
    last_char = " "
    for y in range(screen.height):
        for x in range(screen.width):
            # Draw cursor
            if cursor and x == screen.width // 2 and y == screen.height // 2:
                output[x][y] = cursor_colour + " "

            # The pixel doesn't belong to the set but it was close
            if isinstance(output[x][y], int):
                output[x][y] = map_to_colour(output[x][y], index_max_and_min, colours) + " "

            current_char = output[x][y]

            # Removes repeated colour codes so it is printed faster
            # The colour code will be removed if the pixel before had the same colour
            if last_char != " ":
                if last_char == current_char:
                    output[x][y] = " "
                elif current_char == " ":
                    # Transparent pixel
                    output[x][y] = Back.RESET + " "

            string += output[x][y]
            last_char = current_char

    return Style.DIM + string + Style.RESET_ALL


def render():
    string = generate_string(*calculate())
    print(string)


render()


def on_press(key):
    global screen

    actions = {
        Key.up: Vector(0, 1),
        Key.down: Vector(0, -1),
        Key.right: Vector(-1, 0),
        Key.left: Vector(1, 0),
        Key.f1: 1 / screen.zoom_sensitivity,
        Key.f2: screen.zoom_sensitivity,
        Key.esc: None
    }
    try:
        action = actions[key]
    except KeyError:
        return

    if isinstance(action, Vector):
        screen.offset += action * screen.mov_sensitivity
    elif isinstance(action, (float, int)):
        screen.zoom *= action
        if screen.zoom <= 0:
            screen.zoom = 0.1
    else:
        if clear_on_exit:
            clear()
        sys.exit()

    clear()
    render()


with Listener(on_press=on_press) as listener:
    listener.join()
