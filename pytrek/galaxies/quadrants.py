import curses
import itertools

from dataclasses import dataclass
from random import randint, random, sample

from ..color_pairs import ColorPair


class LocalMap:
    @dataclass
    class Klingon:
        strength: float

    def __init__(
            self,
            quadrant: 'Quadrant',
            player_sector_coordinates: tuple[int, int],
    ):
        self.quadrant = quadrant
        available_positions = [
            (x, y)
            for x, y in itertools.product(range(8), repeat=2)
            if (x, y) != player_sector_coordinates
        ]
        required_space = quadrant.klingons + quadrant.stars
        if quadrant.has_starbase:
            required_space += 1
        choices = sample(available_positions, required_space)

        klingon_positions, star_positions, starbase_positions = (
            choices[0:quadrant.klingons],
            choices[quadrant.klingons:quadrant.klingons + quadrant.stars],
            choices[quadrant.klingons + quadrant.stars:],
        )
        self.klingons = {
            position: self.Klingon(200.0 * (0.5 + random()))
            for position in klingon_positions
        }
        self.stars = set([x for x in star_positions])
        self.starbases = set([x for x in starbase_positions])

        self.repair_factor = 0.5 * random()

    def draw(self, window: curses.window, player_position: tuple[int, int]):
        """Draws the map to the supplied window, given sufficient space."""
        height, width = window.getmaxyx()
        if height < 8 or width < 31:
            if height > 1 and width > 1:
                window.addstr('Insufficient space!'[:width - 1])
            return
        empty_space = (height - 8, width - 31)
        window.addstr(
            player_position[0] + empty_space[0] // 2,
            player_position[1] * 3 + empty_space[1] // 2,
            '<*>',
        )
        for klingon_position in self.klingons.keys():
            window.addstr(
                klingon_position[0] + empty_space[0] // 2,
                klingon_position[1] * 3 + empty_space[1] // 2,
                '+K+',
                curses.color_pair(ColorPair.KLINGON),
            )
        for star_position in self.stars:
            window.addstr(
                star_position[0] + empty_space[0] // 2,
                star_position[1] * 3 + empty_space[1] // 2,
                ' * ',
            )
        for starbase_position in self.starbases:
            window.addstr(
                starbase_position[0] + empty_space[0] // 2,
                starbase_position[1] * 3 + empty_space[1] // 2,
                '>!<',
            )


class Quadrant:
    def __init__(self, name: str):
        self.name = name
        self.scanned = False

        klingon_roll = random()
        if klingon_roll > 0.98:
            self.klingons = 3
        elif klingon_roll > 0.95:
            self.klingons = 2
        elif klingon_roll > 0.80:
            self.klingons = 1
        else:
            self.klingons = 0

        self.stars = randint(1, 8)
        self.has_starbase = random() > 0.96
