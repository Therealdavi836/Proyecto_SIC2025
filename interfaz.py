import tkinter as tk
from tkinter import ttk, messagebox, filedialog

def ejecutar_algoritmo():
    try:
        parametros = {
            "cruce": float(entrada_cruce.get()),
            "mutacion": float(entrada_mutacion.get()),
            "poblacion": int(entrada_tam_poblacion.get()),
            "generaciones": int(entrada_generaciones.get()),
            "elitismo": int(entrada_elitismo.get()),
            "seleccion": metodo_seleccion.get(),
            "cruce_tipo": metodo_cruce.get(),
            "mutacion_tipo": metodo_mutacion.get(),
            "objetivo": entrada_funcion_objetivo.get("1.0", "end").strip(),
            "restriccion": entrada_funcion_restriccion.get("1.0", "end").strip(),
            "modo_poblacion": opcion.get()
        }

        resultados_text.insert("end", "🧬 Ejecutando algoritmo genético...\n")
        resultados_text.insert("end", f"Parámetros: {parametros}\n")
        resultados_text.insert("end", "✅ Listo para integrar con backend.\n\n")

    except ValueError:
        messagebox.showerror("Error", "Por favor, completa todos los campos numéricos correctamente.")

def limpiar_campos():
    for entrada in [entrada_cruce, entrada_mutacion, entrada_tam_poblacion, entrada_generaciones, entrada_elitismo]:
        entrada.delete(0, 'end')
    entrada_funcion_objetivo.delete("1.0", "end")
    entrada_funcion_restriccion.delete("1.0", "end")
    resultados_text.delete("1.0", "end")

def guardar_csv():
    ruta = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if ruta:
        with open(ruta, "w") as f:
            f.write(resultados_text.get("1.0", "end"))
        messagebox.showinfo("Guardado", f"Resultados guardados en:\n{ruta}")

def mostrar_frame():
    if opcion.get() == "s":
        frame_si.pack(fill="both", expand=True)
        frame_no.pack_forget()
    else:
        frame_no.pack(fill="both", expand=True)
        frame_si.pack_forget()

def mostrar_calculadora(label_tipo):
    global seccion_calculadora, funcion_activa

    if seccion_calculadora:
        seccion_calculadora.destroy()

    funcion_activa = label_tipo
    seccion_calculadora = tk.Frame(frame_funciones, bg="#eef")
    seccion_calculadora.grid(row=2 if label_tipo == "objetivo" else 3, column=1, columnspan=2, pady=5, sticky="w")

    tk.Label(seccion_calculadora, text="Editor de Función", bg="#eef").pack(pady=(5, 0))

    entry_funcion = tk.Entry(seccion_calculadora, width=60)
    entry_funcion.pack(pady=5)

    if funcion_activa == "objetivo":
        entry_funcion.insert(0, funcion_objetivo_str.get())
    elif funcion_activa == "restriccion":
        entry_funcion.insert(0, funcion_restriccion_str.get())

    def insertar(texto):
        entry_funcion.insert(tk.END, texto)

    botones = [
        ("+", "+"), ("-", "-"), ("×", "*"), ("÷", "/"),
        ("x²", "^2"), ("x^y", "^"), ("√", "sqrt("),("ⁿ√", "root("), 
        ("log", "log("), ("π", "pi"), ("e", "e"), ("(", "("), 
        (")", ")"), ("sin", "sin("), ("cos", "cos("), ("tan", "tan("),
        ("cot", "cot("), ("csc", "csc("), ("sec", "sec(")
    ]

    botones_frame = tk.Frame(seccion_calculadora, bg="#eef")
    botones_frame.pack()

    for i, (texto, valor) in enumerate(botones):
        tk.Button(botones_frame, text=texto, width=5, command=lambda v=valor: insertar(v)).grid(row=i//6, column=i%6, padx=2, pady=2)

    acciones_frame = tk.Frame(seccion_calculadora, bg="#eef")
    acciones_frame.pack(pady=5)

    def guardar_funcion():
        texto = entry_funcion.get().strip()
        if funcion_activa == "objetivo":
            funcion_objetivo_str.set(texto)
        elif funcion_activa == "restriccion":
            funcion_restriccion_str.set(texto)
        seccion_calculadora.destroy()

    def cancelar():
        seccion_calculadora.destroy()

    tk.Button(acciones_frame, text="Guardar", command=guardar_funcion, bg="#4CAF50", fg="white").pack(side="left", padx=5)
    tk.Button(acciones_frame, text="Cancelar", command=cancelar, bg="#f44336", fg="white").pack(side="left", padx=5)


# Variables globales necesarias
seccion_calculadora = None
funcion_activa = None


root = tk.Tk()
root.title("Algoritmo Genético - Interfaz Gráfica")
root.geometry("1200x700")

# ==== Layout principal en dos columnas ====
frame_izquierda = tk.Frame(root)
frame_izquierda.pack(side="left", fill="both", expand=True, padx=10, pady=10)

frame_derecha = tk.Frame(root)
frame_derecha.pack(side="right", fill="y", padx=10, pady=10)

# ===== PARÁMETROS NUMÉRICOS =====
frame_parametros = tk.LabelFrame(frame_izquierda, text="⚙️ Parámetros Numéricos", padx=10, pady=10)
frame_parametros.pack(fill="x", pady=5)

labels = ["Porcentaje de Cruce (%)", "Porcentaje de Mutación (%)", "Tamaño de Población", "Número de Generaciones", "Elitismo"]
entradas = []

for i, texto in enumerate(labels):
    tk.Label(frame_parametros, text=texto).grid(row=i, column=0, sticky="w", padx=5, pady=5)
    entrada = tk.Entry(frame_parametros)
    entrada.grid(row=i, column=1, padx=5, pady=5)
    entradas.append(entrada)

entrada_cruce, entrada_mutacion, entrada_tam_poblacion, entrada_generaciones, entrada_elitismo = entradas

# ===== MÉTODOS GENÉTICOS =====
frame_metodos = tk.LabelFrame(frame_izquierda, text="🧬 Operadores Genéticos", padx=10, pady=10)
frame_metodos.pack(fill="x", pady=5)

tk.Label(frame_metodos, text="Método de Selección:").grid(row=0, column=0, sticky="w")
metodo_seleccion = ttk.Combobox(frame_metodos, values=["Ruleta", "Torneo", "Ranking"], state="readonly")
metodo_seleccion.grid(row=0, column=1, pady=5)
metodo_seleccion.current(0)

tk.Label(frame_metodos, text="Método de Cruce:").grid(row=1, column=0, sticky="w")
metodo_cruce = ttk.Combobox(frame_metodos, values=["Un punto", "Dos puntos", "Uniforme"], state="readonly")
metodo_cruce.grid(row=1, column=1, pady=5)
metodo_cruce.current(0)

tk.Label(frame_metodos, text="Método de Mutación:").grid(row=2, column=0, sticky="w")
metodo_mutacion = ttk.Combobox(frame_metodos, values=["Bit flip", "Intercambio", "Inversión"], state="readonly")
metodo_mutacion.grid(row=2, column=1, pady=5)
metodo_mutacion.current(0)

# ===== FUNCIONES =====
frame_funciones = tk.LabelFrame(frame_izquierda, text="🧮 Funciones del Problema", padx=10, pady=10)
frame_funciones.pack(fill="x", pady=5)

funcion_objetivo_str = tk.StringVar(value="")
funcion_restriccion_str = tk.StringVar(value="")

tk.Label(frame_funciones, text="Función Objetivo:").grid(row=0, column=0, sticky="nw")
entrada_funcion_objetivo = tk.Label(frame_funciones, textvariable=funcion_objetivo_str, anchor="w", bg="white", relief="solid", width=60, height=1, justify="left")
entrada_funcion_objetivo.grid(row=0, column=1, pady=5, sticky="w")
tk.Button(frame_funciones, text="✏️ Editar", command=lambda: mostrar_calculadora("objetivo")).grid(row=0, column=2, padx=5)

tk.Label(frame_funciones, text="Función de Restricción:").grid(row=1, column=0, sticky="nw")

entrada_funcion_restriccion = tk.Label(frame_funciones, textvariable=funcion_restriccion_str, anchor="w", bg="white", relief="solid", width=60, height=1, justify="left")
entrada_funcion_restriccion.grid(row=1, column=1, pady=5, sticky="w")
tk.Button(frame_funciones, text="✏️ Editar", command=lambda: mostrar_calculadora("restriccion")).grid(row=1, column=2, padx=5)

# ===== POBLACIÓN INICIAL =====
opcion = tk.StringVar(value="s")
frame_poblacion = tk.LabelFrame(frame_izquierda, text="🧪 Población Inicial", padx=10, pady=10)
frame_poblacion.pack(fill="x", pady=5)

ttk.Radiobutton(frame_poblacion, text="Aleatoria", variable=opcion, value="s", command=mostrar_frame).pack(side="left", padx=5)
ttk.Radiobutton(frame_poblacion, text="Predefinida", variable=opcion, value="n", command=mostrar_frame).pack(side="left", padx=5)

frame_si = tk.LabelFrame(frame_poblacion, text="Generar aleatoriamente", padx=10, pady=5)
frame_no = tk.LabelFrame(frame_poblacion, text="Ingresar manualmente", padx=10, pady=5)

mostrar_frame()

# ===== BOTONES =====
frame_botones = tk.Frame(frame_izquierda)
frame_botones.pack(pady=10)

tk.Button(frame_botones, text="▶ Ejecutar", bg="#4CAF50", fg="white", command=ejecutar_algoritmo).grid(row=0, column=0, padx=10)
tk.Button(frame_botones, text="🧹 Limpiar", bg="#f0ad4e", fg="white", command=limpiar_campos).grid(row=0, column=1, padx=10)
tk.Button(frame_botones, text="💾 Guardar CSV", bg="#0275d8", fg="white", command=guardar_csv).grid(row=0, column=2, padx=10)

# ===== RESULTADOS (a la derecha) =====
frame_resultados = tk.LabelFrame(frame_derecha, text="📊 Resultados", padx=10, pady=10)
frame_resultados.pack(fill="both", expand=True)

resultados_text = tk.Text(frame_resultados, wrap="word")
resultados_text.pack(expand=True, fill="both")

root.mainloop()