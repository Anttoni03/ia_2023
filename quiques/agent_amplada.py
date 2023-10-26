




from ia_2022 import entorn
from quiques.agent import Barca, Estat
from quiques.entorn import AccionsBarca, SENSOR
from quiques.entorn import Lloc


class BarcaAmplada(Barca):
    def __init__(self):
        super(BarcaAmplada, self).__init__()
        self.__oberts = None
        self.__tancats = None
        self.__accions = self.cercaGeneralAmplada()
        self.__i = -1

    def actua(
            self, percepcio: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:

        self.__i += 1
        if (self.__i < len(self.__accions)):
            return AccionsBarca.MOURE, self.__accions[self.__i]
        else:
            return AccionsBarca.ATURAR, None


    def cercaGeneralAmplada(self): #exit True / fracas False

        self.__oberts = []
        self.__oberts.append(Estat(Lloc.ESQ, 3, 3))

        self.__tancats = []
        while len(self.__oberts) != 0:
            estat = self.__oberts.pop(0)
            # print(f"el estado es {str(estat)}")
            if estat.es_meta():
                # print(f"tomaaaaaaaaa, metaaaaa")
                return estat.accions_previes
            else:
                successors = estat.genera_fill()
                self.__tancats.append(estat)

                for successor in successors:
                    if successor.es_segur() and successor not in self.__tancats:
                        # print(f"\t> mete {successor} como sucesor")
                        self.__oberts.append(successor)

        return None
