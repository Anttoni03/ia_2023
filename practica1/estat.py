import copy

from practica1.entorn import TipusCasella
from practica1 import agent


class Estat:

    def __init__(self, taulell, pare=None, accions_previes=None, alpha=float('-inf'), beta=float('inf')):
        """
        Constructor de la classe Estat, que genera un estat del joc a
        partir d'un taulell de TipusCasella.

        Està preparat per tenir alpha i beta, enregistra el pare i les accions
        prèvies per arribar al propi estat
        """
        self.tauler = taulell
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
        """
        Mètode que hereta forsosament l'alpha i beta del node pare
        """
        if self.pare is not None:
            self.alpha = self.pare.alpha
            self.beta = self.pare.beta

    @property
    def accions_possibles(self):
        """
        Propietat que retorna la llista de posicions possibles al taulell
        """
        lista = list(range(len(self.tauler)))
        return [(x, y) for x in lista for y in lista]

    def calcular_heuristica(self, tipus: TipusCasella):
        """
        Mètode que asigna forsosament l'heurística a la variable self.heuristica.

        Quan més alt el valor, millor per al jugador 'tipus'. El càlcul en general és:
        heruistica = max_en_linea - max_en_linea_contrari
        heruistica += (max_seguidas - max_seguidas_contrari) * 5

        si max_seguides és 3 heurística suma 10 i si és 4 o més suma 20

        si max_seguides_contrari és 2 resta 10, si és 3 resta 20, i si és 40 o més 30

        D'aquesta manera l'heurística és alta amb estats amb el jugador 'tipus'
        amb 4 fitxes connectades
        """

        max_en_linea = 0
        max_seguidas = 0
        max_en_linea_contrari = 0
        max_seguidas_contrari = 0
        tipus_contrari = TipusCasella.CARA if tipus is TipusCasella.CREU else TipusCasella.CREU

        for i in range(len(self.tauler)):

            # es comproven les fitxes de lines verticals
            max_en_linea, max_seguidas = devolver_máximos((max_en_linea, max_seguidas),
                                                          self.contar_recto(0, i, tipus, False))
            # es comproven les fitxes de lines horitzontals
            max_en_linea, max_seguidas = devolver_máximos((max_en_linea, max_seguidas),
                                                          self.contar_recto(i, 0, tipus, True))
            # es comproven les fitxes de lines diagonals
            if i < len(self.tauler) - 3:
                max_en_linea, max_seguidas = devolver_máximos((max_en_linea, max_seguidas),
                                                              self.contar_diagonal(0, i, tipus, True))
                max_en_linea, max_seguidas = devolver_máximos((max_en_linea, max_seguidas),
                                                              self.contar_diagonal(i, 0, tipus, True))
                max_en_linea, max_seguidas = devolver_máximos((max_en_linea, max_seguidas),
                                                              self.contar_diagonal(i, len(self.tauler)-1, tipus, False))
            if i > 2:
                max_en_linea, max_seguidas = devolver_máximos((max_en_linea, max_seguidas),
                                                              self.contar_diagonal(0, i, tipus, False))

            # es comproven les fitxes contràries de lines verticals
            max_en_linea_contrari, max_seguidas_contrari = devolver_máximos(
                (max_en_linea_contrari, max_seguidas_contrari),
                self.contar_recto(0, i, tipus_contrari, False))
            # es comproven les fitxes contràries de lines horitzontals
            max_en_linea_contrari, max_seguidas_contrari = devolver_máximos(
                (max_en_linea_contrari, max_seguidas_contrari),
                self.contar_recto(i, 0, tipus_contrari, True))
            # es comproven les fitxes contràries de lines diagonals
            if i < len(self.tauler) - 3:
                max_en_linea_contrari, max_seguidas_contrari = devolver_máximos(
                    (max_en_linea_contrari, max_seguidas_contrari),
                    self.contar_diagonal(0, i, tipus_contrari, True))
                max_en_linea_contrari, max_seguidas_contrari = devolver_máximos(
                    (max_en_linea_contrari, max_seguidas_contrari),
                    self.contar_diagonal(i, 0, tipus_contrari, True))
                max_en_linea_contrari, max_seguidas_contrari = devolver_máximos(
                    (max_en_linea_contrari, max_seguidas_contrari),
                    self.contar_diagonal(i, len(self.tauler)-1, tipus_contrari, False))
            if i > 2:
                max_en_linea_contrari, max_seguidas_contrari = devolver_máximos(
                    (max_en_linea_contrari, max_seguidas_contrari),
                    self.contar_diagonal(0, i, tipus_contrari, False))

        # càlculs finals de com marca l'heurística
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

    def set_valor(self, tipus):
        """
        Mètode per enregistrar el valor de la heurística al valor, per usar en minimax
        """
        self.calcular_heuristica(tipus)
        self.valor = self.cost_total

    @property
    def cost_total(self) -> int:
        """
        Propietat per retornar el cost total
        """
        return self.heuristica + self.pes

    def genera_fill(self, tipus: TipusCasella):
        """
        Mètode per generar els fills depenent de les accions possibles
        i els estats als quals es pot arribar amb les accions.
        """
        estats_generats = []

        # genera un fill per a cada acció, o al manco ho intenta
        for accio in self.accions_possibles:
            nou_estat = copy.deepcopy(self)
            nou_estat.pare = self

            x, y = accio

            # només continua endavant si la casella que es vol possar és buida
            if nou_estat.tauler[x][y] is TipusCasella.LLIURE:
                nou_estat.tauler[x][y] = tipus
                nou_estat.accions_previes.append(accio)

                nou_estat.pes -= 1
                nou_estat.calcular_heuristica(tipus)

                estats_generats.append(nou_estat)

        return estats_generats

    def es_meta(self) -> bool:
        """
        Mètode que retorna si l'estat és considerat final, és a dir, amb
        4 fitxes o més seguides
        """
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
        """
        Mètode que comprova si hi han 4 fitxes 'tipus' seguides a alguna
        linia del taulell en vertical o horitzontal
        """
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
        """
        Mètode que comprova si hi han 4 fitxes 'tipus' seguides a alguna
        linia del taulell en vertical o horitzontal
        """

        contar1 = 0
        contar2 = 0
        bool1 = sentit == 0 or sentit == 1
        bool2 = sentit == 0 or sentit == -1
        x1 = x
        y1 = y
        x2 = x
        y2 = y
        while True:
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
        """
        Mètode que compta les fitxes 'tipus' d'alguna linia i retorna una
        tupla amb els valors de: (fitxes, màxim fitxes seguides)
        Pot cercar en vertical i horitzontal
        """

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
        """
        Mètode que compta les fitxes 'tipus' d'alguna linia i retorna una
        tupla amb els valors de: (fitxes, màxim fitxes seguides)
        Fa la cerca en diagonal cap a la dreta o cap a l'esquerra
        """
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
        """
        Mètode que sobreescriu l'impresió en text de l'estat.
        El retorna amb l'estil de(exemple 5x5):
        - - - - -
        - - X X -
        - - - C -
        - X - C -
        - - - C -
        """
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
        """
        Mètode similar a __str__ però es pot indicar una posició (x,y),
        on aquesta coordenada del taulell es remarcarà amb un color groc.
        """
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
    """
    Funció auxiliar feta per retornar el major dels elements de
    tuples en parells i deixar-ho com (x, y)

    Si les tuples son (a, b), (c, d), compararà
    a amb c i ho retornarà com x, i també compararà
    b amb d i ho retornarà com y, fent (x, y)
    """
    temp11, temp12 = valores1
    temp21, temp22 = valores2
    max1 = max(temp11, temp21)
    max2 = max(temp12, temp22)
    return max1, max2
