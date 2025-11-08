import json
from tkinter import filedialog, messagebox

def guardar_datos(datos, ventana_principal):
    """
    Guarda los datos en un archivo JSON seleccionado por el usuario.
    """
    archivo_destino = filedialog.asksaveasfilename(
        parent=ventana_principal,
        defaultextension=".json",
        filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
    )
    
    if not archivo_destino:
        return
    
    try:
        with open(archivo_destino, 'w') as archivo:
            json.dump(datos, archivo, indent=4)
        messagebox.showinfo("Guardado", f"Datos guardados exitosamente.")
    except Exception as e:
        messagebox.showerror("Error de guardado", f"No se pudieron guardar los datos: {e}")

def cargar_datos(ventana_principal):
    """
    Carga datos desde un archivo JSON seleccionado por el usuario.
    Retorna los datos cargados o None si hubo un error/cancelación.
    """
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
