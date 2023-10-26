"""
ClauPercepcio:
    POSICIO = 0
    OLOR = 1
    PARETS = 2
"""
import queue

from ia_2022 import entorn
from practica1 import joc
from practica1.estat import Estat
from practica1.entorn import Accio, SENSOR, TipusCasella

"""
Profunditat = 1
A* = 2
Minimax = 3
"""
TIPUS_CERCA = 3
TWO_PLAYERS = True
DEBUG = False

COL_DEF = "\033[0m"
COL_ACT = "\033[32m"
COL_DEBUG = "\033[33m"
COL_BLUE = "\033[34m"
COL_RED = "\033[31m"


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

        if TWO_PLAYERS:
            taulell = percepcio[SENSOR.TAULELL]
            self.__accions = self.elegir_cerca(taulell, TIPUS_CERCA)
        else:
            if self.__accions is None:
                taulell = percepcio[SENSOR.TAULELL]
                self.__accions = self.elegir_cerca(taulell, TIPUS_CERCA)

        if not TWO_PLAYERS:
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
            if self.__accions is not None:
                if DEBUG:
                    print(
                        f"{COL_DEBUG}el estado previo es{COL_DEF}\n{str(Estat(percepcio[SENSOR.TAULELL]))}\n{COL_DEBUG} le toca a {COL_BLUE if self.jugador is TipusCasella.CARA else COL_RED}{self.jugador}{COL_DEF}")
                if not isinstance(self.__accions, list):
                    self.__accions = [self.__accions]

                if len(self.__accions) > 0:
                    if DEBUG:
                        print(f"{COL_ACT}Y la accion que hace es {self.__accions[0]}{COL_DEF}")
                    return Accio.POSAR, self.__accions[0]
                else:
                    return Accio.ESPERAR, None
            else:
                if DEBUG:
                    print(f"{COL_ACT}PARADO{COL_DEF}")
                return Accio.ESPERAR, None

    def elegir_cerca(self, taulell, opcio):
        if opcio == 1:
            return self.cerca_profunditat(taulell)
        elif opcio == 2:
            return self.cerca_a_estrella(taulell)
        elif opcio == 3:
            return self.cerca_min_i_max(Estat(taulell), 0, 3)

    def cerca_profunditat(self, taulell):
        oberts = [Estat(taulell)]
        tancats = []

        while len(oberts) != 0:
            estat = oberts.pop()
            if estat.es_meta():
                if DEBUG:
                    print(f"{COL_DEBUG}Cantidad de estados evaluados PROFUNDIDAD: {len(oberts)}\nacciones: {estat.accions_previes}\ny encontrado{COL_DEF}\n{str(estat)}")
                return estat.accions_previes
            else:
                successors = estat.genera_fill(self.jugador)
                tancats.append(estat)

                for successor in successors:
                    if successor not in tancats:
                        oberts.append(successor)

        return None

    def cerca_a_estrella(self, taulell):

        oberts = queue.PriorityQueue()
        estat_inicial = Estat(taulell)
        estat_inicial.calcular_heuristica(self.jugador)
        oberts.put((-estat_inicial.cost_total, estat_inicial))
        tancats = []

        while not oberts.empty():
            prioritat, estat = oberts.get()
            if estat.es_meta():
                if DEBUG:
                    print(f"{COL_DEBUG}Cantidad de estados evaluados A*: {oberts.qsize()}\nacciones: {estat.accions_previes}\ny encontrado{COL_DEF}\n{str(estat)}")
                return estat.accions_previes
            else:
                successors = estat.genera_fill(self.jugador)
                tancats.append(estat)

                for successor in successors:
                    if successor not in tancats:
                        oberts.put((-successor.cost_total, successor))

        return None

    def cerca_min_i_max(self, estat, pas: int = 0, profunditat: int = 4):

        if pas >= profunditat - 1:  # no hauria d'arribar aquí
            return

        is_max = pas % 2 == 0
        if is_max:
            jugador = self.jugador
        else:
            jugador = TipusCasella.CARA if self.jugador is TipusCasella.CREU else TipusCasella.CREU

        successors = estat.genera_fill(jugador)
        estat.heretar_a_b()
        estat.valor = -float('inf') if is_max else float('inf')
        estat_fill = successors[0]

        #print(f"{COL_DEBUG}El estado en paso {pas} es{COL_DEF}\n{str(estat)}")

        if pas >= profunditat - 2:
            print(f"{COL_DEBUG}Como ha llegado al penúltimo nivel, genera los {len(successors)} estados:{COL_DEF}")

        for succ in successors:
            if pas >= profunditat - 2:
                succ.set_valor()
                #print(f"{COL_DEBUG}Con valor {succ.cost_total} el estado es{COL_DEF}\n{str(succ)}")
            else:
                #print(f"Entra")
                self.cerca_min_i_max(succ, pas + 1, profunditat)

            if not is_max:
                if succ.valor < estat.valor:
                    estat_fill = succ
                estat.valor = min(estat.valor, succ.valor)
                estat.beta = min(succ.beta, succ.valor)
            else:
                if succ.valor > estat.valor:
                    estat_fill = succ
                estat.valor = max(estat.valor, succ.valor)
                estat.beta = max(succ.beta, succ.valor)

            if estat.alpha >= estat.beta:
                #print(f"{COL_DEBUG}PODA{COL_DEF}")
                break

        if pas == 0:
            pass#print(f"{COL_DEBUG}El estado al que va a ir tiene coste {estat_fill.cost_total}, és\n{COL_DEF}{str(estat_fill)}")
        return estat_fill.accions_previes
