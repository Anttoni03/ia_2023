""" Fitxer que conté els diferents agents aspiradors.

Percepcions:
    Sensor.LLOC: [Localitzacio.HABITACIO_ESQ, Localitzacio.HABITACIO_DRET]
    Sensor.ESTAT: [EstatHabitacio.NET, EstatHabitacio.BRUT]

Accions:
    AccionsAspirador.DRETA
    AccionsAspirador.ESQUERRA
    AccionsAspirador.ATURA
    AccionsAspirador.ASPIRA

Autor: Miquel Miró Nicolau (UIB), 2022
"""
import abc

import pygame

from aspirador.entorn import (AccionsAspirador, Sensor, EstatHabitacio,
                              Localitzacio)
from ia_2022 import agent
from ia_2022 import entorn


class Aspirador(agent.Agent):
    def __init__(self):
        super().__init__(long_memoria=1)

    def pinta(self, display):
        img = pygame.image.load("../assets/aspirador/sprite.png")
        img = pygame.transform.scale(img, (100, 100))
        display.blit(img, self._posicio_pintar)

    @abc.abstractmethod
    def actua(self, percepcio: entorn.Percepcio) -> entorn.Accio:
        pass


class AspiradorTaula(Aspirador):
    TAULA = {
        (Localitzacio.HABITACIO_ESQ, EstatHabitacio.NET): AccionsAspirador.DRETA,
        (Localitzacio.HABITACIO_ESQ, EstatHabitacio.BRUT): AccionsAspirador.ASPIRA,
        (Localitzacio.HABITACIO_DRET, EstatHabitacio.NET): AccionsAspirador.ESQUERRA,
        (Localitzacio.HABITACIO_DRET, EstatHabitacio.BRUT): AccionsAspirador.ASPIRA,
    }

    def actua(self, percepcio: entorn.Percepcio) -> entorn.Accio:
        return AspiradorTaula.TAULA[
            (percepcio[Sensor.LLOC], percepcio[Sensor.ESTAT])
        ]


class AspiradorReflex(Aspirador):
    def actua(self, percepcio: entorn.Percepcio) -> entorn.Accio:
        """ IMPLEMENTAR -> hecho"""
        if percepcio[Sensor.ESTAT] == EstatHabitacio.BRUT:
            return AccionsAspirador.ASPIRA
        elif percepcio[Sensor.LLOC] == Localitzacio.HABITACIO_ESQ:
            return AccionsAspirador.DRETA
        else:
            return AccionsAspirador.ESQUERRA



class AspiradorMemoria(Aspirador):
    def actua(self, percepcio: entorn.Percepcio) -> entorn.Accio:
        """ IMPLEMENTAR -> hecho"""

        if self.get_memoria(1) == EstatHabitacio.NET and percepcio[Sensor.ESTAT] == EstatHabitacio.NET:
            return AccionsAspirador.ATURA

        if percepcio[Sensor.ESTAT] == EstatHabitacio.BRUT:
            return AccionsAspirador.ASPIRA
        self.set_memoria(EstatHabitacio.NET)

        if percepcio[Sensor.LLOC] == Localitzacio.HABITACIO_ESQ:
            return AccionsAspirador.DRETA
        else:
            return AccionsAspirador.ESQUERRA
