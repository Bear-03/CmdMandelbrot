from dataclasses import dataclass

def remap(value, old_min, old_max, new_min, new_max):
    old_range = old_max - old_min
    new_range = new_max - new_min
    return int(((value - old_min) / old_range) * new_range + new_min)

@dataclass
class CriticalPoints:
    min: int = 0
    max: int = 0

class Vector:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __add__(self, vector):
        if not isinstance(vector, Vector):
            raise ValueError("Vector operation is only possible with another Vector")

        return Vector(self.x + vector.x, self.y + vector.y)

    def __sub__(self, vector):
        return self.__add__(Vector(-vector.x, -vector.y))

    def __mul__(self, scalar):
        if not isinstance(scalar, (float, int)):
            raise ValueError("Vector operation is only possible with another Vector")

        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return self.__mul__(1 / scalar)

class Screen:
    def __init__(self, width, height, zoom, mov_sensitivity, zoom_sensitivity):
        self.width = width
        self.height = height
        self._zoom = zoom
        self.mov_sensitivity = mov_sensitivity
        self.zoom_sensitivity = zoom_sensitivity

        self._offset = Vector(50, 0)
        self.recalc_center()

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
