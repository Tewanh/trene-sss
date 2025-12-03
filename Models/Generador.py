# Models/Generador.py — versión correcta SIN IMPORTACIONES CÍCLICAS
import datetime as dt
import random


# -------------------------------------------------------------
# GENERADOR BASE
# -------------------------------------------------------------
class Generador:
    def __init__(self,
                 poblacion,
                 distancia_media_estaciones_km=100.0,
                 velocidad_media_trenes_kmh=100.0,
                 seed=123,
                 fecha_inicial=dt.datetime(2015, 1, 1, 7, 0),
                 hora_apertura=dt.time(7, 0),
                 hora_cierre=dt.time(20, 0)):

        self.poblacion = poblacion
        self.distancia_media = distancia_media_estaciones_km
        self.velocidad_media = velocidad_media_trenes_kmh
        self.rdm = random.Random(seed)

        # Tiempo interno del generador
        self.current_datetime = fecha_inicial

        self.hora_apertura = hora_apertura
        self.hora_cierre = hora_cierre

    # Método base — se sobrescribe en subclases
    def generar_clientes(self, minutos, constructor, update=True):
        return []


# -------------------------------------------------------------
# GENERADOR PEAK — SIN IMPORTAR EL MISMO ARCHIVO
# -------------------------------------------------------------
class GeneradorPeak(Generador):

    def __init__(self,
                 poblacion,
                 distancia_media_estaciones_km=100.0,
                 velocidad_media_trenes_kmh=100.0,
                 seed=123,
                 fecha_inicial=dt.datetime(2015, 1, 1, 7, 0),
                 hora_apertura=dt.time(7, 0),
                 hora_cierre=dt.time(20, 0),
                 tasa_base_por_minuto=0.005,
                 horas_peak=[(8, 10), (17, 19)],
                 factor_peak=3.0):

        super().__init__(poblacion,
                         distancia_media_estaciones_km,
                         velocidad_media_trenes_kmh,
                         seed,
                         fecha_inicial,
                         hora_apertura,
                         hora_cierre)

        self.tasa_base_por_minuto = tasa_base_por_minuto
        self.horas_peak = horas_peak
        self.factor_peak = factor_peak

    def peakahora(self, hora_actual):
        for inicio, fin in self.horas_peak:
            if inicio <= hora_actual < fin:
                return True
        return False

    def generar_clientes(self, minutos, constructor, update=True):
        lista = []
        tiempo = self.current_datetime

        for _ in range(minutos):

            hora_actual = tiempo.hour

            tasa = (
                self.tasa_base_por_minuto * self.factor_peak
                if self.peakahora(hora_actual)
                else self.tasa_base_por_minuto
            )

            if self.rdm.random() < tasa:
                cliente = constructor(None, tiempo)
                lista.append(cliente)

            tiempo += dt.timedelta(minutes=1)

        if update:
            self.current_datetime = tiempo

        return lista

