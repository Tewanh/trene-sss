# Models/Generador.py
import datetime as dt
import random
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

# =============================================================================
# CLASE BASE ABSTRACTA: GENERADOR
# =============================================================================
class Generador(ABC):
    def __init__(
        self,
        poblacion: int,
        distancia_media_estaciones_km: float = 100.0,
        velocidad_media_trenes_kmh: float = 100.0,
        seed: int = 123,
        fecha_inicial: dt.datetime = dt.datetime(2015, 1, 1, 7, 0),
        hora_apertura: dt.time = dt.time(7, 0),
        hora_cierre: dt.time = dt.time(20, 0),
    ):
        self.poblacion = poblacion
        self.seed = seed
        self.rdm = random.Random(seed)
        self.hora_apertura = hora_apertura
        self.hora_cierre = hora_cierre
        self.current_datetime: dt.datetime = fecha_inicial
        self.distancia_media_estaciones_km = distancia_media_estaciones_km
        self.velocidad_media_trenes_kmh = velocidad_media_trenes_kmh

    def minutos_de_funcionamiento(self) -> int:
        horas = self.hora_cierre.hour - self.hora_apertura.hour
        return horas * 60

    def tiempo_viaje_minutos(self) -> float:
        if self.velocidad_media_trenes_kmh <= 0:
            return 0.0
        tiempo_horas = self.distancia_media_estaciones_km / self.velocidad_media_trenes_kmh
        return tiempo_horas * 60

    @abstractmethod
    def generar_clientes(
        self,
        minutos: int,
        constructor: Callable[[int, dt.datetime], Any],
        update: bool = True,
    ) -> list[Any]:
        pass

# =============================================================================
# GENERADOR AVANZADO: PROPORCIÓN DE POBLACIÓN 
# =============================================================================
class GeneradorPorProporcion(Generador):
    def __init__(self, *args, tasa_base_clientes_por_hora: float = 0.001, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasa_base_clientes_por_hora = tasa_base_clientes_por_hora

    def generar_clientes(
        self,
        minutos: int,
        constructor: Callable[[int, dt.datetime], Any],
        update: bool = True,
    ) -> list[Any]:

        clientes_generados = []
        tasa_por_minuto = self.tasa_base_clientes_por_hora / 60
        clientes_estimados = int(self.poblacion * tasa_por_minuto * minutos)
        num_clientes = self.rdm.randint(max(0, clientes_estimados - 5), clientes_estimados + 5)

        for _ in range(num_clientes):
            minutos_creacion = self.rdm.randint(0, max(1, minutos) - 1)
            tiempo_creacion = self.current_datetime + dt.timedelta(minutes=minutos_creacion)
            cliente = f"Cliente @ {tiempo_creacion.strftime('%H:%M')}" # Simulación simple de cliente
            clientes_generados.append(cliente)

        if update:
            self.current_datetime += dt.timedelta(minutes=minutos)
        return clientes_generados

# =============================================================================
# GENERADOR UNIFORME
# =============================================================================
class GeneradorUniforme(Generador):
    def generar_clientes(
        self,
        minutos: int,
        constructor: Callable[[int, dt.datetime], Any],
        update: bool = True,
    ) -> list[Any]:
        if update:
            self.current_datetime += dt.timedelta(minutes=minutos)

        cpm = self.poblacion * 0.2 / self.minutos_de_funcionamiento()
        size = int(minutos * cpm)
        clientes = []
        for _ in range(size):
            cliente = f"Cliente @ {self.current_datetime.strftime('%H:%M')}"
            clientes.append(cliente)
        return clientes
