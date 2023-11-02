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
# afegits imports SENSOR y TipusCasella
from practica1.entorn import Accio, SENSOR, TipusCasella
# afegit import de la Classe Estat
from practica1.estat import Estat

# 1 = cerca profunditat
# 2 = cerca A*
# 3 = cerca Minimax
TIPUS_CERCA = 3
# booleà que indica si hi haurà o no missatges de Debug
DEBUG = False

# colors por defecte
COL_DEF = "\033[0m"
COL_ACT = "\033[32m"
COL_DEBUG = "\033[33m"
COL_BLUE = "\033[34m"
COL_RED = "\033[31m"

# variables de rendiment
tiempo_total = 0
estados_totales = 1
kb_totales = 0


class Agent(joc.Agent):
    def __init__(self, nom):
        """
        Constructor de la classe Agent

        Crea els agents que juguen al Connecta 4. Té les accions que ha de fer(__accions)
        i el pas que ha d'executar(__i)
        """
        super(Agent, self).__init__(nom)
        self.__accions = None
        self.__i = -1

    def pinta(self, display):
        pass

    def actua(
            self, percepcio: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        """
        El mètode d'actuació de l'agent.

        Segons el tipus de cerca genera una llista d'accions o acció a fer,
        i retorna l'acció que ha de retornar en cada moment.
        """

        # si la cerca és minimax, detecta el taulell i genera una cerca depenent d'aquest
        if TIPUS_CERCA == 3:
            taulell = percepcio[SENSOR.TAULELL]
            if not Estat(taulell).es_meta():
                self.__accions = self.elegir_cerca(taulell, TIPUS_CERCA)
            else:
                self.__accions = []
        # si la cerca no és minimax, només detecta el taulell i genera una cerca una vegada
        else:
            if self.__accions is None:
                taulell = percepcio[SENSOR.TAULELL]
                self.__accions = self.elegir_cerca(taulell, TIPUS_CERCA)

        # si la cerca no és minimax retorna l'acció del moment o ESPERAR si les ha passades totes
        if TIPUS_CERCA == 1 or TIPUS_CERCA == 2:
            self.__i += 1
            if self.__i < len(self.__accions):
                if DEBUG:
                    print(f"{COL_DEBUG}L'estat previ és{COL_DEF}\n{str(Estat(percepcio[SENSOR.TAULELL]))}")
                    print(f"{COL_ACT}L'acció que fa és {self.__accions[self.__i]}{COL_DEF}")
                return Accio.POSAR, self.__accions[self.__i]
            else:
                if DEBUG:
                    print(str(Estat(percepcio[SENSOR.TAULELL])))
                    print(f"{COL_ACT}ATURAT{COL_DEF}")
                return Accio.ESPERAR, None
        # si la cerca és minimax retorna
        else:
            if len(self.__accions) != 0:
                if DEBUG:
                    print(f"{COL_DEBUG}L'estat previ és{COL_DEF}\n{str(Estat(percepcio[SENSOR.TAULELL]))}\n"
                          f"{COL_DEBUG}Li toca a {COL_BLUE if self.jugador is TipusCasella.CARA else COL_RED}"
                          f"{self.jugador}{COL_DEF}"
                          f"{COL_ACT}I la acció que fa és {self.__accions[0]}{COL_DEF}")
                return Accio.POSAR, self.__accions[0]
            else:
                if DEBUG:
                    print(f"{COL_ACT}ATURAT{COL_DEF}")
                return Accio.ESPERAR, None

    def elegir_cerca(self, taulell, opcio):
        """
        Mètode que tria l'algorisme de cerca.

        Reb el taulell de joc i l'opció de la cerca.
        """
        global tiempo_total, kb_totales

        # actualitza les dades de rendiment
        if kb_totales == 0:
            kb_totales = sys.getsizeof(Estat(taulell))
        tiempo_inicial = time.time()
        tiempo_final = 0

        # defineix el resultat del mètode
        res = None

        # si l'opció és 1 es fa la cerca per profunditat
        if opcio == 1:
            res = self.cerca_profunditat(taulell)
            tiempo_final = time.time()
            print(f"{COL_DEBUG}CERCA PROFUNDITAT{COL_DEF}")
        # si l'opció és 2 es fa la cerca per A*
        elif opcio == 2:
            res = self.cerca_a_estrella(taulell)
            tiempo_final = time.time()
            print(f"{COL_DEBUG}CERCA A*{COL_DEF}")
        # si l'opció és 3 es fa la cerca per Minimax
        elif opcio == 3:
            profunditat = 3
            res = self.cerca_min_i_max(Estat(taulell), 0, profunditat)
            tiempo_final = time.time()
            print(f"{COL_DEBUG}CERCA MINIMAX(PROFUNDITAT {profunditat}){COL_DEF}")

        # es troba el temps final i les dades de rendiment de la cerca feta
        tiempo_total += (tiempo_final - tiempo_inicial)
        print(f"{COL_DEBUG}Temps de cerca: {round((tiempo_total) * 1000, 2)} ms{COL_DEF}")
        print(f"{COL_DEBUG}Estats generats: {estados_totales} = {kb_totales} B{COL_DEF}\n")

        # retorna la llista d'accions o acció a realitzar
        return res

    def cerca_profunditat(self, taulell):
        """
        Mètode de cerca en profunditat, a partir d'un taulell, l'inicial.
        """
        global estados_totales, kb_totales

        # estats oberts i tancats, iniciats amb l'estat inicial
        oberts = [Estat(taulell)]
        tancats = []

        # bucle que recorr els fills i va cercant l'estat final, a partir del darrer
        # element de la llista d'oberts
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
        """
        Mètode de cerca per A*, usant l'heurística dels estats.
        """
        global estados_totales, kb_totales

        # estats oberts i tancats, iniciats aquí amb l'ordre dels estats per l'heurística
        oberts = queue.PriorityQueue()
        estat_inicial = Estat(taulell)
        estat_inicial.calcular_heuristica(self.jugador)
        oberts.put((-estat_inicial.cost_total, estat_inicial))
        tancats = []

        # bucle que recorr els fills i va cercant l'estat final, a partir de l'element amb
        # més prioritat(heurística més baixa) de la llista d'oberts
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
        """
        Mètode de cerca d'un torn de l'agent amb Minimax

        Genera recursivament les 'profunditat' passes per trobar el millor següent
        estat per jugar

        :param estat: Estat des de el qual es parteix la cerca, és considerat max
        :param pas: Pas desde el qual es parteix la cerca, per defecte és 0
        :param profunditat: Nivell de profunditat que es vol arribar
        :return: L'acció a fer per arribar al següent estat més òptim
        """
        global estados_totales, kb_totales

        # no hauria d'arribar mai si el problema té solució, és un
        # limitador per aturar a la profunditat elegida
        if pas >= profunditat - 1:
            return None

        # 'is_max' registra si l'estat que està avaluant és del pas max o min
        is_max = pas % 2 == 0
        if is_max:
            jugador = self.jugador
        else:
            jugador = TipusCasella.CARA if self.jugador is TipusCasella.CREU else TipusCasella.CREU

        # es generen els fills i comença l'avaluació recursiva d'aquests
        successors = estat.genera_fill(jugador)
        if len(successors) == 0:
            return None
        estat.heretar_a_b()
        estat.valor = float('-inf') if is_max else float('inf')
        estat_fill = successors[0]

        if pas >= profunditat - 2 and DEBUG:
            print(f"{COL_DEBUG}Com ha arribat al penultim nivell, genera els {len(successors)} estats{COL_DEF}")

        for succ in successors:
            estados_totales += 1
            kb_totales += sys.getsizeof(succ)
            if pas >= profunditat - 2:
                succ.set_valor(self.jugador)
            else:
                self.cerca_min_i_max(succ, pas + 1, profunditat)

            # avaluació alpha beta de l'estat segons si el nivell és max o min
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

            # condició de poda si alpha és major o igual a beta
            if estat.alpha >= estat.beta:
                break

        if DEBUG:
            print(f"{COL_DEBUG}-----------\nL'estat al que anirà\n"
                  f"{COL_DEF}{str(estat)}{COL_DEBUG}\nés\n"
                  f"{COL_DEF}{str(estat_fill)}{COL_DEBUG}\n"
                  f"amb valor {COL_DEF}{estat_fill.cost_total}{COL_DEBUG}\n"
                  f"-----------{COL_DEF}")

        return estat_fill.accions_previes
