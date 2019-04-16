from util import V2, BBox


def test_V2():
    a = V2(0, 0)
    b = V2(0, 0)
    c = V2(1, 0)
    d = V2(0, 1)
    e = V2(1, 1)
    assert(a.x == 0)
    assert(a.y == 0)
    assert(a == b)
    assert(a != c)
    assert(a != d)
    assert(a != e)


def test_BBox():
    a = BBox(V2(0, 0), V2(1, 1))
    assert(a.min == V2(0, 0))
    assert(a.max == V2(1, 1))

    a.expand(V2(7, 11))
    assert(a.min == V2(0, 0))
    assert(a.max == V2(7, 11))

    a.expand(V2(-3, -19))
    assert(a.min == V2(-3, -19))
    assert(a.max == V2(7, 11))

    assert(a.width == 10)
    assert(a.height == 30)

    # immutability on copy constructor
    b = BBox(a.min, a.max)
    b.expand(V2(100, 100))
    assert(a.min == V2(-3, -19))
    assert(a.max == V2(7, 11))
    assert(b.min == V2(-3, -19))
    assert(b.max == V2(100, 100))
