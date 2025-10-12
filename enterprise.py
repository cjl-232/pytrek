import re

from math import ceil, floor, sqrt
from random import choice, randint, random
from typing import Callable

from galaxy import Galaxy


def _navigation_calculator(start: tuple[int, int], end: tuple[int, int]):
    vertical_movement = end[0] - start[0]
    horizontal_movement = end[1] - start[1]
    if vertical_movement == 0:
        if horizontal_movement > 0:
            direction = 6
        elif horizontal_movement < 0:
            direction = 4
        else:
            direction = 5
    elif horizontal_movement == 0:
        if vertical_movement > 0:
            direction = 2
        elif vertical_movement < 0:
            direction = 8
        else:
            direction = 5
    else:
        slope = abs(vertical_movement) / abs(horizontal_movement)
        if slope <= 0.5:
            if horizontal_movement > 0.0:
                direction = 6
            else:
                direction = 4
        elif slope > 4.0:
            if vertical_movement > 0.0:
                direction = 2
            else:
                direction = 8
        else:
            if horizontal_movement > 0.0:
                if vertical_movement > 0.0:
                    direction = 3
                else:
                    direction = 9
            else:
                if vertical_movement > 0.0:
                    direction = 1
                else:
                    direction = 7
    distance = sqrt(sum([pow(a - b, 2) for a, b in zip(start, end)]))
    print(f'    DIRECTION = {direction}')
    print(f'    DISTANCE = {distance:.2f}')


class Device:
    def __init__(
            self,
            handler: Callable[[bool], None],
            name: str,
            help_text: str,
            health: float = 0.0,
    ):
        self._handler = handler
        self.name = name
        self.help_text = help_text
        self.health = health

    @property
    def operational(self):
        return self.health >= 0.0

    def handle_command(self):
        self._handler(self.operational)


class Enterprise:

    MAX_ENERGY = 3000
    MAX_TORPEDOES = 10

    def __init__(self, galaxy: Galaxy):
        self.galaxy = galaxy
        self.destroyed = False
        self.resigned = False
        self.fired = False
        self.docked = False
        self.galactic_coordinates = (randint(0, 7), randint(0, 7))
        self.quadrant_coordinates = (randint(0, 7), randint(0, 7))
        self.energy = self.MAX_ENERGY
        self.shields = 0
        self.torpedoes = self.MAX_TORPEDOES

        # Retrieve a quadrant map:
        quadrant = galaxy.quadrants[self.galactic_coordinates]
        self.local_map = quadrant.generate_local_map(self.quadrant_coordinates)

        # Set up devices:
        self._devices = {
            'NAV': Device(
                handler=self._use_warp_engines,
                name='WARP ENGINES',
                help_text='TO SET COURSE'
            ),
            'SRS': Device(
                handler=self._use_short_range_sensors,
                name='SHORT RANGE SENSORS',
                help_text='FOR SHORT RANGE SENSOR SCAN',
            ),
            'LRS': Device(
                handler=self._use_long_range_sensors,
                name='LONG RANGE SENSORS',
                help_text='FOR LONG RANGE SENSOR SCAN',
            ),
            'PHA': Device(
                handler=self._fire_phasers,
                name='PHASER CONTROL',
                help_text='TO FIRE PHASERS',
            ),
            'TOR': Device(
                handler=self._fire_torpedo,
                name='PHOTON TUBES',
                help_text='TO FIRE PHOTON TORPEDOES',
            ),
            'SHE': Device(
                handler=self._adjust_shields,
                name='SHIELD CONTROL',
                help_text='TO RAISE OR LOWER SHIELDS',
            ),
            'DAM': Device(
                handler=self._damage_control,
                name='DAMAGE CONTROL',
                help_text='FOR DAMAGE CONTROL REPORTS',
            ),
            'COM': Device(
                handler=self._use_library_computer,
                name='LIBRARY-COMPUTER',
                help_text='TO CALL ON LIBRARY-COMPUTER',
            )
        }
        self._device_keys = list(self._devices.keys())

        # Officially enter the starting quadrant:
        self._new_quadrant_handler()

    @property
    def total_energy(self):
        return self.energy + self.shields

    def handle_command(self, command: str):
        self._docking_check()
        if command in self._devices:
            self._devices[command].handle_command()
            self._stranded_check()
        elif command == 'XXX':
            self.resigned = True
        else:
            print('ENTER ONE OF THE FOLLOWING:')
            for key, value in self._devices.items():
                print(f'  {key}  ({value.help_text})')
            print('  XXX  (TO RESIGN YOUR COMMAND)')
            print()

    def _docking_check(self):
        self.docked = False
        for i in range(-1, +2):
            for j in range(-1, +2):
                if (tuple([
                    x + y
                    for x, y
                    in zip(self.quadrant_coordinates, (i, j))
                ])) in self.local_map.starbases:
                    self.docked = True
                    self.energy = self.MAX_ENERGY
                    self.shields = 0
                    self.torpedoes = self.MAX_TORPEDOES
                    print('SHIELDS DROPPED FOR DOCKING PURPOSES')
                    return

    def _stranded_check(self):
        if self.energy > 10:
            return
        elif self.energy + self.shields > 10:
            if self._devices['SHE'].operational:
                return
        print("** FATAL ERROR **   YOU'VE JUST STRANDED YOUR SHIP IN SPACE")
        print("YOU HAVE INSUFFICIENT MANEUVERING ENERGY, AND SHIELD CONTROL")
        print("IS PRESENTLY INCAPABLE OF CROSS-CIRCUITING TO ENGINE ROOM!!")
        self.destroyed = True

    def _new_quadrant_handler(self):
        quadrant = self.galaxy.quadrants[self.galactic_coordinates]
        quadrant.entered = True
        self.local_map = quadrant.generate_local_map(self.quadrant_coordinates)
        if self.galaxy.current_date == self.galaxy.start_date:
            print('YOUR MISSION BEGINS WITH YOUR STARSHIP LOCATED')
            print(f'IN THE GALACTIC QUADRANT {quadrant.name}')
        else:
            print(f'NOW ENTERING {quadrant.name} QUADRANT . . .')
        print()
        if quadrant.klingons > 0:
            print('COMBAT AREA      CONDITION RED'.center(30))
            if self.shields <= 200:
                print('SHIELDS DANGEROUSLY LOW'.center(30))
        self.handle_command('SRS')

    def _process_klingon_moves(self):
        # Live Klingons get moved randomly, moves to a random empty space:
        for position in list(self.local_map.klingons.keys()):
            klingon = self.local_map.klingons.pop(position)
            if klingon.energy <= 0.0:
                continue
            empty_sectors = self.local_map.get_empty_sectors(
                enterprise_sector=self.quadrant_coordinates,
            )
            new_position = choice(empty_sectors)
            self.local_map.klingons[new_position] = klingon

    def _process_klingon_firing(self):
        if self.local_map.klingons:
            print('KLINGONS OPEN FIRE!')
            if self.docked:
                print('STARBASE SHIELDS PROTECT THE ENTERPRISE')
                return
        else:
            return
        for position, klingon in self.local_map.klingons.items():
            distance = sqrt(sum([
                pow(x - y, 2)
                for x, y in zip(self.quadrant_coordinates, position)
            ]))
            damage = int((klingon.energy / distance) * (2.0 + random()))
            klingon.energy /= (3.0 + random())
            print((
                f'{damage}-UNIT HIT ON ENTERPRISE FROM SECTOR '
                f'{position[0]}, {position[1]}'
            ))
            if damage >= self.shields:
                self.destroyed = True
                return
            self.shields -= damage
            print((
                f'      <SHIELDS DOWN TO {self.shields} '
                f'UNIT{'S' if self.shields != 1 else ''}>'
            ))
            if random() > 0.4 and damage / self.shields > 0.02:
                target = self._devices[choice(self._device_keys)]
                target.health -= (damage / self.shields) + 0.5 * random()
                print((
                    f"DAMAGE CONTROL REPORTS '{target.name} "
                    f"DAMAGED BY THE HIT'"
                ))

    def _damage_control_report(self, warp_factor: float):
        repair = min(1.0, warp_factor)
        damaged_devices = [
            device
            for device in self._devices.values()
            if not device.operational
        ]
        first_event = True
        for device in damaged_devices:
            device.health = device.health + repair
            if device.operational:
                if first_event:
                    print('DAMAGE CONTROL REPORT:')
                    first_event = False
                print(f'\t{device.name} REPAIR COMPLETED.')
        if random() >= 0.2:
            return
        random_device = self._devices[choice(self._device_keys)]
        if random() >= 0.6:
            random_device.health += random() * 3.0 + 1.0
            print((
                f'DAMAGE CONTROL REPORT: {random_device.name} STATE OF REPAIR '
                f'IMPROVED.\n'
            ))
        else:
            random_device.health -= random() * 0.5 + 1.0
            print(f'DAMAGE CONTROL REPORT: {random_device.name} DAMAGED.\n')

    def _use_warp_engines(self, device_operational: bool):
        match input('COURSE (1-9): ').strip():
            case '1':
                direction_vector = [+1, -1]
            case '2':
                direction_vector = [+1, +0]
            case '3':
                direction_vector = [+1, +1]
            case '4':
                direction_vector = [+0, -1]
            case '6':
                direction_vector = [+0, +1]
            case '7':
                direction_vector = [-1, -1]
            case '8':
                direction_vector = [-1, +0]
            case '9':
                direction_vector = [-1, +1]
            case '':
                return
            case _:
                print("   LT. SULU REPORTS, 'INCORRECT COURSE DATA, SIR!'")
                return
        max_factor = 8.0 if device_operational else 0.2
        factor = input(f'WARP FACTOR (0.0-{max_factor:.1f}): ')
        if not factor:
            return
        try:
            factor = round(float(factor), 1)
            if factor == 0.0:
                return
            elif factor > max_factor and not device_operational:
                print('WARP ENGINES ARE DAMAGED.  MAXIMUM SPEED = WARP 0.2')
                return
            elif not 0.0 < factor <= max_factor:
                print((
                    f"   CHIEF ENGINEER SCOTT REPORTS 'THE ENGINES WON'T TAKE "
                    f"WARP {factor:.2f}!'"
                ))
                return
        except ValueError:
            print("CHIEF ENGINEER SCOTT REPORTS 'ORDER NOT UNDERSTOOD.'")
            return
        cost = int(factor * 8.0 + 0.5)
        if cost > self.energy:
            print("ENGINEERING REPORTS   'INSUFFICIENT ENERGY AVAILABLE")
            print(f"                       FOR MANEUVERING AT WARP {factor}!'")
            if self._devices['SHE'].operational and self.total_energy >= cost:
                print((
                    f'DEFLECTOR CONTROL ROOM ACKNOWLEDGES {self.shields} '
                    f'UNIT{'S' if self.shields != 1 else ''} OF ENERGY'
                ))
                print(
                    '                         PRESENTLY DEPLOYED TO SHIELDS.',
                )
            return
        # Klingons respond to movement:
        self._process_klingon_moves()
        self._process_klingon_firing()
        self._damage_control_report(factor)
        # Enterprise moves:
        initial_position = [
            self.galactic_coordinates[i] * 8 + self.quadrant_coordinates[i]
            for i in range(2)
        ]
        destination_sector = list(self.quadrant_coordinates)
        destination_quadrant = list(self.galactic_coordinates)
        new_quadrant = False
        out_of_bounds = False
        for _ in range(cost):
            for i in range(2):
                destination_sector[i] += direction_vector[i]
                if destination_sector[i] < 0:
                    if destination_quadrant[i] > 0:
                        new_quadrant = True
                        destination_quadrant[i] -= 1
                        destination_sector[i] = 7
                        break
                    else:
                        out_of_bounds = True
                        destination_sector[i] -= direction_vector[i]
                        break
                elif destination_sector[i] > 7:
                    if destination_quadrant[i] < 7:
                        new_quadrant = True
                        destination_quadrant[i] += 1
                        destination_sector[i] = 0
                        break
                    else:
                        out_of_bounds = True
                        destination_sector[i] -= direction_vector[i]
                        break
            if not new_quadrant:
                collision = False
                if tuple(destination_sector) in self.local_map.klingons:
                    collision = True
                elif tuple(destination_sector) in self.local_map.starbases:
                    collision = True
                elif tuple(destination_sector) in self.local_map.stars:
                    collision = True
                if collision:
                    print((
                        f'WARP ENGINES SHUT DOWN AT SECTOR '
                        f'{self.quadrant_coordinates[0]}, '
                        f'{self.quadrant_coordinates[1]} DUE TO BAD NAVIGATION'
                    ))
                    break
            self.galactic_coordinates = tuple(destination_quadrant)
            self.quadrant_coordinates = tuple(destination_sector)
            if new_quadrant or out_of_bounds:
                self.galaxy.current_date += 1
                self.energy -= cost + 10
                if self.energy < 0:
                    print((
                        'SHIELD CONTROL SUPPLIES ENERGY TO COMPLETE THE '
                        'MANEUVER.'
                    ))
                    self.shields = max(self.shields + self.energy, 0)
                    self.energy = 0
                break
        if new_quadrant:
            final_position = [
                max(0, min(x + y, 63))
                for x, y in zip(
                    initial_position,
                    [x * cost for x in direction_vector],
                )
            ]
            self.galactic_coordinates = tuple([x // 8 for x in final_position])
            self.quadrant_coordinates = tuple([x % 8 for x in final_position])
            self._new_quadrant_handler()
        elif out_of_bounds:
            print("LT. UHURA REPORTS MESSAGE FROM STARFLEET COMMAND:")
            print("  'PERMISSION TO ATTEMPT CROSSING OF GALACTIC PERIMETER")
            print("  IS HEREBY *DENIED*.  SHUT DOWN YOUR ENGINES.'")
            print("CHIEF ENGINEER SCOTT REPORTS  'WARP ENGINES SHUT DOWN")
            print((
                f"  AT SECTOR {destination_sector[0]}, "
                f"{destination_sector[1]} OF QUADRANT "
                f"{destination_quadrant[0]}, {destination_quadrant[1]}.'"
            ))
        else:
            self.galaxy.current_date += min(0.1 * int(factor * 10.0), 1.0)
            self.energy -= cost + 10
            if self.energy < 0:
                print((
                    'SHIELD CONTROL SUPPLIES ENERGY TO COMPLETE THE '
                    'MANEUVER.'
                ))
                self.shields = max(self.shields + self.energy, 0)
                self.energy = 0

    def _use_short_range_sensors(self, device_operational: bool):
        if not device_operational:
            print('*** SHORT RANGE SENSORS ARE OUT ***')
            return
        if self.local_map.klingons:
            condition = 'RED'
        elif self.energy < 0.1 * self.MAX_ENERGY:
            condition = 'YELLOW'
        else:
            condition = 'GREEN'
        g1, g2 = self.galactic_coordinates
        s1, s2 = self.quadrant_coordinates
        lines = [''] * 8
        for i in range(8):
            for j in range(8):
                sector = (i, j)
                if sector == self.quadrant_coordinates:
                    lines[i] += ' <*>'
                elif sector in self.local_map.klingons:
                    lines[i] += ' +K+'
                elif sector in self.local_map.starbases:
                    lines[i] += ' >!<'
                elif sector in self.local_map.stars:
                    lines[i] += '  * '
                else:
                    lines[i] += '    '
        current_date = floor(self.galaxy.current_date)
        lines[0] += f'        STARDATE           {current_date}'
        lines[1] += f'        CONDITION          {condition}'
        lines[2] += f'        QUADRANT           {g1}, {g2}'
        lines[3] += f'        SECTOR             {s1}, {s2}'
        lines[4] += f'        PHOTON TORPEDOES   {self.torpedoes}'
        lines[5] += f'        TOTAL ENERGY       {self.energy + self.shields}'
        lines[6] += f'        SHIELDS            {self.shields}'
        lines[7] += f'        KLINGONS REMAINING {self.galaxy.klingon_count}'
        print('-' * 33)
        print('\n'.join(lines))
        print('-' * 33)

    def _use_long_range_sensors(self, device_operational: bool):
        if not device_operational:
            print('*** LONG RANGE SENSORS ARE INOPERABLE ***')
            return
        q1, q2 = self.galactic_coordinates
        print(f'LONG RANGE SCAN FOR QUADRANT {q1}, {q2}')
        print('-------------------')
        for x in range(q1 - 1, q1 + 2):
            if not 0 <= x <= 7:
                print(' '.join([':'] + ['***'] * 3 + [':']))
                continue
            scan_line_components = []
            for y in range(q2 - 1, q2 + 2):
                if 0 <= y <= 7:
                    scan_line_components.append((
                        f'{int(self.galaxy.quadrants[(x, y)].klingons)}'
                        f'{int(self.galaxy.quadrants[(x, y)].has_starbase)}'
                        f'{int(self.galaxy.quadrants[(x, y)].stars)}'
                    ))
                else:
                    scan_line_components.append('***')
            print(' '.join([':'] + scan_line_components + [':']))

    def _fire_phasers(self, device_operational: bool):
        if not device_operational:
            print('PHASERS INOPERATIVE')
            return
        elif not self.local_map.klingons:
            print(
                "SCIENCE OFFICER SPOCK REPORTS  'SENSORS SHOW NO ENEMY SHIPS",
            )
            print("                                IN THIS QUADRANT'")
            return
        if not self._devices['COM'].operational:
            print('COMPUTER FAILURE HAMPERS ACCURACY')
        print((
            f'PHASERS LOCKED ON TARGET;  ENERGY AVAILABLE = {self.energy} '
            f'UNIT{'S' if self.energy != 1 else ''}'
        ))
        value = input('NUMBER OF UNITS TO FIRE: ')
        if not value.isdigit() or int(value) == 0 or int(value) > self.energy:
            return
        value = float(value)
        self.energy -= int(value)
        if not self._devices['COM'].operational:
            value *= random()
        base_damage = value / len(self.local_map.klingons)
        for position in list(self.local_map.klingons.keys()):
            klingon = self.local_map.klingons[position]
            distance = sqrt(sum([
                pow(x - y, 2)
                for x, y in zip(self.quadrant_coordinates, position)
            ]))
            damage = (base_damage / distance) * (random() + 2.0)
            if damage <= 0.15 * klingon.energy:
                print((
                    f'SENSORS SHOW NO DAMAGE TO ENEMY AT {position[0]}, '
                    f'{position[1]}'
                ))
                continue
            klingon.energy -= damage
            print((
                f'{ceil(damage)}-UNIT HIT ON KLINGON AT SECTOR {position[0]}, '
                f'{position[1]}'
            ))
            if klingon.energy <= 0.0:
                print('*** KLINGON DESTROYED ***')
                self.local_map.klingons.pop(position)
                self.galaxy.quadrants[self.galactic_coordinates].klingons -= 1
            else:
                print((
                    f'   (SENSORS SHOW {ceil(klingon.energy)} '
                    f'UNIT{'S' if ceil(klingon.energy) != 1 else ''} '
                    'REMAINING)'
                ))
        self._process_klingon_firing()

    def _fire_torpedo(self, device_operational: bool):
        if not device_operational:
            print('PHOTON TUBES ARE NOT OPERATIONAL')
            return
        elif self.torpedoes <= 0:
            print('ALL PHOTON TORPEDOES EXPENDED')
            return
        elif self.energy < 2:
            print('INSUFFICIENT ENERGY TO FIRE TORPEDOES')
            return
        match input('PHOTON TORPEDO COURSE (1-9): ').strip():
            case '1':
                direction_vector = [+1, -1]
            case '2':
                direction_vector = [+1, +0]
            case '3':
                direction_vector = [+1, +1]
            case '4':
                direction_vector = [+0, -1]
            case '6':
                direction_vector = [+0, +1]
            case '7':
                direction_vector = [-1, -1]
            case '8':
                direction_vector = [-1, +0]
            case '9':
                direction_vector = [-1, +1]
            case '':
                return
            case _:
                print(
                    "   ENSIGN CHEKOV REPORTS, 'INCORRECT COURSE DATA, SIR!'",
                )
                return
        self.energy -= 2
        self.torpedoes -= 1
        torpedo_position = self.quadrant_coordinates
        print('TORPEDO TRACK:')
        for _ in range(8):
            torpedo_position = tuple([
                current_position + movement
                for current_position, movement
                in zip(list(torpedo_position), direction_vector)
            ])
            within_bounds = all([0 <= x <= 7 for x in torpedo_position])
            if not within_bounds:
                print('               QUADRANT LIMIT')
                print('TORPEDO MISSED')
                break
            x, y = torpedo_position
            print(f'               {x}, {y}')
            if torpedo_position in self.local_map.klingons:
                print('*** KLINGON DESTROYED ***')
                self.local_map.klingons.pop(torpedo_position)
                quadrant = self.galaxy.quadrants[self.galactic_coordinates]
                quadrant.klingons -= 1
                break
            elif torpedo_position in self.local_map.stars:
                print(f'STAR AT {x}, {y} ABSORBED TORPEDO ENERGY.')
                break
            elif torpedo_position in self.local_map.starbases:
                print('*** STARBASE DESTROYED ***')
                self.local_map.starbases.remove(torpedo_position)
                quadrant = self.galaxy.quadrants[self.galactic_coordinates]
                quadrant.has_starbase = False
                if self.galaxy.klingon_count > self.galaxy.time_remaining:
                    print((
                        'THAT DOES IT, CAPTAIN!!  YOU ARE HEREBY RELIEVED '
                        'OF COMMAND'
                    ))
                    print((
                        'AND SENTENCED TO 99 STARDATES AT HARD LABOR ON '
                        'CYGNUS 12!!'
                    ))
                    self.fired = True
                    return
                else:
                    print(
                        'STARFLEET COMMAND REVIEWING YOUR RECORD TO CONSIDER',
                    )
                    print('COURT MARTIAL!')
                break
        self._process_klingon_firing()

    def _adjust_shields(self, device_operational: bool):
        if not device_operational:
            print('SHIELD CONTROL INOPERABLE')
            return
        total_energy = self.energy + self.shields
        info = f'ENERGY AVAILABLE = {total_energy}'
        value = input(info + ' NUMBER OF UNITS TO SHIELDS: ')
        if not value.isdigit():
            print("SHIELD CONTROL REPORTS  'ORDER NOT UNDERSTOOD.'")
            print('<SHIELDS UNCHANGED>')
            return
        value = int(value)
        if value > total_energy:
            print((
                "SHIELD CONTROL REPORTS  'THIS IS NOT THE FEDERATION "
                "TREASURY.'"
            ))
            print('<SHIELDS UNCHANGED>')
        elif value == self.shields:
            print('<SHIELDS UNCHANGED>')
        else:
            self.shields = value
            self.energy = total_energy - self.shields
            print('DEFLECTOR CONTROL ROOM REPORT:')
            print((
                f'SHIELDS NOW AT {self.shields} UNIT'
                f'{'S' if self.shields != 1 else ''} PER YOUR COMMAND.'
            ))

    def _report_device_status(self):
        print()
        print('DEVICE             STATE OF REPAIR')
        for device in self._devices.values():
            print(f'{device.name:<19}{device.health:>15.2f}')
        print()

    def _damage_control(self, device_operational: bool):
        if not device_operational:
            print('DAMAGE CONTROL REPORT NOT AVAILABLE')
        else:
            self._report_device_status()
        if not self.docked:
            return
        repair_cost = self.local_map.repair_factor * sum([
            0.1 if not device.operational else 0.0
            for device in self._devices.values()
        ])
        if repair_cost == 0.0:
            return
        print()
        print('TECHNICIANS STANDING BY TO EFFECT REPAIRS TO YOUR SHIP;')
        print(f'ESTIMATED TIME TO REPAIR: {repair_cost:.2f} STARDATES')
        value = input('WILL YOU AUTHORIZE THE REPAIR ORDER? (Y/N) ')
        if value.strip().upper() != 'Y':
            return
        for device in self._devices.values():
            device.health = max(device.health, 0.0)
        self._report_device_status()

    def _use_library_computer(self, device_operational: bool):
        if not device_operational:
            print('COMPUTER DISABLED')
            return
        value = ''
        first_iteration = True
        while not value.isdigit() or not 0 <= int(value) <= 6:
            if not first_iteration:
                print('FUNCTIONS AVAILABLE FROM LIBRARY-COMPUTER:')
                print('   0 = CUMULATIVE GALACTIC RECORD')
                print('   1 = STATUS REPORT')
                print('   2 = PHOTON TORPEDO DATA')
                print('   3 = STARBASE NAV DATA')
                print('   4 = DIRECTION/DISTANCE CALCULATOR')
                print("   5 = GALAXY 'REGION NAME' MAP")
                print('   6 = CANCEL')
                print()
            first_iteration = False
            value = input('COMPUTER ACTIVE AND AWAITING COMMAND: ').strip()
        match int(value):
            case 0:
                self._library_computer_galactic_record()
            case 1:
                self._library_computer_status_report()
            case 2:
                self._library_computer_torpedo_nav_data()
            case 3:
                self._library_computer_starbase_nav_data()
            case 4:
                self._library_computer_direction_distance_calculator()
            case 5:
                self._library_computer_galaxy_map()
            case _:
                pass

    def _library_computer_galactic_record(self):
        x, y = self.galactic_coordinates
        print(f'        COMPUTER RECORD OF GALAXY FOR QUADRANT {x}, {y}')
        print()
        print('       1     2     3     4     5     6     7     8')
        print('     ----- ----- ----- ----- ----- ----- ----- -----')
        for i in range(8):
            line = f' {i + 1} '
            for j in range(8):
                line += '   '
                quadrant = self.galaxy.quadrants[(i, j)]
                if not quadrant.entered:
                    line += '***'
                else:
                    line += f'{quadrant.klingons}'
                    line += f'{1 if quadrant.has_starbase else 0}'
                    line += f'{quadrant.stars}'
            print(line)
            print('     ----- ----- ----- ----- ----- ----- ----- -----')
        print()

    def _library_computer_status_report(self):
        klingons = self.galaxy.klingon_count
        time_limit = ceil(self.galaxy.end_date - self.galaxy.current_date)
        bases = self.galaxy.starbase_count
        print('   STATUS REPORT:')
        print(f'KLINGON{'S' if klingons != 1 else ''} LEFT:  {klingons}')
        print((
            f'MISSION MUST BE COMPLETED IN {time_limit} '
            f'STARDATE{'S' if time_limit != 1 else ''}'
        ))
        if bases > 0:
            print((
                f'THE FEDERATION IS MAINTAINING {bases} '
                f'STARBASE{'S' if bases != 1 else ''} IN THE GALAXY'
            ))
        else:
            print('YOUR STUPIDITY HAS LEFT YOU ON YOUR ON IN')
            print('  THE GALAXY -- YOU HAVE NO STARBASES LEFT!')
        self._devices['DAM'].handle_command()

    def _library_computer_torpedo_nav_data(self):
        klingon_positions = list(self.local_map.klingons.keys())
        match len(klingon_positions):
            case 0:
                print((
                    "SCIENCE OFFICER SPOCK REPORTS  'SENSORS SHOW NO ENEMY "
                    "SHIPS"
                ))
                print("                                IN THIS QUADRANT.'")
            case 1:
                print('SENSORS DETECT 1 ENEMY SHIP:')
                print()
            case _:
                print(f'SENSORS DETECT {len(klingon_positions)} ENEMY SHIPS:')
                print()
        for position in klingon_positions:
            _navigation_calculator(self.quadrant_coordinates, position)
            print()

    def _library_computer_starbase_nav_data(self):
        if not self.local_map.starbases:
            print((
                "MR. SPOCK REPORTS,  'SENSORS SHOW NO STARBASES IN THIS "
                "QUADRANT.'"
            ))
            return
        print('SENSORS DETECT LOCAL STARBASE:')
        for position in self.local_map.starbases:
            _navigation_calculator(self.quadrant_coordinates, position)
            break
        print()

    def _library_computer_direction_distance_calculator(self):
        pattern = r'^.*?([+-]?\d+).*,.*?([+-]?\d+).*$'
        print('DIRECTION/DISTANCE CALCULATOR:')
        q1, q2 = self.galactic_coordinates
        s1, s2 = self.quadrant_coordinates
        print(f'YOU ARE AT QUADRANT {q1}, {q2} SECTOR {s1}, {s2}')
        print('PLEASE ENTER')
        start_match = re.match(pattern, input('  INITIAL COORDINATES (X, Y) '))
        if not start_match:
            print('INVALID INPUT')
            return
        end_match = re.match(pattern, input('  FINAL COORDINATES (X, Y) '))
        if not end_match:
            print('INVALID INPUT')
            return
        start = tuple([int(x) for x in start_match.group(1, 2)])
        end = tuple([int(x) for x in end_match.group(1, 2)])
        print(start, end)
        _navigation_calculator(start, end)

    def _library_computer_galaxy_map(self):
        x, y = self.galactic_coordinates
        print('                        THE GALAXY')
        print('       1     2     3     4     5     6     7     8')
        print('     ----- ----- ----- ----- ----- ----- ----- -----')
        for i in range(8):
            lhs, rhs = (
                self.galaxy.quadrants[(i, 0)].name[:-2],
                self.galaxy.quadrants[(i, 4)].name[:-2],
            )
            print(f' {i + 1}   {lhs.center(23)} {rhs.center(23)}')
            print('     ----- ----- ----- ----- ----- ----- ----- -----')
        print()
