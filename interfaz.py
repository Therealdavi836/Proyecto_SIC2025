from tkinter import *
import tkinter as tk
from tkinter import ttk

# Interfaz gráfica para configurar y ejecutar un algoritmo genético todavia no implementado.

def ejecutar_algoritmo():
    # Aquí se implementaría la lógica del algoritmo genético
    print("Ejecutando algoritmo genético con los siguientes parámetros:")
    print("Porcentaje de Cruce:", entrada_cruce.get())
    print("Porcentaje de Mutación:", entrada_mutacion.get())
    print("Tamaño de Población:", entrada_tam_poblacion.get())
    print("Número de Generaciones:", entrada_generaciones.get())
    print("Restricción:", entrada_restriccion.get())
    print("Función Objetivo:", entrada_funcion_objetivo.get())
    print("Función de Restricción:", entrada_funcion_restriccion.get())

def mostrar_frame():
    eleccion = opcion.get()
    if eleccion == "s":
        frame_si.pack(fill="both", expand=True)
        frame_no.pack_forget()
    elif eleccion == "n":
        frame_no.pack(fill="both", expand=True)
        frame_si.pack_forget()

root = Tk()
root.title("Algoritmos Genéticos")

frame_parametros = tk.LabelFrame(root, text="Parametros Numéricos", padx=10, pady=10)
frame_parametros.pack(padx=10, pady=10)

tk.Label(frame_parametros, text="Porcentaje de Cruce (%):").grid(row=0, column=0, sticky='w')
entrada_cruce = tk.Entry(frame_parametros)
entrada_cruce.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_parametros, text="Porcentaje de Mutación (%):").grid(row=1, column=0, sticky='w')
entrada_mutacion = tk.Entry(frame_parametros)
entrada_mutacion.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_parametros, text="Tamaño de Población:").grid(row=2, column=0, sticky='w')
entrada_tam_poblacion = tk.Entry(frame_parametros)
entrada_tam_poblacion.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_parametros, text="Número de Generaciones:").grid(row=3, column=0, sticky='w')
entrada_generaciones = tk.Entry(frame_parametros)
entrada_generaciones.grid(row=3, column=1, padx=5, pady=5)

tk.Label(frame_parametros, text="Restricción:").grid(row=4, column=0, sticky='w')
entrada_restriccion = tk.Entry(frame_parametros)
entrada_restriccion.grid(row=4, column=1, padx=5, pady=5)


frame_funciones = tk.LabelFrame(root, text="Funciones", padx=10, pady=10)
frame_funciones.pack(padx=10, pady=10)

tk.Label(frame_funciones, text="Función Objetivo:").grid(row=0, column=0, sticky='w')
entrada_funcion_objetivo = tk.Entry(frame_funciones)
entrada_funcion_objetivo.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_funciones, text="Función de Restricción:").grid(row=1, column=0, sticky='w')
entrada_funcion_restriccion = tk.Entry(frame_funciones)
entrada_funcion_restriccion.grid(row=1, column=1, padx=5, pady=5)

opcion = tk.StringVar(value="s")

frame_poblacion = tk.LabelFrame(root, text="Población Inicial", padx=10, pady=10)
frame_poblacion.pack(padx=10, pady=10, fill="x")

ttk.Radiobutton(frame_poblacion, text="Si", variable=opcion, value="s", command=mostrar_frame).pack(side="left", padx=5, pady=5)
ttk.Radiobutton(frame_poblacion, text="No", variable=opcion, value="n", command=mostrar_frame).pack(side="left", padx=5, pady=5)

frame_si = tk.LabelFrame(frame_poblacion, text="Población Aleatoria", padx=10, pady=10)
frame_si.pack(side="left", padx=5, pady=5, fill="x")

frame_no = tk.LabelFrame(frame_poblacion, text="Población Predefinida", padx=10, pady=10)
frame_no.pack(side="left", padx=5, pady=5, fill="x")
root.mainloop()