# Proyecto Ferroviario

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


# Persistencia de datos.

Dentro del codigo existira una carpeta vacia a la cual el programa se encargara de dirigir los datos requeridos, y a su vez cuando el usuario quiera cargar los datos guardados hara que el programa se diriga a la carpeta donde estan los datos guardados y los va a mostrar en pantalla. con la funcion (ask save) as (askname) se usara una funcion que hace que el usuario elige la funcion y como guardarla, en que formato se guarda y si quiere abrir el archivo usa la funcion open.

# Archivos pricipales 

Si usas Visual Studio Code (VS Code)
Abre la carpeta completa del proyecto (por ejemplo, proyecto_simulacion/) desde Archivo → Abrir carpeta. 
En el Explorador de archivos de VS Code, selecciona el archivo principal — por ejemplo, main.py.
Asegúrate de tener seleccionado el intérprete de Python correcto (abajo a la derecha).

Ejecuta el archivo presionando:
“Run Python File” (botón arriba a la derecha), o
Usa el atajo Ctrl + F5 (sin depuración) o F5 (con depuración).
Esto correrá el bloque if __name__ == "__main__": automáticamente.

Si usas la terminal de Python directamente
Abre una terminal o consola (CMD, PowerShell o terminal de VS Code).
Posiciónate en la carpeta del proyecto, por ejemplo:
cd ruta/del/proyecto_simulacion

Ejecuta el archivo principal:
python main.py
Si quieres ejecutar otro módulo con __main__, entra a su carpeta y corre:
python ventana_gestion.py
