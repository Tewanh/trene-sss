# Logic/Guardado.py
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, Menu
from datetime import datetime


def guardar_datos(datos, ventana_principal):
    archivo_destino = filedialog.asksaveasfilename(
        parent=ventana_principal,
        defaultextension=".json",
        filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
    )
   
    if not archivo_destino:
        return
   
    try:
        with open(archivo_destino, 'w') as archivo:
            if 'tiempo_actual_simulado' in datos and isinstance(datos['tiempo_actual_simulado'], datetime):
                datos['tiempo_actual_simulado'] = datos['tiempo_actual_simulado'].strftime("%Y-%m-%d %H:%M:%S")
           
            json.dump(datos, archivo, indent=4)
        messagebox.showinfo("Guardado", f"Datos guardados exitosamente en {archivo_destino.split('/')[-1]}.")
    except IOError as e:
        messagebox.showerror("Error de guardado (IO)", f"No se pudo escribir en el archivo: {e}")
    except Exception as e:
        messagebox.showerror("Error de guardado", f"Ocurrió un error inesperado al guardar los datos: {e}")



def cargar_datos(ventana_principal):
    archivo_origen = filedialog.askopenfilename(
        parent=ventana_principal,
        filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
    )
   
    if not archivo_origen:
        return None
   
    try:
        with open(archivo_origen, 'r') as archivo:
            datos = json.load(archivo)
        messagebox.showinfo("Cargado", f"Datos cargados exitosamente de {archivo_origen.split('/')[-1]}.")
        return datos
    except FileNotFoundError:
        messagebox.showerror("Error de carga", "El archivo no existe.")
        return None
    except json.JSONDecodeError:
        messagebox.showerror("Error de carga", "El archivo no tiene un formato JSON válido o está corrupto.")
        return None
    except Exception as e:
        messagebox.showerror("Error de carga", f"No se pudieron cargar los datos: {e}")
        return None



def guardar_datos_completo(estado_simulacion, nombre_archivo=None):
    """Guarda el estado completo de la simulación en un archivo JSON."""
    
    if not nombre_archivo:
        nombre_archivo = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json")],
            title="Guardar Estado de Simulación"
        )
        if not nombre_archivo:
            return

    
    datos = {
        "tiempo_actual_simulado": estado_simulacion.tiempo_actual_simulado.strftime(estado_simulacion.formato_fecha),

        
        "estaciones": [e.to_dict() for e in estado_simulacion.estaciones.values()] if hasattr(estado_simulacion, "estaciones") else [],
        "trenes": [t.to_dict() for t in estado_simulacion.trenes.values()] if hasattr(estado_simulacion, "trenes") else [],

        
        "registro_eventos": getattr(estado_simulacion, "registro_eventos", []),
        "contador_id_cliente": getattr(estado_simulacion, "contador_id_cliente", 0)
    }

    try:
        with open(nombre_archivo, 'w') as f:
            json.dump(datos, f, indent=4)
        messagebox.showinfo("Guardado Exitoso", f"Estado guardado en: {os.path.basename(nombre_archivo)}")
    except Exception as e:
        messagebox.showerror("Error de Guardado", f"No se pudo guardar el archivo: {e}")


def cargar_datos_completo(ventana):
    """Carga el estado completo de la simulación desde JSON."""
    nombre_archivo = filedialog.askopenfilename(
        defaultextension=".json",
        filetypes=[("Archivos JSON", "*.json")],
        title="Cargar Estado de Simulación"
    )

    if not nombre_archivo:
        return None

    try:
        with open(nombre_archivo, 'r') as f:
            data = json.load(f)

        datos_cargados = {
            "tiempo_actual_simulado": data.get("tiempo_actual_simulado"),
            "estaciones": data.get("estaciones", []),
            "trenes": data.get("trenes", []),
            "registro_eventos": data.get("registro_eventos", []),
            "contador_id_cliente": data.get("contador_id_cliente", 0)
        }

        messagebox.showinfo("Carga Exitosa", f"Estado cargado desde: {os.path.basename(nombre_archivo)}")
        return datos_cargados

    except Exception as e:
        messagebox.showerror("Error de Carga", f"No se pudo cargar el archivo o está corrupto: {e}")
        return None



#  FUNCIÓN DEL MENÚ 
def crear_menu_archivo(root, menubar, datos_funcion):
    archivo_menu = Menu(menubar, tearoff=0)

    archivo_menu.add_command(
        label="Guardar (simple)",
        command=lambda: guardar_datos(datos_funcion(), root)
    )

    archivo_menu.add_command(
        label="Guardar Completo (RF08)",
        command=lambda: guardar_datos_completo(datos_funcion(), None)
    )

    archivo_menu.add_command(
        label="Cargar Completo (RF08)",
        command=lambda: cargar_datos_completo(root)
    )

    menubar.add_cascade(label="Archivo", menu=archivo_menu)
    return archivo_menu
