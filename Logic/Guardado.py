import json
from tkinter import filedialog, messagebox, Menu

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
    Añade una cascada 'Archivo' al menubar de tkinter.
    - root: la ventana principal de tkinter
    - menubar: el Menu principal de tkinter (Menu(root))
    - datos_funcion: función/callback que devuelve los datos actuales a guardar
    """
    archivo_menu = Menu(menubar, tearoff=0)
    
    archivo_menu.add_command(
        label="Guardar", 
        command=lambda: guardar_datos(datos_funcion(), root)
    )
    archivo_menu.add_command(
        label="Cargar", 
        command=lambda: cargar_datos(root)
    )
    menubar.add_cascade(label="Archivo", menu=archivo_menu)
