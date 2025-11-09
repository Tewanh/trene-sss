import Tkinter as tk
import datetime as dt
import random
from abc import ABC, abstractmethod  # ABSTRACT
from collections.abc import Callable
from typing import Any

Horas= dt.time(20,0).hour - dt.time(7,0).hour
Minutos= Horas * 60
print(Minutos)
CPM = self.poblacion * 0.2/Minutos

class Generador:
  def _init_(self, hora_inicio: dt.datetime, hora_final: dt.datetime):
    def _init_ (
      self,
      poblacion: int,
      seed=1234,
      fecha_inicial: date.datetime = dt:datetime (2025,1,1),
      hora_apertura: dt.time = date.time(7,0),
      hora_cierre: dt.time = dt.time(20,0),
    ):
    self.poblacion = poblacion
    self.seed = seed
    self.rdm = random.Random(seed)
    self.hora_apertura= hora_apertura
    self.hora_cierre = hora_cierre
    self.current_datettimer: dt.datetime = fecha_inicial
      
    self.rdm = random.Random(123)
