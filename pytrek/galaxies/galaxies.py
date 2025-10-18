import itertools

from random import randint

from .quadrants import Quadrant

_REGION_NAMES = [
    'ANTARES',
    'RIGEL',
    'PROCYON',
    'VEGA',
    'CANOPUS',
    'ALTAIR',
    'SAGITTARIUS',
    'POLLUX',
    'SIRIUS',
    'DENEB',
    'CAPELLA',
    'BETELGEUSE',
    'ALDEBARAN',
    'REGULUS',
    'ARCTURUS',
    'SPICA',
]


def _get_quadrant_name(position: tuple[int, int]):
    assert 0 <= position[0], position[1] < 8
    region = _REGION_NAMES[position[0] + int(position[1] >= 4) * 8]
    suffixes = ['I', 'II', 'III', 'IV']
    return f'{region} {suffixes[position[1] % 4]}'


class Galaxy:
    def __init__(self):
        self.quadrants = {
            (x, y): Quadrant(_get_quadrant_name((x, y)))
            for x, y in itertools.product(range(8), repeat=2)
        }
        self.initial_klingon_count = self.klingon_count
        self.initial_starbase_count = self.starbase_count
        if self.initial_starbase_count == 0:
            self.initial_starbase_count = 1
            insertion_position = (randint(0, 7), randint(0, 7))
            self.quadrants[insertion_position].has_starbase = True
            if self.quadrants[insertion_position].klingons < 2:
                self.quadrants[insertion_position].klingons += 1
        duration = max(randint(0, 9) + 25, self.initial_klingon_count + 1)
        self.start_date = randint(20, 39) * 100
        self.current_date = self.start_date
        self.end_date = self.start_date + duration

    @property
    def klingon_count(self):
        return sum([x.klingons for x in self.quadrants.values()])

    @property
    def starbase_count(self):
        return sum([int(x.has_starbase) for x in self.quadrants.values()])
    
    @property
    def time_remaining(self):
        return self.end_date - self.current_date

    @property
    def orders(self):
        single_klingon = self.initial_klingon_count == 1
        single_starbase = self.initial_starbase_count == 1
        single_stardate = self.time_remaining == 1
        return (
            f'DESTROY THE {self.initial_klingon_count} '
            f'KLINGON WARSHIP{'' if single_klingon else 'S'} '
            f'WHICH {'HAS' if single_klingon else 'HAVE'} INVADED THE GALAXY '
            f'BEFORE {'IT' if single_klingon else 'THEY'} CAN ATTACK '
            f'FEDERATION HEADQUARTERS ON STARDATE {self.end_date}. THIS GIVES '
            f'YOU {self.time_remaining} DAY{'' if single_stardate else 'S'}. '
            f'THERE {'IS' if single_starbase else 'ARE'} '
            f'{self.initial_starbase_count} '
            f'STARBASE{'' if single_starbase else 'S'} IN THE GALAXY FOR '
            f'RESUPPLYING YOUR SHIP.'
        )
