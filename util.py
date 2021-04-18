from dataclasses import dataclass
from colorama import Back
from typing import Union


@dataclass
class MaxAndMin:
    """
    Stores the maximum and minimum number of iterations tha will get a colour
    """
    min: int = 0
    max: int = 0


def map_to_colour(value: Union[int, float], max_and_min: MaxAndMin, colours: Union[list, tuple]) -> Back:
    """
    Maps the iteration count of each pixel to one of the colours in the colour array
    :param value: the value to map to the new range
    :param max_and_min: MaxAndMin instance containing the max and min iterations
    :param colours: collection of colours to use
    :return: Back
    """
    old_range = max_and_min.max - max_and_min.min
    index = int(((value - max_and_min.min) / old_range) * (len(colours) - 1))
    return colours[index]


class Vector:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __add__(self, vector):
        self.check_for_valid_operation(vector, Vector)
        return Vector(self.x + vector.x, self.y + vector.y)

    def __sub__(self, vector):
        return self.__add__(Vector(-vector.x, -vector.y))

    def __mul__(self, scalar):
        self.check_for_valid_operation(scalar, (float, int))
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return self.__mul__(1 / scalar)

    @staticmethod
    def check_for_valid_operation(value, classes: tuple):
        if not isinstance(value, classes):
            class_names = ",".join(class_element.__name__ for class_element in classes)
            raise ValueError(f"Vector operation is only possible with {class_names}")


class Screen:
    def __init__(self, width, height, zoom, mov_sensitivity, zoom_sensitivity):
        self.width = width
        self.height = height
        self._zoom = zoom
        self.mov_sensitivity = mov_sensitivity
        self.zoom_sensitivity = zoom_sensitivity
        self.center = None

        self.offset = Vector(50, 0)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        self.recalc_center()

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        """ adjusts current offset so figure doesn't move when zooming.
         This way the new offset is proportional to the old one with the new zoom """
        increase = value / self.zoom
        self.offset *= increase
        self._zoom = value

    def recalc_center(self):
        self.center = Vector(self.width / 2, self.height / 2) + self.offset
