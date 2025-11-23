# logic/guardado.py
import json
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
        messagebox.showinfo("Guardado", f"Datos guardados exitosamente.")
    except Exception as e:
        messagebox.showerror("Error de guardado", f"No se pudieron guardar los datos: {e}")

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
        messagebox.showinfo("Cargado", f"Datos cargados exitosamente.")
        return datos
    except Exception as e:
        messagebox.showerror("Error de carga", f"No se pudieron cargar los datos: {e}")
        return None

def crear_menu_archivo(root, menubar, datos_funcion):
    """
    Añade una cascada 'Archivo' al menubar de tkinter Y DEVUELVE el objeto Menu.
    """
    archivo_menu = Menu(menubar, tearoff=0)
    
    archivo_menu.add_command(
        label="Guardar", 
        command=lambda: guardar_datos(datos_funcion(), root)
    )
    # Ya no añadimos 'Cargar' aquí, se añade en main.py
    menubar.add_cascade(label="Archivo", menu=archivo_menu)

    # ESTA LÍNEA ES CLAVE PARA LA CORRECCIÓN DEL ERROR
    return archivo_menu
