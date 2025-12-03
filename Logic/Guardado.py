# Logic/Guardado.py
import json
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

def crear_menu_archivo(root, menubar, datos_funcion):
    archivo_menu = Menu(menubar, tearoff=0)
    archivo_menu.add_command(
        label="Guardar", 
        command=lambda: guardar_datos(datos_funcion(), root)
    )
    menubar.add_cascade(label="Archivo", menu=archivo_menu)
    return archivo_menu

