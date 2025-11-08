# ui/menu_cascada.py
import tkinter as tk
from tkinter import messagebox

def crear_menu_principal(root):
    """
    Crea y devuelve un menú cascada con la opción 'Acerca de'.
    Este menú se asocia a la ventana principal (root).
    """
    # Crear barra de menú
    barra_menu = tk.Menu(root)
    root.config(menu=barra_menu)

    # Crear menú 'Archivo'
    menu_archivo = tk.Menu(barra_menu, tearoff=0)
    menu_archivo.add_command(label="Salir", command=root.quit)
    barra_menu.add_cascade(label="Archivo", menu=menu_archivo)

    # Crear menú 'Ayuda'
    menu_ayuda = tk.Menu(barra_menu, tearoff=0)
    menu_ayuda.add_command(label="Acerca de", command=mostrar_acerca_de)
    barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)

def mostrar_acerca_de():
    """
    Muestra una ventana emergente con información del programa.
    """
    messagebox.showinfo(
        "Acerca de",
        "Proyecto Ferroviario v1.0\n\nDesarrollado por el equipo.\n© 2025"
    )
