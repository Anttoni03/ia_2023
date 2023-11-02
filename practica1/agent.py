"""
ClauPercepcio:
    POSICIO = 0
    OLOR = 1
    PARETS = 2
"""
import queue
import sys
import time

from ia_2022 import entorn
from practica1 import joc
from practica1.estat import Estat
from practica1.entorn import Accio, SENSOR, TipusCasella

"""
Profunditat = 1
A* = 2
Minimax = 3 (TWO_PLAYERS = True)
"""
TIPUS_CERCA = 3
DEBUG = False

COL_DEF = "\033[0m"
COL_ACT = "\033[32m"
COL_DEBUG = "\033[33m"
COL_BLUE = "\033[34m"
COL_RED = "\033[31m"

tiempo_inicial = 0
tiempo_final = 0

tiempo_total = 0
estados_totales = 1
kb_totales = 0

class Agent(joc.Agent):
    def __init__(self, nom):
        super(Agent, self).__init__(nom)
        self.__accions = None
        self.__i = -1

    def pinta(self, display):
        pass

    def actua(
            self, percepcio: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:

        if self.__accions is None and DEBUG:
            print(f"{COL_DEBUG}La mida és {percepcio[SENSOR.MIDA]}{COL_DEF}")

        if TIPUS_CERCA == 3:
            taulell = percepcio[SENSOR.TAULELL]
            if not Estat(taulell).es_meta():
                self.__accions = self.elegir_cerca(taulell, TIPUS_CERCA)
            else:
                self.__accions = []
        else:
            if self.__accions is None:
                taulell = percepcio[SENSOR.TAULELL]
                self.__accions = self.elegir_cerca(taulell, TIPUS_CERCA)

        if TIPUS_CERCA == 1 or TIPUS_CERCA == 2:
            self.__i += 1
            if self.__i < len(self.__accions):
                if DEBUG:
                    print(f"{COL_DEBUG}El estado es{COL_DEF}\n{str(Estat(percepcio[SENSOR.TAULELL]))}")
                    print(f"{COL_ACT}Accion que hace {self.__accions[self.__i]}{COL_DEF}")
                return Accio.POSAR, self.__accions[self.__i]
            else:
                if DEBUG:
                    print(str(Estat(percepcio[SENSOR.TAULELL])))
                    print(f"{COL_ACT}PARADO{COL_DEF}")
                return Accio.ESPERAR, None
        else:
            if len(self.__accions) != 0:
                if DEBUG:
                    print(f"{COL_DEBUG}estat previ és{COL_DEF}\n{str(Estat(percepcio[SENSOR.TAULELL]))}\n"
                          f"{COL_DEBUG}li toca a {COL_BLUE if self.jugador is TipusCasella.CARA else COL_RED}"
                          f"{self.jugador}{COL_DEF}")
                if not isinstance(self.__accions, list):
                    self.__accions = [self.__accions]
                if DEBUG:
                    print(f"{COL_ACT}Y la accion que hace es {self.__accions[0]}{COL_DEF}")

                return Accio.POSAR, self.__accions[0]
            else:
                if DEBUG:
                    print(f"{COL_ACT}PARADO{COL_DEF}")
                return Accio.ESPERAR, None

    def elegir_cerca(self, taulell, opcio):
        global tiempo_total, kb_totales

        if kb_totales == 0:
            kb_totales = sys.getsizeof(Estat(taulell))
        tiempo_inicial = time.time()
        res = None
        if opcio == 1:
            res = self.cerca_profunditat(taulell)
            tiempo_final = time.time()
            print(f"{COL_DEBUG}CERCA PROFUNDITAT{COL_DEF}")
        elif opcio == 2:
            res = self.cerca_a_estrella(taulell)
            tiempo_final = time.time()
            print(f"{COL_DEBUG}CERCA A*{COL_DEF}")
        elif opcio == 3:
            profunditat = 3
            res = self.cerca_min_i_max(Estat(taulell), 0, profunditat)
            tiempo_final = time.time()
            print(f"{COL_DEBUG}CERCA MINIMAX(PROFUNDITAT {profunditat}){COL_DEF}")

        tiempo_total += (tiempo_final - tiempo_inicial)
        print(f"{COL_DEBUG}Temps de cerca: {(tiempo_total) * 1000}ms{COL_DEF}")
        print(f"{COL_DEBUG}Estats generats: {estados_totales} = {kb_totales}B{COL_DEF}\n")
        return res

    def cerca_profunditat(self, taulell):
        global estados_totales, kb_totales

        oberts = [Estat(taulell)]
        tancats = []

        while len(oberts) != 0:
            estat = oberts.pop()
            if estat.es_meta():
                return estat.accions_previes
            else:
                successors = estat.genera_fill(self.jugador)
                tancats.append(estat)

                for successor in successors:
                    estados_totales += 1
                    kb_totales += sys.getsizeof(successor)
                    if successor not in tancats:
                        oberts.append(successor)

        return None

    def cerca_a_estrella(self, taulell):
        global estados_totales, kb_totales

        oberts = queue.PriorityQueue()
        estat_inicial = Estat(taulell)
        estat_inicial.calcular_heuristica(self.jugador)
        oberts.put((-estat_inicial.cost_total, estat_inicial))
        tancats = []

        while not oberts.empty():
            prioritat, estat = oberts.get()
            if estat.es_meta():
                return estat.accions_previes
            else:
                successors = estat.genera_fill(self.jugador)
                tancats.append(estat)

                for successor in successors:
                    estados_totales += 1
                    kb_totales += sys.getsizeof(successor)
                    if successor not in tancats:
                        oberts.put((-successor.cost_total, successor))

        return None

    def cerca_min_i_max(self, estat, pas: int = 0, profunditat: int = 3):
        global estados_totales, kb_totales

        if pas >= profunditat - 1:  # no hauria d'arribar aquí
            return None

        is_max = pas % 2 == 0
        if is_max:
            jugador = self.jugador
        else:
            jugador = TipusCasella.CARA if self.jugador is TipusCasella.CREU else TipusCasella.CREU

        successors = estat.genera_fill(jugador)
        if len(successors) == 0:
            return None
        estat.heretar_a_b()
        estat.valor = float('-inf') if is_max else float('inf')
        estat_fill = successors[0]

        if pas >= profunditat - 2 and DEBUG:
            print(f"{COL_DEBUG}Como ha llegado al penúltimo nivel, genera los {len(successors)} estados{COL_DEF}")

        for succ in successors:
            estados_totales += 1
            kb_totales += sys.getsizeof(succ)
            if pas >= profunditat - 2:
                succ.set_valor(self.jugador)
            else:
                self.cerca_min_i_max(succ, pas + 1, profunditat)

            if not is_max:
                if succ.valor < estat.valor:
                    estat.valor = succ.valor
                    estat_fill = succ
                estat.beta = min(succ.beta, succ.valor)
            else:
                if succ.valor > estat.valor:
                    estat.valor = succ.valor
                    estat_fill = succ
                estat.alpha = max(succ.alpha, succ.valor)

            if estat.alpha >= estat.beta:
                break

        if DEBUG:
            print(f"{COL_DEBUG}-----------\nEl estado al que va a ir\n{COL_DEF}{str(estat)}{COL_DEBUG}\nes\n{COL_DEF}{str(estat_fill)}{COL_DEBUG}\ncon valor {COL_DEF}{estat_fill.cost_total}{COL_DEBUG}\n-----------{COL_DEF}")

        return estat_fill.accions_previes
