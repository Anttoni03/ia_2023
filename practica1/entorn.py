import enum

from ia_2022 import entorn


class SENSOR(enum.Enum):
    TAULELL = 0
    MIDA = 1


class TipusCasella(enum.Enum):
    LLIURE = 0
    CREU = 1
    CARA = 2


class Accio(entorn.Accio, enum.Enum):
    ESPERAR = 0
    POSAR = 1
