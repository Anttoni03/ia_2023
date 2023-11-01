import copy

from practica1.entorn import TipusCasella
from practica1 import agent


class Estat:

    def __init__(self, tablero, pare=None, accions_previes=None, alpha=float('-inf'), beta=float('inf')):
        self.tauler = tablero
        self.pare = pare

        self.pes = 0
        self.heuristica = 0

        self.alpha = alpha
        self.beta = beta
        self.valor = 0

        if accions_previes is None:
            accions_previes = []
        self.accions_previes = accions_previes

    def __eq__(self, other):
        for i in range(len(self.tauler)):
            for j in range(len(self.tauler[0])):
                if self.tauler[i][j] is not other.tauler[i][j]:
                    return False
        return True

    def __lt__(self, other):
        return self.cost_total < other.cost_total

    def __le__(self, other):
        return self.cost_total <= other.cost_total

    def heretar_a_b(self):
        if self.pare is not None:
            self.alpha = self.pare.alpha
            self.beta = self.pare.beta

    @property
    def accions_possibles(self):
        lista = list(range(len(self.tauler)))
        return [(x, y) for x in lista for y in lista]

    def calcular_heuristica(self, tipus: TipusCasella):
        max_en_linea = 0
        max_seguidas = 0
        max_en_linea_contrari = 0
        max_seguidas_contrari = 0
        tipus_contrari = TipusCasella.CARA if tipus is TipusCasella.CREU else TipusCasella.CREU
        for i in range(len(self.tauler)):

            max_en_linea, max_seguidas = devolver_máximos((max_en_linea, max_seguidas),
                                                          self.contar_recto(0, i, tipus, False))
            max_en_linea, max_seguidas = devolver_máximos((max_en_linea, max_seguidas),
                                                          self.contar_recto(i, 0, tipus, True))


            if i < len(self.tauler) - 3:
                # print(f"A1 {i}")
                max_en_linea, max_seguidas = devolver_máximos((max_en_linea, max_seguidas),
                                                              self.contar_diagonal(0, i, tipus, True))
                # print(f"A2 {i}")
                max_en_linea, max_seguidas = devolver_máximos((max_en_linea, max_seguidas),
                                                              self.contar_diagonal(i, 0, tipus, True))
                # print(f"A3 {i}")
                max_en_linea, max_seguidas = devolver_máximos((max_en_linea, max_seguidas),
                                                              self.contar_diagonal(i, len(self.tauler)-1, tipus, False))

            if i > 2:
                # print(f"A4 {i}")
                max_en_linea, max_seguidas = devolver_máximos((max_en_linea, max_seguidas),
                                                              self.contar_diagonal(0, i, tipus, False))


            max_en_linea_contrari, max_seguidas_contrari = devolver_máximos(
                (max_en_linea_contrari, max_seguidas_contrari),
                self.contar_recto(0, i, tipus_contrari, False))
            max_en_linea_contrari, max_seguidas_contrari = devolver_máximos(
                (max_en_linea_contrari, max_seguidas_contrari),
                self.contar_recto(i, 0, tipus_contrari, True))

            if i < len(self.tauler) - 3:
                # print(f"B1 {i}")
                max_en_linea_contrari, max_seguidas_contrari = devolver_máximos(
                    (max_en_linea_contrari, max_seguidas_contrari),
                    self.contar_diagonal(0, i, tipus_contrari, True))
                # print(f"B2 {i}")
                max_en_linea_contrari, max_seguidas_contrari = devolver_máximos(
                    (max_en_linea_contrari, max_seguidas_contrari),
                    self.contar_diagonal(i, 0, tipus_contrari, True))
                # print(f"B3 {i}")
                max_en_linea_contrari, max_seguidas_contrari = devolver_máximos(
                    (max_en_linea_contrari, max_seguidas_contrari),
                    self.contar_diagonal(i, len(self.tauler)-1, tipus_contrari, False))

            if i > 2:
                # print(f"B4 {i}")
                max_en_linea_contrari, max_seguidas_contrari = devolver_máximos(
                    (max_en_linea_contrari, max_seguidas_contrari),
                    self.contar_diagonal(0, i, tipus_contrari, False))

        # print(f"{str(self)}\n{agent.COL_DEBUG}té max en linea: {agent.COL_DEF}{max_en_linea}{agent.COL_DEBUG} i seguides: {agent.COL_DEF}{max_seguidas}{agent.COL_DEBUG}\n"
              # f"i max en linea contrari: {agent.COL_DEF}{max_en_linea_contrari}{agent.COL_DEBUG} i seguides contrari: {agent.COL_DEF}{max_seguidas_contrari}")

        res = max_en_linea - max_en_linea_contrari
        res += (max_seguidas - max_seguidas_contrari) * 5
        if max_seguidas == 3:
            res += 10
        if max_seguidas >= 4:
            res += 20

        if max_seguidas_contrari == 2:
            res -= 10
        if max_seguidas_contrari == 3:
            res -= 20
        if max_seguidas_contrari >= 4:
            res -= 30

        self.heuristica = res
        # print(f"{agent.COL_DEBUG}cost: {agent.COL_DEF}{self.cost_total}{agent.COL_DEBUG} per jugador {agent.COL_DEF}{tipus}\n")

    def set_valor(self, tipus):
        self.calcular_heuristica(tipus)
        self.valor = self.cost_total

    @property
    def cost_total(self) -> int:
        return self.heuristica + self.pes

    def genera_fill(self, tipus: TipusCasella):

        estats_generats = []

        for accio in self.accions_possibles:
            nou_estat = copy.deepcopy(self)
            nou_estat.pare = self

            x, y = accio
            if nou_estat.tauler[x][y] is TipusCasella.LLIURE:
                nou_estat.tauler[x][y] = tipus
                nou_estat.accions_previes.append(accio)

                nou_estat.pes -= 1
                nou_estat.calcular_heuristica(tipus)

                estats_generats.append(nou_estat)

        return estats_generats

    def es_meta(self) -> bool:
        for x in range(len(self.tauler)):
            for y in range(len(self.tauler[0])):

                if self.tauler[x][y] is TipusCasella.LLIURE:
                    continue

                if y < len(self.tauler) - 3:
                    if self.check_recto(x, y, self.tauler[x][y], True):
                        return True

                    direccio = 0
                    if not (x < len(self.tauler) - 3):
                        direccio = -1
                    if not (x >= 3):
                        direccio = 1
                    if self.check_diagonal(y, x, self.tauler[x][y], direccio):
                        return True

                if x < len(self.tauler) - 3:
                    if self.check_recto(x, y, self.tauler[x][y], False):
                        return True

        return False

    def check_recto(self, x: int, y: int, tipus: TipusCasella, horizontal: bool = False) -> bool:
        contar = 0
        while True:
            if self.tauler[x][y] is not tipus:
                return False
            else:
                contar += 1

            if contar == 4:
                return True

            if not horizontal:
                x += 1
            else:
                y += 1

    def check_diagonal(self, x: int, y: int, tipus: TipusCasella, sentit: int = 0) -> bool:
        contar1 = 0
        contar2 = 0
        bool1 = sentit == 0 or sentit == 1
        bool2 = sentit == 0 or sentit == -1
        x1 = x
        y1 = y
        x2 = x
        y2 = y
        while True:
            """
            print(f"x1,y1: {(x1,y1)}\tx2,y2:{(x2,y2)}\tsentit: {sentit}\tcontar1: {contar1}\tcontar2: {contar2}")
            if sentit == 0 or sentit == 1:
                print(self.str_position((x1, y1)))
            if sentit == 0 or sentit == -1:
                print(self.str_position((x2, y2)))
            """

            if self.tauler[y1][x1] is not tipus:
                bool1 = False
            if self.tauler[y2][x2] is not tipus:
                bool2 = False

            if sentit == -1 and not bool2:
                return False
            elif sentit == 1 and not bool1:
                return False
            elif sentit == 0 and not bool1 and not bool2:
                return False

            if sentit == -1 or sentit == 0:
                contar2 += 1
            if sentit == 1 or sentit == 0:
                contar1 += 1

            if contar1 == 4:
                return True
            if contar2 == 4:
                return True

            if bool1:
                x1 += 1
                y1 += 1
            if bool2:
                x2 += 1
                y2 -= 1

        return False

    def contar_recto(self, x: int, y: int, tipus: TipusCasella, horizontal: bool = False) -> (int, int):
        contador = 0
        contador_max = 0
        contador_nou = 0
        seguit = False

        for i in range(len(self.tauler)):
            casilla = self.tauler[i][x] if horizontal else self.tauler[y][i]
            if casilla is tipus:
                contador += 1
                seguit = True
                contador_nou += 1
            else:
                if seguit:
                    contador_max = max(contador_max, contador_nou)
                    contador_nou = 0
                    seguit = False

        if seguit:
            contador_max = max(contador_max, contador_nou)

        return (contador, contador_max)

    def contar_diagonal(self, x: int, y: int, tipus: TipusCasella, derecha: bool = True) -> (int, int):
        contador = 0
        contador_max = 0
        contador_nou = 0
        seguit = False
        x1 = x
        y1 = y

        while x1 < len(self.tauler) and y1 < len(self.tauler) and y1 >= 0:

            casilla = self.tauler[y1][x1]

            # print(f"{' '*(x1+y1)}{'X' if casilla is TipusCasella.CREU else 'C' if casilla is TipusCasella.CARA else '-'}")

            if casilla is tipus:
                contador += 1
                seguit = True
                contador_nou += 1
            else:
                if seguit:
                    contador_max = max(contador_max, contador_nou)
                    contador_nou = 0
                    seguit = False
            x1 += 1
            y1 += 1 if derecha else -1

        # print()
        if seguit:
            contador_max = max(contador_max, contador_nou)

        return (contador, contador_max)

    def __str__(self):
        txt = ""
        for x in range(len(self.tauler)):
            for y in range(len(self.tauler[0])):
                if self.tauler[y][x] is TipusCasella.LLIURE:
                    txt += "- "
                elif self.tauler[y][x] is TipusCasella.CARA:
                    txt += f"{agent.COL_BLUE}C {agent.COL_DEF}"
                else:
                    txt += f"{agent.COL_RED}X {agent.COL_DEF}"
            if x != len(self.tauler) - 1:
                txt += "\n"
        return txt

    def str_position(self, pos=(-1, -1)):
        txt = ""
        for x in range(len(self.tauler)):
            for y in range(len(self.tauler[0])):
                if self.tauler[y][x] is TipusCasella.LLIURE:
                    txt += f"{agent.COL_DEBUG}-" if pos == (x, y) else f"{agent.COL_DEF}-"
                elif self.tauler[y][x] is TipusCasella.CARA:
                    txt += f"{agent.COL_DEBUG}C" if pos == (x, y) else f"{agent.COL_BLUE}C"
                else:
                    txt += f"{agent.COL_DEBUG}X" if pos == (x, y) else f"{agent.COL_RED}X"

                txt += f" {agent.COL_DEF}"
            if x != len(self.tauler) - 1:
                txt += "\n"
        return txt


def devolver_máximos(valores1, valores2):
    temp11, temp12 = valores1
    temp21, temp22 = valores2
    max1 = max(temp11, temp21)
    max2 = max(temp12, temp22)
    return max1, max2
