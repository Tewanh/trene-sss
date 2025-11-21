# ui/eventos_ui.py
import tkinter as tk
from tkinter import Button, Toplevel, messagebox
# Importamos las funciones de guardado que están en la carpeta logic
from Logic.Guardado import guardar_datos, cargar_datos


def crear_ventana_eventos(ventana_padre, obtener_estado_callback, aplicar_estado_callback):
    ventana_eventos = Toplevel(ventana_padre)
    ventana_eventos.title("Gestión de Simulación y Eventos")
    ventana_eventos.geometry("300x200")

    tk.Label(ventana_eventos, text="Opciones de Simulación:").pack(pady=10)

    # Botón Guardar
    Button(
        ventana_eventos, 
        text="Guardar Simulación", 
        command=lambda: guardar_datos(obtener_estado_callback(), ventana_eventos)
    ).pack(pady=5)
    
    # Botón Cargar
    Button(
        ventana_eventos, 
        text="Cargar Simulación", 
        # Usamos un lambda para pasar la ventana y el callback necesarios
        command=lambda: manejar_carga_estado(ventana_eventos, aplicar_estado_callback)
    ).pack(pady=5)

    # Botón Reiniciar Simulación
    Button(
        ventana_eventos,
        text="Reiniciar Simulación",
        command=lambda: manejar_reinicio_estado(ventana_eventos, aplicar_estado_callback)
    ).pack(pady=10, fill=tk.X, padx=20)


def manejar_carga_estado(ventana_eventos, aplicar_estado_callback):
    """Maneja la lógica de carga y llama al callback principal para aplicar los datos."""
    datos_cargados = cargar_datos(ventana_eventos)
    if datos_cargados:
        aplicar_estado_callback(datos_cargados)
        # Opcional: Cerrar la ventana de eventos tras una carga exitosa
        # ventana_eventos.destroy()


def manejar_reinicio_estado(ventana_eventos, aplicar_estado_callback):
    """
    Pregunta al usuario y, si confirma, reinicia la simulación al estado original.
    """
    if messagebox.askokcancel("Reiniciar", "¿Estás seguro de querer reiniciar la simulación a la fecha y hora original?"):
        # La fecha y hora original es 2015-01-01 07:00:00 (definida en Estado_de_simulacion.py)
        datos_reinicio = {
            "tiempo_actual_simulado": "2015-01-01 07:00:00"
        }
        aplicar_estado_callback(datos_reinicio)
        messagebox.showinfo("Reinicio Exitoso", "La simulación ha vuelto a su estado original.")
        ventana_eventos.destroy()
