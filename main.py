import os
import sys

import numpy as np
from pynput.keyboard import Key, Listener
from colorama import init, Back, Style

from util import remap, CriticalPoints, Vector, Screen


def clear():
    os.system("cls" if os.name == "nt" else "clear")


init()
clear()

width, height = os.get_terminal_size()
screen = Screen(width, height - 1, 30, 30, 5)

iterations = 100 # iterations to perform until it is decided if z belongs to the set
threshold = 10  # iters for pixel to count as colour
cursor = False # shows a black square in the middle of the console, useful for zooming
colour_modulo = 10 # when to repeat the colours
colours = [Back.CYAN, Back.BLUE, Back.MAGENTA, Back.GREEN, Back.YELLOW, Back.RED]


def calculate():
    # python lists are needed because the list will contain both numbers and strings later on
    output = np.full((screen.width, screen.height), " ").tolist()
    critical_points = CriticalPoints()

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

                        if i_modulo > critical_points.max:
                            critical_points.max = i_modulo
                        if i_modulo < critical_points.min:
                            critical_points.min = i_modulo
                    break
            else:
                output[x][y] = Back.WHITE + " "

    return output, critical_points


# Also removes repeated colour codes to optimize printing
def generate_string(output, critical_points):
    string = ""
    last_char = " "
    for y in range(screen.height):
        for x in range(screen.width):
            if cursor and x == screen.width // 2 and y == screen.height // 2:
                output[x][y] = Back.BLACK + " "

            if isinstance(output[x][y], int):
                colour_index = remap(output[x][y], critical_points.min, critical_points.max, 0, len(colours) - 1)
                output[x][y] = colours[colour_index] + " "

            original_char = output[x][y]

            if last_char != " ":
                if last_char == original_char:
                    output[x][y] = " "
                elif original_char == " ":
                    output[x][y] = Back.RESET + " "

            string += output[x][y]
            last_char = original_char

    return Style.DIM + string + Style.RESET_ALL


def render():
    string = generate_string(*calculate())
    sys.stdout.write(string)


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
    keys = tuple(actions.keys())

    if key not in keys:
        return

    if key in keys[:4]:
        screen.offset += actions[key] * screen.mov_sensitivity
    elif key in keys[4:6]:
        screen.zoom *= actions[key]
        if screen.zoom <= 0:
            screen.zoom = 0.1
    else:
        sys.exit()

    clear()
    render()


with Listener(on_press=on_press) as listener:
    listener.join()
