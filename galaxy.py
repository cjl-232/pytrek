# Z$="                         "
# 330 DIM G(8,8),C(9,2),K(3,3),N(3),Z(8,8),D(8)
# 370 T=INT(RND(1)*20+20)*100:T0=T:T9=25+INT(RND(1)*10):D0=0:E=3000:E0=E
# 440 P=10:P0=P:S9=200:S=0:B9=2:K9=0:X$="":X0$=" IS "
# 470 DEF FND(D)=SQR((K(I,1)-S1)^2+(K(I,2)-S2)^2)
# 475 DEF FNR(R)=INT(RND(R)*7.98+1.01)
# 480 REM INITIALIZE ENTERPRIZE'S POSITION
# 490 Q1=FNR(1):Q2=FNR(1):S1=FNR(1):S2=FNR(1)
# 530 FORI=1TO9:C(I,1)=0:C(I,2)=0:NEXTI
# 540 C(3,1)=-1:C(2,1)=-1:C(4,1)=-1:C(4,2)=-1:C(5,2)=-1:C(6,2)=-1
# 600 C(1,2)=1:C(2,2)=1:C(6,1)=1:C(7,1)=1:C(8,1)=1:C(8,2)=1:C(9,2)=1
# 670 FORI=1TO8:D(I)=0:NEXTI
# 710 A1$="NAVSRSLRSPHATORSHEDAMCOMXXX"
# 810 REM SETUP WHAT EXHISTS IN GALAXY . . .
# 815 REM K3= # KLINGONS  B3= # STARBASES  S3 = # STARS
# 820 FORI=1TO8:FORJ=1TO8:K3=0:Z(I,J)=0:R1=RND(1)
# 850 IFR1>.98THENK3=3:K9=K9+3:GOTO980
# 860 IFR1>.95THENK3=2:K9=K9+2:GOTO980
# 870 IFR1>.80THENK3=1:K9=K9+1
# 980 B3=0:IFRND(1)>.96THENB3=1:B9=B9+1
# 1040 G(I,J)=K3*100+B3*10+FNR(1):NEXTJ:NEXTI:IFK9>T9THENT9=K9+1
# 1100 IFB9<>0THEN1200
# 1150 IFG(Q1,Q2)<200THENG(Q1,Q2)=G(Q1,Q2)+120:K9=K9+1
# 1160 B9=1:G(Q1,Q2)=G(Q1,Q2)+10:Q1=FNR(1):Q2=FNR(1)
# 1200 K7=K9:IFB9<>1THENX$="S":X0$=" ARE "
# 1230 PRINT"YOUR ORDERS ARE AS FOLLOWS:"
# 1240 PRINT"     DESTROY THE";K9;"KLINGON WARSHIPS WHICH HAVE INVADED"
# 1252 PRINT"   THE GALAXY BEFORE THEY CAN ATTACK FEDERATION HEADQUARTERS"
# 1260 PRINT"   ON STARDATE";T0+T9;"  THIS GIVES YOU";T9;"DAYS.  THERE";X0$
# 1272 PRINT"  ";B9;"STARBASE";X$;" IN THE GALAXY FOR RESUPPLYING YOUR SHIP"
# 1280 PRINT:REM PRINT"HIT ANY KEY EXCEPT RETURN WHEN READY TO ACCEPT COMMAND"

import itertools

from dataclasses import dataclass
from random import choice, randint, random

# 9040 G2$="ANTARES":GOTO9210
# 9050 G2$="RIGEL":GOTO9210
# 9060 G2$="PROCYON":GOTO9210
# 9070 G2$="VEGA":GOTO9210
# 9080 G2$="CANOPUS":GOTO9210
# 9090 G2$="ALTAIR":GOTO9210
# 9100 G2$="SAGITTARIUS":GOTO9210
# 9110 G2$="POLLUX":GOTO9210
# 9120 ONZ4GOTO9130,9140,9150,9160,9170,9180,9190,9200
# 9130 G2$="SIRIUS":GOTO9210
# 9140 G2$="DENEB":GOTO9210
# 9150 G2$="CAPELLA":GOTO9210
# 9160 G2$="BETELGEUSE":GOTO9210
# 9170 G2$="ALDEBARAN":GOTO9210
# 9180 G2$="REGULUS":GOTO9210
# 9190 G2$="ARCTURUS":GOTO9210
# 9200 G2$="SPICA"


def _get_quadrant_name(coords: tuple[int, int]):
    REGION_NAMES = [
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
    region = REGION_NAMES[coords[0] + int(coords[1] >= 4) * 8]
    match coords[1] % 4:
        case 0:
            return f'{region} I'
        case 1:
            return f'{region} II'
        case 2:
            return f'{region} III'
        case 3:
            return f'{region} IV'


class QuadrantMap:
    @dataclass
    class Klingon:
        energy: float

    def __init__(
            self,
            enterprise_sector: tuple[int, int],
            klingon_count: int,
            has_starbase: bool,
            star_count: int,
    ):
        empty_sectors = set(itertools.product(range(8), repeat=2))
        self.enterprise_sector = enterprise_sector
        empty_sectors.remove(enterprise_sector)
        self.klingons: dict[tuple[int, int], self.Klingon] = {}
        self.starbases: set[tuple[int, int]] = set()
        self.stars: set[tuple[int, int]] = set()
        for _ in range(klingon_count):
            sector = choice(list(empty_sectors))
            self.klingons[sector] = self.Klingon(200 * (0.5 + random()))
            empty_sectors.remove(sector)
        if has_starbase:
            sector = choice(list(empty_sectors))
            self.starbases.add(sector)
            empty_sectors.remove(sector)
        for _ in range(star_count):
            sector = choice(list(empty_sectors))
            self.stars.add(sector)
            empty_sectors.remove(sector)
        self.repair_factor = 0.5 * random()

    def get_empty_sectors(self, enterprise_sector: tuple[int, int]):
        result = set(itertools.product(range(8), repeat=2))
        result.remove(enterprise_sector)
        for position in self.klingons.keys():
            result.remove(position)
        for position in self.starbases:
            result.remove(position)
        for position in self.stars:
            result.remove(position)
        return list(result)

    def __str__(self):
        lines = [''] * 8
        for i in range(8):
            for j in range(8):
                sector = (i, j)
                if sector == self.enterprise_sector:
                    lines[i] += ' <*>'
                elif sector in self.klingons:
                    lines[i] += ' +K+'
                elif sector in self.starbases:
                    lines[i] += ' >!<'
                elif sector in self.stars:
                    lines[i] += '  * '
                else:
                    lines[i] += '    '
        return '\n'.join(lines)


class Quadrant:
    def __init__(self, name: str):
        self.name = name
        klingon_roll = random()
        if klingon_roll > 0.98:
            self.klingons = 3
        elif klingon_roll > 0.95:
            self.klingons = 2
        elif klingon_roll > 0.80:
            self.klingons = 1
        else:
            self.klingons = 0
        self.has_starbase = random() > 0.96
        self.stars = randint(1, 8)
        self.scanned = False

    def generate_local_map(self, enterprise_sector: tuple[int, int]):
        return QuadrantMap(
            enterprise_sector=enterprise_sector,
            klingon_count=self.klingons,
            has_starbase=self.has_starbase,
            star_count=self.stars,
        )


class Galaxy:
    def __init__(self):
        self.quadrants = {
            x: Quadrant(_get_quadrant_name(x))
            for x in itertools.product(range(8), repeat=2)
        }
        self.initial_klingon_count = self.klingon_count
        self.initial_starbase_count = self.starbase_count
        self.start_date = randint(20, 39) * 100
        self.duration = max(randint(0, 9) + 25, self.initial_klingon_count + 1)
        self.end_date = self.start_date + self.duration
        self.current_date = self.start_date
        if self.starbase_count == 0:
            insertion_coords = (randint(0, 7), randint(0, 7))
            if self.quadrants[insertion_coords].klingons < 2:
                self.quadrants[insertion_coords].klingons += 1
            self.quadrants[insertion_coords].has_starbase = True
            self.initial_starbase_count = 1

    @property
    def klingon_count(self):
        result = 0
        for quadrant in self.quadrants.values():
            result += quadrant.klingons
        return result

    @property
    def starbase_count(self):
        result = 0
        for quadrant in self.quadrants.values():
            if quadrant.has_starbase:
                result += 1
        return result

    @property
    def time_remaining(self):
        return int(self.end_date - self.current_date)
