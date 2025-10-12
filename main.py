from math import floor
from random import randint

from enterprise import Enterprise
from galaxy import Galaxy

TITLE_PADDING_COMPONENTS_TOP = ['' for _ in range(11)]
TITLE_ENTERPRISE_COMPONENTS = [
    "                                    ,------*------,",
    "                    ,-------------   '---  ------'",
    "                     '-------- --'      / /",
    "                         ,---' '-------/ /--,",
    "                          '----------------'",
    "",
    "                    THE USS ENTERPRISE --- NCC-1701",
]
TITLE_PADDING_COMPONENTS_BOTTOM = ['' for _ in range(5)]

TITLE = '\n'.join(
    TITLE_PADDING_COMPONENTS_TOP
    + TITLE_ENTERPRISE_COMPONENTS
    + TITLE_PADDING_COMPONENTS_BOTTOM
)

STRANDED_MESSAGE = '\n'.join([
    "** FATAL ERROR **   YOU'VE JUST STRANDED YOUR SHIP IN SPACE",
    'YOU HAVE INSUFFICIENT MANEUVERING ENERGY, AND SHIELD CONTROL',
    'IS PRESENTLY INCAPABLE OF CROSS-CIRCUITING TO ENGINE ROOM!!',
])

print(TITLE)

galaxy = Galaxy()
current_quadrant_coordinates = (randint(0, 7), randint(0, 7))
current_sector = (randint(0, 7), randint(0, 7))
current_quadrant = galaxy.quadrants[current_quadrant_coordinates]

start_date = randint(20, 39) * 100
duration = max(randint(0, 9) + 25, galaxy.klingon_count + 1)
end_date = start_date + duration

shields = 0

start_date = galaxy.start_date
duration = galaxy.duration
end_date = galaxy.end_date

orders_warship_text = (
    f'THE {galaxy.initial_klingon_count} KLINGON '
    f'WARSHIP{'S' if galaxy.initial_klingon_count != 1 else ''}'
)
orders_starbase_text = (
    f'{'ARE' if galaxy.initial_starbase_count != 1 else 'IS'} '
    f'{galaxy.initial_starbase_count} '
    f'STARBASE{'S' if galaxy.initial_starbase_count != 1 else ''}'
)
orders_components = [
    f'DESTROY {orders_warship_text} WHICH HAVE INVADED',
    f'THE GALAXY BEFORE THEY CAN ATTACK FEDERATION HEADQUARTERS',  # noqa: F541
    f'ON STARDATE {end_date}. THIS GIVES YOU {duration} DAYS. THERE',
    f'{orders_starbase_text} IN THE GALAXY FOR RESUPPLYING YOUR SHIP.',
]

print('YOUR ORDERS ARE AS FOLLOWS:')
print('\n'.join(['    ' + x.center(57) for x in orders_components]))
print()

enterprise = Enterprise(galaxy)
while not enterprise.destroyed and not enterprise.resigned:
    enterprise.handle_command(input('ENTER A COMMAND: ').upper().strip())
    if galaxy.current_date >= galaxy.end_date or galaxy.klingon_count == 0:
        break
    elif enterprise.fired:
        break

final_klingon_count = galaxy.klingon_count
if enterprise.resigned:
    print((
        f'THERE {'WERE' if galaxy.klingon_count != 1 else 'WAS'} '
        f'{galaxy.klingon_count} KLINGON WARSHIP'
        f'{'S' if galaxy.klingon_count != 1 else ''} LEFT AT'
    ))
    print('THE END OF YOUR MISSION.')
elif enterprise.destroyed:
    print((
        '\nTHE ENTERPRISE HAS BEEN DESTROYED.  THE FEDERATION '
        'WILL BE CONQUERED'
    ))
    print(f'IT IS STARDATE {floor(galaxy.current_date)}')
    print((
        f'THERE {'WERE' if final_klingon_count != 1 else 'WAS'} '
        f'{final_klingon_count} KLINGON WARSHIP'
        f'{'S' if final_klingon_count != 1 else ''} LEFT AT'
    ))
    print('THE END OF YOUR MISSION.')
elif galaxy.current_date >= galaxy.end_date and final_klingon_count > 0:
    print(
        f'IT IS STARDATE {floor(galaxy.current_date)}.  YOU ARE OUT OF TIME!',
    )
    print((
        f'THERE {'WERE' if final_klingon_count != 1 else 'WAS'} '
        f'{final_klingon_count} KLINGON WARSHIP'
        f'{'S' if final_klingon_count != 1 else ''} LEFT AT'
    ))
    print('THE END OF YOUR MISSION.')
else:
    efficiency = galaxy.initial_klingon_count
    efficiency /= galaxy.current_date - galaxy.start_date
    efficiency = 1000.0 * pow(efficiency, 2)
    print('CONGRULATIONS, CAPTAIN!  THE LAST KLINGON BATTLE CRUISER')
    print('MENACING THE FDERATION HAS BEEN DESTROYED.')
    print()
    print(f'YOUR EFFICIENCY RATING IS {efficiency:.2f}')
exit()
