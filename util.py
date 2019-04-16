from math import inf


class V2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '({0}, {1})'.format(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class BBox:
    def __init__(self, min, max):
        self.min = V2(min.x, min.y)
        self.max = V2(max.x, max.y)

    def __str__(self):
        return 'min: {0} max: {1}'.format(self.min, self.max)

    def __eq__(self, other):
        return self.min == other.min and self.max == other.max

    def expand(self, coordinate):
        self.min.x = min(coordinate.x, self.min.x)
        self.min.y = min(coordinate.y, self.min.y)
        self.max.x = max(coordinate.x, self.max.x)
        self.max.y = max(coordinate.y, self.max.y)

    def get_width(self):
        return self.max.x - self.min.x

    def get_height(self):
        return self.max.y - self.min.y

    width = property(get_width)
    height = property(get_height)
