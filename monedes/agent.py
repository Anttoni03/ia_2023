""" Mòdul que conté l'agent per jugar al joc de les monedes.

Percepcions:
    ClauPercepcio.MONEDES
Solució:
    " XXXC"
"""
import copy
import queue

from ia_2022 import agent, entorn
from monedes import entorn as entorno

SOLUCIO = " XXXC"


class AgentMoneda(agent.Agent):
    def __init__(self):
        super().__init__(long_memoria=0)
        self.__oberts = None
        self.__tancats = None
        self.__accions = None
        self.__i = -1

    def pinta(self, display):
        print(self._posicio_pintar)

    def actua(
        self, percepcio: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:

        if self.__i == -1:
            self.__accions = self.cerca_general(percepcio[entorno.SENSOR.MONEDES])

        self.__i += 1
        if self.__i < len(self.__accions):
            return self.__accions[self.__i]
        else:
            return entorno.AccionsMoneda.RES, 0

    def cerca_general(self, text_monedes: str) -> list: #exit True / fracas False

        self.__oberts = queue.PriorityQueue()
        estat_inicial = Estat(text_monedes)
        self.__oberts.put((estat_inicial.cost_total, estat_inicial))
        self.__tancats = []

        while not self.__oberts.empty():
            estat_prioritat = self.__oberts.get()
            prioritat, estat = estat_prioritat

            # print(f"estado es {str(estat)}")
            if estat.es_meta():
                # print(f"tomaaaaaaaaa, metaaaaa")
                print(f"estado final es {str(estat)}")
                return estat.accions_previes
            else:
                successors = estat.genera_fill()
                self.__tancats.append(estat)

                for successor in successors:
                    if successor not in self.__tancats:
                        # print(f"\t> mete {successor} como sucesor")
                        self.__oberts.put((successor.cost_total, successor))

        return None

class Estat:

    def __init__(self, monedes : str, pare=None, accions_previes=None):

        if accions_previes is None:
            accions_previes = []

        self.monedes = monedes
        self.pare = pare
        self.pes = 0

        self.accions_previes = accions_previes

    def __eq__(self, other) -> bool:
        return self.monedes == other.monedes

    def __lt__(self, other):
        return self.cost_total < other.cost_total

    def __le__(self, other):
        return self.cost_total <= other.cost_total

    def es_meta(self) -> bool:
        return self.monedes == SOLUCIO

    @property
    def espai(self):
        return self.monedes.find(' ')

    @property
    def heuristica(self) -> int:
        estat_final = Estat(SOLUCIO)
        heur = abs(self.espai - estat_final.espai)
        for i in range(len(self.monedes)):
            if i == self.espai or i == estat_final.espai:
                continue

            if self.monedes[i] == estat_final.monedes[i]:
                heur += 1
        return heur

    @property
    def cost_total(self) -> int:
        return self.pes + self.heuristica

    def accio_desplasament(self, moneda: int):
        lletra = self.monedes[moneda]
        self.monedes = self.monedes.replace(" ", lletra)
        self.monedes = f"{self.monedes[:moneda]} {self.monedes[(moneda+1):]}"

    def accio_girar(self, moneda: int):
        nova_lletra = "C" if self.monedes[moneda] == "X" else "X"
        self.monedes = f"{self.monedes[:moneda]}{nova_lletra}{self.monedes[(moneda+1):]}"

    def accio_botar(self, moneda: int):
        self.accio_girar(moneda)
        self.accio_desplasament(moneda)

    def fill(self):
        nou_estat = copy.deepcopy(self)
        nou_estat.pare = (self)
        return nou_estat

    def genera_fill(self) -> list:

        estats_generats = []

        # generar fills amb la acció desplaçament
        if self.espai > 0 and self.espai < len(self.monedes)-1:
            nou_estat = self.fill()
            nou_estat.accio_desplasament(self.espai-1)
            nou_estat.accions_previes.append((entorno.AccionsMoneda.DESPLACAR, self.espai-1))
            nou_estat.pes += 1
            estats_generats.append(nou_estat)

            nou_estat = self.fill()
            nou_estat.accio_desplasament(self.espai + 1)
            nou_estat.accions_previes.append((entorno.AccionsMoneda.DESPLACAR, self.espai+1))
            nou_estat.pes += 1
            estats_generats.append(nou_estat)
        else:
            if self.espai > 0:
                nou_estat = self.fill()
                nou_estat.accio_desplasament(self.espai - 1)
                nou_estat.accions_previes.append((entorno.AccionsMoneda.DESPLACAR, self.espai - 1))
                nou_estat.pes += 1
                estats_generats.append(nou_estat)
            elif self.espai < len(self.monedes)-1:
                nou_estat = self.fill()
                nou_estat.accio_desplasament(self.espai + 1)
                nou_estat.accions_previes.append((entorno.AccionsMoneda.DESPLACAR, self.espai + 1))
                nou_estat.pes += 1
                estats_generats.append(nou_estat)

        # generar fills amb la acció girar
        for i in range(len(self.monedes)):
            if i == self.espai:
                continue

            nou_estat = self.fill()
            nou_estat.accio_girar(i)
            nou_estat.accions_previes.append((entorno.AccionsMoneda.GIRAR, i))
            nou_estat.pes += 2
            estats_generats.append(nou_estat)

        # generar fills amb la acció botar
        if self.espai > 1 and self.espai < len(self.monedes)-2:
            nou_estat = self.fill()
            nou_estat.accio_botar(self.espai-2)
            nou_estat.accions_previes.append((entorno.AccionsMoneda.BOTAR, self.espai - 2))
            nou_estat.pes += 3
            estats_generats.append(nou_estat)

            nou_estat = self.fill()
            nou_estat.accio_botar(self.espai + 2)
            nou_estat.accions_previes.append((entorno.AccionsMoneda.BOTAR, self.espai + 2))
            nou_estat.pes += 3
            estats_generats.append(nou_estat)
        else:
            nou_estat = self.fill()
            if self.espai > 1:
                nou_estat.accio_botar(self.espai - 2)
                nou_estat.accions_previes.append((entorno.AccionsMoneda.BOTAR, self.espai - 2))
                nou_estat.pes += 3
                estats_generats.append(nou_estat)
            elif self.espai < len(self.monedes)-2:
                nou_estat.accio_botar(self.espai + 2)
                nou_estat.accions_previes.append((entorno.AccionsMoneda.BOTAR, self.espai + 2))
                nou_estat.pes += 3
                estats_generats.append(nou_estat)

        return estats_generats


    def __str__(self):
        return (f"Monedes {self.monedes} | Accio {self.accions_previes}")


