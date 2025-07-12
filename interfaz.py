import tkinter as tk
import random
import threading
import time
import json
from tkinter import ttk, messagebox, filedialog
from funciones import *
from metodos import *


# Variables globales necesarias
# Ague esta variable global para los checkpints
indice_generacion_actual = 0  # Controla qué generación se está mostrando

seccion_calculadora = None
funcion_activa = None


def mostrar_generacion(indice):
    global json_generaciones, resultados_text

    if 0 <= indice < len(json_generaciones):
        resultados_text.delete("1.0", "end")
        gen = json_generaciones[indice]

        resultados_text.insert("end", f"Generación {gen['generacion']}\n")
        resultados_text.insert("end", "N° | Cromosoma binario                 | Fenotipo       | Obj. | Factible\n")
        resultados_text.insert("end", "-"*70 + "\n")

        for i, ind in enumerate(gen["individuos"]):
            crom = ind["cromosoma"]
            feno = ind["fenotipo"]
            obj = ind["objetivo"]
            fact = "✔" if ind["factible"] else "❌"
            resultados_text.insert("end", f"{i+1:2d} | {crom:28} | {feno} | {obj:5} | {fact}\n")

        # Mostrar también el mejor
        mejor = gen["mejor"]
        resultados_text.insert("end", "\n🌟 Mejor individuo de esta generación:\n")
        resultados_text.insert("end", f"Cromosoma: {mejor['cromosoma']}\n")
        resultados_text.insert("end", f"Fenotipo: {mejor['fenotipo']}\n")
        resultados_text.insert("end", f"Objetivo: {mejor['objetivo']}\n")
        resultados_text.insert("end", f"Factible: {'✔' if mejor['factible'] else '❌'}\n")
def cambiar_generacion(delta):
    global indice_generacion_actual
    nuevo_indice = indice_generacion_actual + delta
    if 0 <= nuevo_indice < len(json_generaciones):
        indice_generacion_actual = nuevo_indice
        mostrar_generacion(indice_generacion_actual)
def ir_a_generacion():
    global indice_generacion_actual
    try:
        numero = int(entrada_generacion_ir.get()) - 1
        if 0 <= numero < len(json_generaciones):
            indice_generacion_actual = numero
            mostrar_generacion(indice_generacion_actual)
        else:
            messagebox.showwarning("Fuera de rango", f"Debe ser entre 1 y {len(json_generaciones)}")
    except ValueError:
        messagebox.showerror("Error", "Debe ingresar un número entero.")


def ejecutar_algoritmo_en_hilo():
    hilo = threading.Thread(target=ejecutar_algoritmo)
    hilo.start()

def imprimir_y_guardar(texto):
    resultados_text.insert("end", texto)
    resultados_text.see("end")
    global historial_resultados
    historial_resultados += texto
#ejecutar_algoritmo
# Funciones de control de interfaz
def ejecutar_algoritmo():
    global json_generaciones
    global historial_resultados
    global historial_resultados_csv_completo

    json_generaciones = []
    historial_resultados = "Ejecutando algoritmo genético...\n"
    historial_resultados_csv_completo = []

    try:
        # 1. Obtener parámetros desde la GUI
        parametros = {
            "cruce": float(entrada_cruce.get()) / 100,
            "mutacion": float(entrada_mutacion.get()) / 100,
            "poblacion": int(entrada_tam_poblacion.get()),
            "generaciones": int(entrada_generaciones.get()),
            "elitismo": int(entrada_elitismo.get()),
            "seleccion": metodo_seleccion.get(),
            "cruce_tipo": metodo_cruce.get(),
            "mutacion_tipo": metodo_mutacion.get(),
            "objetivo": funcion_objetivo_str.get().strip(),
            "restriccion": funcion_restriccion_str.get().strip(),
            "modo_poblacion": opcion.get()
        }
        '''agrege esto mis lideres'''
        print(f"DEBUG - Restricción cruda: {parametros['restriccion']}")

        # 2. Parsear funciones
        coef_funcion = funcionesAVectores(parametros["objetivo"])
        coef_restriccion, limite_restriccion = parsear_restriccion(parametros["restriccion"])
        tam_fenotipo = len(coef_funcion)
        bits_por_variable = 4
        fenotipo = [bits_por_variable] * tam_fenotipo

        # 3. Preparar la interfaz
        resultados_text.delete("1.0", "end")
        imprimir_y_guardar("🧬 Ejecutando algoritmo genético...\n")
        root.update_idletasks()

        # 4. Inicializar población
        poblacion = generarPoblacionInicial(coef_funcion, limite_restriccion, parametros["poblacion"], fenotipo)

        # 5. Evolución
        for generacion in range(parametros["generaciones"]):
            nueva_poblacion = []

            fitness = [
                resultadoFuncion(ind, fenotipo, coef_funcion)
                if esFactible(ind, fenotipo, coef_restriccion, limite_restriccion) else 0
                for ind in poblacion
            ]

            elite = sorted(zip(poblacion, fitness), key=lambda x: x[1], reverse=True)[:parametros["elitismo"]]
            nueva_poblacion.extend([ind for ind, _ in elite])

            while len(nueva_poblacion) < parametros["poblacion"]:
                # Selección
                if parametros["seleccion"] == "Ruleta":
                    padre1 = seleccion_ruleta(fitness, sum(fitness), poblacion)
                    padre2 = seleccion_ruleta(fitness, sum(fitness), poblacion)
                elif parametros["seleccion"] == "Torneo":
                    padre1 = seleccion_torneo(fitness, poblacion)
                    padre2 = seleccion_torneo(fitness, poblacion)
                else:  # Ranking
                    padre1 = seleccion_ranking(fitness, poblacion)
                    padre2 = seleccion_ranking(fitness, poblacion)

                # Cruce
                if random.random() < parametros["cruce"]:
                    if parametros["cruce_tipo"] == "Un punto":
                        hijo1, hijo2 = cruce_un_punto(padre1, padre2, sum(fenotipo))
                    elif parametros["cruce_tipo"] == "Dos puntos":
                        hijo1, hijo2 = cruce_dos_puntos(padre1, padre2, sum(fenotipo))
                    else:
                        hijo1, hijo2 = cruce_uniforme(padre1, padre2, sum(fenotipo))
                else:
                    hijo1, hijo2 = padre1, padre2

                # Mutación
                if parametros["mutacion_tipo"] == "Bit flip":
                    hijo1 = mutacion_bit_flip(hijo1, parametros["mutacion"])
                    hijo2 = mutacion_bit_flip(hijo2, parametros["mutacion"])
                elif parametros["mutacion_tipo"] == "Intercambio":
                    hijo1 = mutacion_intercambio(hijo1)
                    hijo2 = mutacion_intercambio(hijo2)
                else:
                    hijo1 = mutacion_inversion(hijo1, sum(fenotipo) - 1)
                    hijo2 = mutacion_inversion(hijo2, sum(fenotipo) - 1)

                # Validar factibilidad
                if esFactible(hijo1, fenotipo, coef_restriccion, limite_restriccion):
                    nueva_poblacion.append(hijo1)
                if len(nueva_poblacion) < parametros["poblacion"] and esFactible(hijo2, fenotipo, coef_restriccion, limite_restriccion):
                    nueva_poblacion.append(hijo2)

            poblacion = nueva_poblacion

            imprimir_y_guardar(f"Generación {generacion + 1} completada...\n")
            resultados_text.see("end")

            # 📥 Guardar tabla de esta generación (solo en CSV, no en interfaz)
            tabla_generacion = f"\n📋 Generación {generacion + 1}\n"
            tabla_generacion += "N° | Cromosoma binario                 | Fenotipo       | Obj. | Factible\n"
            tabla_generacion += "-"*70 + "\n"

            for i, ind in enumerate(poblacion):
                cromosoma = "".join(str(bit) for bit in ind)
                fenotipo_vals = [int(z) for z in listaDecimales(ind, fenotipo)]
                obj = resultadoFuncion(ind, fenotipo, coef_funcion)
                factible = esFactible(ind, fenotipo, coef_restriccion, limite_restriccion)
                tabla_generacion += f"{i+1:2d} | {cromosoma:28} | {fenotipo_vals} | {obj:5} | {'✔' if factible else '❌'}\n"

            historial_resultados_csv_completo.append(tabla_generacion)
            
            # 🔍 Construir entrada para el JSON
            datos_generacion = {
                "generacion": generacion + 1,
                "individuos": [],
                "mejor": None
            }

            # Guardar datos de individuos
            for ind in poblacion:
                cromosoma = "".join(str(bit) for bit in ind)
                fenotipo_vals = [int(z) for z in listaDecimales(ind, fenotipo)]
                obj = resultadoFuncion(ind, fenotipo, coef_funcion)
                factible = esFactible(ind, fenotipo, coef_restriccion, limite_restriccion)
                
                datos_generacion["individuos"].append({
                    "cromosoma": cromosoma,
                    "fenotipo": fenotipo_vals,
                    "objetivo": obj,
                    "factible": factible
                })

            # Guardar mejor solución de la generación
            mejor_gen = max(poblacion, key=lambda ind: resultadoFuncion(ind, fenotipo, coef_funcion))
            mejor_fenotipo = [int(z) for z in listaDecimales(mejor_gen, fenotipo)]
            datos_generacion["mejor"] = {
                "cromosoma": "".join(str(bit) for bit in mejor_gen),
                "fenotipo": mejor_fenotipo,
                "objetivo": resultadoFuncion(mejor_gen, fenotipo, coef_funcion),
                "factible": esFactible(mejor_gen, fenotipo, coef_restriccion, limite_restriccion)
            }

            # Añadir al historial JSON
            json_generaciones.append(datos_generacion)

            time.sleep(0.05)

        # 6. Mostrar en la interfaz SOLO la última generación y mejor solución

        imprimir_y_guardar("\nTabla de individuos:\n")
        imprimir_y_guardar("N° | Cromosoma binario                 | Fenotipo       | Obj. | Factible\n")
        imprimir_y_guardar("-"*70 + "\n")

        for i, ind in enumerate(poblacion):
            cromosoma = "".join(str(bit) for bit in ind)
            fenotipo_vals = [int(z) for z in listaDecimales(ind, fenotipo)]
            obj = resultadoFuncion(ind, fenotipo, coef_funcion)
            factible = esFactible(ind, fenotipo, coef_restriccion, limite_restriccion)
            imprimir_y_guardar(f"{i+1:2d} | {cromosoma:28} | {fenotipo_vals} | {obj:5} | {'✔' if factible else '❌'}\n")

        mejores = sorted(poblacion, key=lambda ind: resultadoFuncion(ind, fenotipo, coef_funcion), reverse=True)
        mejor = mejores[0]
        resultado = resultadoFuncion(mejor, fenotipo, coef_funcion)
        valores = [int(v) for v in listaDecimales(mejor, fenotipo)]
        # aqui agregue 
        indice_generacion_actual = len(json_generaciones) - 1
        mostrar_generacion(indice_generacion_actual)

        imprimir_y_guardar("\nMejor solución encontrada:\n")
        imprimir_y_guardar(f"Cromosoma: {mejor.tolist()}\n")
        imprimir_y_guardar(f"Fenotipo decodificado: {valores}\n")

        expresion = " + ".join(f"{coef}*X{i+1}" for i, coef in enumerate(coef_funcion))
        valores_str = " + ".join(f"{coef_funcion[i]}*{valores[i]}" for i in range(len(coef_funcion)))
        imprimir_y_guardar(f"Función objetivo: {expresion} = {valores_str} = {resultado}\n")

        restriccion_expr = " + ".join(f"{coef_restriccion[i]}*{valores[i]}" for i in range(len(valores)))
        restriccion_valor = sum(coef_restriccion[i] * valores[i] for i in range(len(valores)))

        cumple = "✔ Cumple restricción" if restriccion_valor <= limite_restriccion else "❌ No cumple restricción"
        imprimir_y_guardar(f"Restricción: {restriccion_expr} = {restriccion_valor} <= {limite_restriccion} → {cumple}\n")
        

        try:
            with open("registro_generaciones.json", "w", encoding="utf-8") as json_file:
                json.dump(json_generaciones, json_file, indent=4, ensure_ascii=False)
        except Exception as e:
            print("No se pudo guardar el archivo JSON:", e)


    except Exception as e:
        messagebox.showerror("Error", f"Error en entrada o ejecución: {str(e)}")


def limpiar_campos():
    for entrada in [entrada_cruce, entrada_mutacion, entrada_tam_poblacion, entrada_generaciones, entrada_elitismo]:
        entrada.delete(0, 'end')
    funcion_objetivo_str.set("")
    funcion_restriccion_str.set("")
    resultados_text.delete("1.0", "end")

def guardar_csv():
    ruta = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if ruta:
        try:
            # Guardar solo los resultados mostrados (última generación)
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(historial_resultados)

            # Guardar todas las generaciones
            ruta_generaciones = ruta.replace(".csv", "_todas_generaciones.csv")
            with open(ruta_generaciones, "w", encoding="utf-8") as f_gen:
                for tabla in historial_resultados_csv_completo:
                    f_gen.write(tabla + "\n")

            messagebox.showinfo("Guardado", f"Se guardó:\n{ruta}\n{ruta_generaciones}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

def guardar_json():
    ruta = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if ruta:
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(json_generaciones, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Guardado", f"JSON de generaciones guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el JSON:\n{e}")

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

    entry_funcion = tk.Entry(seccion_calculadora, width=50)

    # Validación solo para eventos de teclado
    def limitar_entrada_teclado(event):
        tecla = event.char
        if event.keysym in ["BackSpace", "Left", "Right", "Delete", "Tab"]:
            return
        if tecla and tecla not in "0123456789+-*/()xXyY<> =":  # <-- Se agregó el espacio
            return "break"

    entry_funcion.bind("<KeyPress>", limitar_entrada_teclado)
    entry_funcion.pack(pady=5)

    if funcion_activa == "objetivo":
        entry_funcion.insert(0, funcion_objetivo_str.get())
    elif funcion_activa == "restriccion":
        entry_funcion.insert(0, funcion_restriccion_str.get())

    def insertar(texto):
        entry_funcion.insert(tk.END, texto)

    botones = [
        ("+", "+"), ("-", "-"), ("×", "*"), ("÷", "/"),
        ("x²", "^2"), ("x^y", "^"), ("√", "sqrt("), ("ⁿ√", "root("), 
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

# === GUI PRINCIPAL ===
root = tk.Tk()
root.title("Algoritmo Genético - Interfaz Gráfica")
root.geometry("1365x733")

frame_izquierda = tk.Frame(root)
frame_izquierda.pack(side="left", fill="both", expand=True, padx=10, pady=10)

frame_derecha = tk.Frame(root)
frame_derecha.pack(side="right", fill="y", padx=10, pady=10)

# === PARÁMETROS ===
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

# === MÉTODOS ===
frame_metodos = tk.LabelFrame(frame_izquierda, text="🧬 Operadores Genéticos", padx=10, pady=10)
frame_metodos.pack(fill="x", pady=5)

metodo_seleccion = ttk.Combobox(frame_metodos, values=["Ruleta", "Torneo", "Ranking"], state="readonly")
metodo_cruce = ttk.Combobox(frame_metodos, values=["Un punto", "Dos puntos", "Uniforme"], state="readonly")
metodo_mutacion = ttk.Combobox(frame_metodos, values=["Bit flip", "Intercambio", "Inversión"], state="readonly")

tk.Label(frame_metodos, text="Método de Selección:").grid(row=0, column=0, sticky="w")
metodo_seleccion.grid(row=0, column=1, pady=5)
metodo_seleccion.current(0)

tk.Label(frame_metodos, text="Método de Cruce:").grid(row=1, column=0, sticky="w")
metodo_cruce.grid(row=1, column=1, pady=5)
metodo_cruce.current(0)

tk.Label(frame_metodos, text="Método de Mutación:").grid(row=2, column=0, sticky="w")
metodo_mutacion.grid(row=2, column=1, pady=5)
metodo_mutacion.current(0)

# === FUNCIONES ===

frame_funciones = tk.LabelFrame(frame_izquierda, text="🧮 Funciones del Problema", padx=10, pady=10)
frame_funciones.pack(fill="x", pady=5)

funcion_objetivo_str = tk.StringVar(value="")
funcion_restriccion_str = tk.StringVar(value="")

entrada_funcion_objetivo = tk.Label(frame_funciones, textvariable=funcion_objetivo_str, anchor="w", bg="white", relief="solid", width=60, height=1, justify="left")
entrada_funcion_restriccion = tk.Label(frame_funciones, textvariable=funcion_restriccion_str, anchor="w", bg="white", relief="solid", width=60, height=1, justify="left")

tk.Label(frame_funciones, text="Función Objetivo:").grid(row=0, column=0, sticky="nw")
entrada_funcion_objetivo.grid(row=0, column=1, pady=5, sticky="w")
tk.Button(frame_funciones, text="✏️ Editar", command=lambda: mostrar_calculadora("objetivo")).grid(row=0, column=2, padx=5)

tk.Label(frame_funciones, text="Función de Restricción:").grid(row=1, column=0, sticky="nw")
entrada_funcion_restriccion.grid(row=1, column=1, pady=5, sticky="w")
tk.Button(frame_funciones, text="✏️ Editar", command=lambda: mostrar_calculadora("restriccion")).grid(row=1, column=2, padx=5)

# === POBLACIÓN ===
opcion = tk.StringVar(value="s")
frame_poblacion = tk.LabelFrame(frame_izquierda, text="🧪 Población Inicial", padx=10, pady=10)
frame_poblacion.pack(fill="x", pady=5)

ttk.Radiobutton(frame_poblacion, text="Aleatoria", variable=opcion, value="s", command=mostrar_frame).pack(side="left", padx=5)
ttk.Radiobutton(frame_poblacion, text="Predefinida", variable=opcion, value="n", command=mostrar_frame).pack(side="left", padx=5)

frame_si = tk.LabelFrame(frame_poblacion, text="Generar aleatoriamente", padx=10, pady=5)
frame_no = tk.LabelFrame(frame_poblacion, text="Ingresar manualmente", padx=10, pady=5)
mostrar_frame()

# === BOTONES ===
frame_botones = tk.Frame(frame_izquierda)
frame_botones.pack(pady=10)

tk.Button(frame_botones, text="▶ Ejecutar", bg="#4CAF50", fg="white", command=ejecutar_algoritmo_en_hilo).grid(row=0, column=0, padx=10)
tk.Button(frame_botones, text="🧹 Limpiar", bg="#f0ad4e", fg="white", command=limpiar_campos).grid(row=0, column=1, padx=10)
tk.Button(frame_botones, text="💾 Guardar CSV", bg="#0275d8", fg="white", command=guardar_csv).grid(row=0, column=2, padx=10)
tk.Button(frame_botones, text="💾 Guardar Registro en JSON", bg="#fffb00", fg="white", command=guardar_csv).grid(row=0, column=3, padx=10)

# === RESULTADOS ===
frame_resultados = tk.LabelFrame(frame_derecha, text="📊 Resultados", padx=10, pady=10)
frame_resultados.pack(fill="both", expand=True)

#Pa' que quede lindo
frame_navegacion = tk.Frame(frame_derecha)
frame_navegacion.pack(pady=5)

btn_anterior = tk.Button(frame_navegacion, text="⬅ Anterior", command=lambda: cambiar_generacion(-1))
btn_anterior.pack(side="left", padx=5)

btn_siguiente = tk.Button(frame_navegacion, text="Siguiente ➡", command=lambda: cambiar_generacion(1))
btn_siguiente.pack(side="left", padx=5)

tk.Label(frame_navegacion, text="Ir a generación #:").pack(side="left", padx=5)
entrada_generacion_ir = tk.Entry(frame_navegacion, width=5)
entrada_generacion_ir.pack(side="left")

btn_ir = tk.Button(frame_navegacion, text="Ir", command=lambda: ir_a_generacion())
btn_ir.pack(side="left", padx=5)



resultados_text = tk.Text(frame_resultados, wrap="word")
resultados_text.pack(expand=True, fill="both")

root.mainloop()