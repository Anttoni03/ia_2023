import random

from ia_2022 import agent, entorn, joc
from monedes.entorn import AccionsMoneda, SENSOR


class Moneda(joc.JocNoGrafic):
    def __init__(self, agents: list[agent.Agent], random_order: bool = False):
        super(Moneda, self).__init__((1024, 512), agents, title="Casa")

        monedes = "CXCX "

        if random_order:
            monedes = ''.join(random.sample(monedes, len(monedes)))

        self.__monedes = monedes

    @staticmethod
    def __gira(caract: str):
        if caract == "C":
            return "X"
        elif caract == "X":
            return "C"
        else:
            return caract

    def __empty_pos(self) -> int:
        return self.__monedes.find(" ")

    def _aplica(self, accio: entorn.Accio, params=None, agent_actual=None) -> None:
        id_moneda = params
        monedes_aux = list(self.__monedes.upper())
        if accio is AccionsMoneda.DESPLACAR:
            if (self.__empty_pos() != (id_moneda - 1)) and (
                    self.__empty_pos() != (id_moneda + 1)
            ):
                raise joc.HasPerdut("Moneda una damunt l'altra")
            monedes_aux[id_moneda] = " "
            monedes_aux[self.__empty_pos()] = self.__monedes[id_moneda]
        elif accio is AccionsMoneda.BOTAR:
            if (self.__empty_pos() != (id_moneda - 2)) and (
                    self.__empty_pos() != (id_moneda + 2)
            ):
                raise joc.HasPerdut("Moneda una damunt l'altra")
            monedes_aux[id_moneda] = " "
            monedes_aux[self.__empty_pos()] = self.__gira(self.__monedes[id_moneda])
        elif accio is AccionsMoneda.GIRAR:
            monedes_aux[id_moneda] = self.__gira(self.__monedes[id_moneda])
        elif accio is not AccionsMoneda.RES:
            raise Exception(f"Acció no existent en aquest joc: {accio}")

        self.__monedes = "".join(monedes_aux)

    def _draw(self) -> None:
        print(self.__monedes)

    def percepcio(self) -> entorn.Percepcio:
        return entorn.Percepcio({SENSOR.MONEDES: self.__monedes})
