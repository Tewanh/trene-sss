# Proyecto Ferrodiario

Resumen y contexto del proyecto 

Este proyecto corresponde al desarrollo del Sistema de Simulación de Tráfico Ferroviario, cuyo propósito es representar de forma controlada el funcionamiento del sistema ferroviario nacional.  
Este proyecto responde a una necesidad planteada por la Empresa de Ferrocarriles del Estado (EFE) de Chile, la cual busca una herramienta que permita modelar, analizar y optimizar el flujo de pasajeros entre distintas estaciones a lo largo de un día de operación.
El sistema simula el tránsito de trenes, estaciones y rutas, considerando la demanda diaria de transporte y la dinámica temporal del servicio.  
Su objetivo principal es permitir al operario tomar decisiones que mejoren la eficiencia del transporte, mediante una interfaz gráfica desarrollada con Tkinter y un sistema de turnos basado en eventos.
Durante la simulación, los trenes se desplazan entre estaciones con capacidad y velocidad configurables, mientras los usuarios son generados de forma aleatoria según la población de cada estación.  
El sistema gestiona eventos como llegadas, esperas o giros de trenes, manteniendo un Estado de Simulación persistente que puede ser guardado, cargado o restaurado en diferentes momentos del día.

# Integrantes

Ricardo Torres, Heidi Santisteban, Nestor Sepulveda, Dalma Redoles.
 
# Indicadores del sistema.

1. Flujo de Pasajeros Transportados:
  Mide la cantidad total de personas que completan su viaje durante el día. Permite al operario evaluar la eficiencia del sistema y detectar cuellos de botella.

2. Tasa de Ocupación Promedio:
   Representa el porcentaje promedio de ocupación de los trenes. Un valor alto indica buen uso de recursos; un valor bajo sugiere exceso de trenes o baja demanda.


# persistencia de datos.

dentro del codigo existira una carpeta vacia a la cual el programa se encargara de dirigir los datos requeridos, y a su vez cuando el usuario quiera cargar los datos guardados hara que el programa se diriga a la carpeta donde estan los datos guardados y los va a mostrar en pantalla.
