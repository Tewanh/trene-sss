import Tkinter as tk
import datetime as dt
import random
from abc import ABC, abstractmethod  # ABSTRACT
from collections.abc import Callable
from typing import Any

class Estacion:
  def __init__(self, nombre: str, hora:inicio: dt.datetime,hora_final: dt.datetime):
    self.nombre = nombre
    self.generador = Generador(hora_inicio, hora_final)
    self.poblacion = self.poblacion * 0.2
