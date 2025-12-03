import random

class Cliente:
    def __init__(self, id, estacion_origen, destino=None):
        self.id = id
        self.estacion_origen = estacion_origen
        self.destino = destino

    def __repr__(self):
        return f"Cliente({self.id}, origen={self.estacion_origen.nombre})"


# ================================================================
#  GENERACIÓN DE CLIENTES POR ESTACIÓN (20% ± 1%)
# ================================================================
def generar_clientes_estacion(estacion):
    """
    Genera clientes esperando en la estación según:
    - entre el 19% y 21% de la población total de esa estación.
    """

    poblacion = estacion.poblacion_total

    # Cálculo del rango permitido 20% + o - 1%
    min_clientes = int(poblacion * 0.19)
    max_clientes = int(poblacion * 0.21)

    # Cantidad final de clientes generados
    cantidad = random.randint(min_clientes, max_clientes)

    # Si la estación no tiene lista para clientes esperando, la creamos
    if not hasattr(estacion, "clientes_esperando"):
        estacion.clientes_esperando = []

    # Limpiamos cualquier dato previo
    estacion.clientes_esperando.clear()

    # Crear los clientes
    for i in range(cantidad):
        cliente = Cliente(
            id=f"{estacion.nombre}_C{i}",
            estacion_origen=estacion,
            destino=None  # Puedes asignar destino después según tu lógica
        )
        estacion.clientes_esperando.append(cliente)

