from random import randint


class Enterprise:
    MAX_ENERGY = 3000
    MAX_TORPEDOES = 10

    def __init__(self):
        self.energy = self.MAX_ENERGY
        self.shields = 0
        self.torpedoes = self.MAX_TORPEDOES
        self.quadrant_coordinates = (randint(0, 7), randint(0, 7))
        self.sector_coordinates = (randint(0, 7), randint(0, 7))
