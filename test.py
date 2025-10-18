import itertools

from timeit import timeit

positions = {
    (x, y): 3
    for x, y in itertools.product(range(8), repeat=2)
}


def approach_1():
    result = 0
    for x, y in itertools.product(range(8), repeat=2):
        result += positions[(x, y)]
    return result


def approach_2():
    return sum([x for x in positions.values()])


print(timeit(approach_1))
print(timeit(approach_2))
