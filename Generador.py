import Tkinter as tk
import datetime as dt
import random

Horas= dt.time(20,0).hour - dt.time(7,0).hour
Minutos= Horas * 60
print(Minutos)
CPM = Poblacion * 0.2/Minutos

class Cliente:
  def _init_(self, hora_creacion: dt.datetime):
    self.hora_creacion = hora_creacion
    self.destino = ...
    self.origen = ...
    self.delay = ...
    self.id = ...
    self.nombre = ...
    self.edad = ...

class Generador:
  def _init_(self, hora_inicio: dt.datetime, hora_final: dt.datetime):
    . . .
    . . .
    self.rdm = random.Random(123)
    
  def generar_clientes(self, minutos: int):
    size = int(minutos * CPM)
    return [Cliente(dt.datetime.now())] * size

class Estacion:
  def _init_(self, nombre: str, hora:inicio: dt.datetime,hora_final: dt.datetime):
    self.nombre = nombre
    self.generador = Generador(hora_inicio, hora_final)

def generar_clientes(minutos: int):
  size = int(minutos * CPM)
  return [Cliente(dt.datetime.now())] * size

if _name_ == "_main_":
  estecion1 = Estacion("Ferroviario Valdivia", dt.datetime(7,0), dt.time(20,0))
  generador = estacion1.generador
  res = generar_clientes(10)
  print("Clientes:", len(res))

res = generador.generar_clientes(Minutos)
print("Min:", Poblacion * 0.19)
print("Clientes", len(res))
print("Max:", Poblacion * 0.21)
assert Poblacion * 0.19 <= len(res) <= Poblacion * 0.21

