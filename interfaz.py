import tkinter as tk
import random
import threading
import time
import traceback
import json
from tkinter import ttk, messagebox, filedialog
from funciones import *
from metodos import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Variables globales necesarias
# Ague esta variable global para los checkpints
indice_generacion_actual = 0  # Controla qué generación se está mostrando
seccion_calculadora = None
funcion_activa = None

def mostrar_grafica():
    global json_generaciones
    
    if not json_generaciones:
        messagebox.showinfo("Información", "Primero ejecute el algoritmo para generar datos")
        return
    
    # Crear ventana emergente para la gráfica
    ventana_grafica = tk.Toplevel(root)
    ventana_grafica.title("Evolución del Algoritmo Genético")
    ventana_grafica.geometry("800x600")
    
    fig = Figure(figsize=(8, 6), dpi=100)
    ax = fig.add_subplot(111)
    
    # Preparar datos para la gráfica
    generaciones = [g['generacion'] for g in json_generaciones]
    mejores_valores = [g['mejor']['objetivo'] for g in json_generaciones]
    promedios = [sum(ind['objetivo'] for ind in g['individuos'])/len(g['individuos']) 
                 for g in json_generaciones]
    
    # Crear gráfico
    ax.plot(generaciones, mejores_valores, 'g-', linewidth=2, label='Mejor Individuo')
    ax.plot(generaciones, promedios, 'b--', linewidth=1, label='Promedio Población')
    ax.set_title('Evolución del Fitness por Generación', fontsize=14)
    ax.set_xlabel('Generación', fontsize=12)
    ax.set_ylabel('Valor de Fitness', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    # Integrar gráfica en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=ventana_grafica)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Botón para guardar la imagen
    btn_guardar = tk.Button(ventana_grafica, text="💾 Guardar Gráfica", 
                           command=lambda: guardar_grafica(fig))
    btn_guardar.pack(pady=10)

def guardar_grafica(fig):
    ruta = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
    )
    if ruta:
        fig.savefig(ruta, dpi=300)
        messagebox.showinfo("Éxito", f"Gráfica guardada en:\n{ruta}")

def validar_y_ejecutar():
    """"Valida los parámetros ingresados y ejecuta el algoritmo genético si son correctos.
    Valida que todos los campos estén llenos, que las funciones objetivo y restricción estén definidas,
    y que la población inicial esté guardada. Si todo es correcto, inicia el algoritmo en un hilo separado.
    """
    # Validar parámetros
    parametros = [
        entrada_cruce, entrada_mutacion, entrada_convergencia,
        entrada_tam_poblacion, entrada_generaciones, entrada_elitismo,
        entrada_restriccion, entrada_numero_variables
    ]

    if any(not entrada.get().strip() for entrada in parametros):
        messagebox.showerror("Error", "No se ingresaron todos los parámetros.")
        return

    # Validar funciones
    if not funcion_objetivo_str.get().strip() or not funcion_restriccion_str.get().strip():
        messagebox.showerror("Error", "No ha ingresado todas las funciones.")
        return

    # Validar población
    if poblacion_guardada is None:
        messagebox.showerror("Error", "Falta la población inicial.")
        return

    # Si pasa todas las validaciones, ejecuta el algoritmo
    ejecutar_algoritmo_en_hilo()

def mostrar_generacion(indice):
    global json_generaciones, resultados_text

    if 0 <= indice < len(json_generaciones):
        resultados_text.delete("1.0", "end")
        gen = json_generaciones[indice]

        resultados_text.insert("end", f"📋 Generación {gen['generacion']}\n")
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
            "convergencia": float(entrada_convergencia.get()) / 100,
            "poblacion": int(entrada_tam_poblacion.get()),
            "generaciones": int(entrada_generaciones.get()),
            "elitismo": int(entrada_elitismo.get()),
            "restriccion": int(entrada_restriccion.get()),
            "variables_decision": int(entrada_numero_variables.get()),
            "seleccion": metodo_seleccion.get(),
            "cruce_tipo": metodo_cruce.get(),
            "mutacion_tipo": metodo_mutacion.get(),
        }
        # 2. varaibles globales
        global valores_variables_decision, poblacion_guardada
        if any(valor == 0 for valor in valores_variables_decision):
            raise ValorVariableInvalidoError()

        # 3 creación del fenotipo el cual contine el tamaño parqa representar en binario cada variable de decisión
        fenotipo = []
        for valor in valores_variables_decision:
            fenotipo.append(valor.bit_length())
        
        # 4. Obtener las funciones objetivo y restricción, y sus valores
        funcion_objetivo = funcion_objetivo_str.get().split("+")
        valores_funcion_objetivo = resultados_funcion(funcion_objetivo, valores_variables_decision)

        funcion_restriccion = funcion_restriccion_str.get().split("+")
        valores_funcion_restriccion = resultados_funcion(funcion_restriccion, valores_variables_decision)
        poblacion = poblacion_guardada

        # 5. Preparar la interfaz
        resultados_text.delete("1.0", "end")
        imprimir_y_guardar("🧬 Ejecutando algoritmo genético...\n")
        root.update_idletasks()

        # 6. Evolución
        generacion = 0
        while generacion < parametros["generaciones"] and igualdad(poblacion, parametros["convergencia"]):
            nueva_poblacion = []

            fitness = []
            for individuo in poblacion:
                fitness.append(suma_funcion(individuo, valores_funcion_objetivo))

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
                
                padre1 = decimales_a_binario(padre1, fenotipo)
                padre2 = decimales_a_binario(padre2, fenotipo)

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
                
                hijo1 = listaDecimales(hijo1, fenotipo)
                hijo2 = listaDecimales(hijo2, fenotipo)

                # Validar factibilidad
                if esFactible(hijo1, parametros["restriccion"], valores_funcion_restriccion):
                    nueva_poblacion.append(hijo1)
                if len(nueva_poblacion) < parametros["poblacion"] and esFactible(hijo2, parametros["restriccion"], valores_funcion_restriccion):
                    nueva_poblacion.append(hijo2)

            poblacion = nueva_poblacion
            generacion += 1


            imprimir_y_guardar(f"Generación {generacion + 1} completada...\n")
            resultados_text.see("end")

            # 📥 Guardar tabla de esta generación (solo en CSV, no en interfaz)
            tabla_generacion = f"\n📋 Generación {generacion + 1}\n"
            tabla_generacion += "N° | Cromosoma binario                 | Fenotipo       | Obj. | Factible\n"
            tabla_generacion += "-"*70 + "\n"

            for i, ind in enumerate(poblacion):
                cromosoma = "".join(str(bit) for bit in ind)
                fenotipo_vals = [int(z) for z in listaDecimales(ind, fenotipo)]
                obj = suma_funcion(ind, valores_funcion_objetivo)
                factible = esFactible(ind, parametros["restriccion"], valores_funcion_restriccion)
                tabla_generacion += f"{i+1:2d} | {cromosoma:28} | {fenotipo_vals} | {obj:5} | {'✔' if factible else '❌'}\n"

            historial_resultados_csv_completo.append(tabla_generacion)
            
            # 🔍 Construir entrada para el JSON
            datos_generacion = {
                "generacion": generacion,
                "individuos": [],
                "mejor": None
            }

            # Guardar datos de individuos
            for ind in poblacion:
                cromosoma = "".join(str(bit) for bit in ind)
                fenotipo_vals = [int(z) for z in listaDecimales(ind, fenotipo)]
                obj = suma_funcion(ind, valores_funcion_objetivo)
                factible = esFactible(ind, parametros["restriccion"], valores_funcion_restriccion)
                
                datos_generacion["individuos"].append({
                    "cromosoma": cromosoma,
                    "fenotipo": fenotipo_vals,
                    "objetivo": obj,
                    "factible": factible
                })

            # Guardar mejor solución de la generación
            mejor_gen = max(poblacion, key=lambda ind: suma_funcion(ind, valores_funcion_objetivo))
            mejor_fenotipo = [int(z) for z in listaDecimales(mejor_gen, fenotipo)]
            datos_generacion["mejor"] = {
                "cromosoma": "".join(str(bit) for bit in mejor_gen),
                "fenotipo": mejor_fenotipo,
                "objetivo": suma_funcion(mejor_gen, valores_funcion_objetivo),
                "factible": esFactible(mejor_gen, parametros["restriccion"], valores_funcion_restriccion)
            }

            # Añadir al historial JSON
            json_generaciones.append(datos_generacion)

            time.sleep(0.05)

         # 7. Verificar si se encontraron soluciones y calcular el mejor individuo
        if not poblacion:
            imprimir_y_guardar("\n❌ El algoritmo no encontró ninguna solución factible.")
            messagebox.showwarning("Finalizado", "No se encontraron soluciones factibles.")
            return

        # PRIMERO: Calcular la mejor solución de la población final
        mejores = sorted(poblacion, key=lambda ind: suma_funcion(ind, valores_funcion_objetivo), reverse=True)
        mejor = mejores[0]
        resultado = suma_funcion(mejor, valores_funcion_objetivo)
        valores = [int(v) for v in listaDecimales(mejor, fenotipo)]

        # SEGUNDO: Mostrar la tabla de la última generación en la interfaz
        imprimir_y_guardar("\n--- Tabla de la Última Generación ---\n")
        for i, ind in enumerate(poblacion):
            # Tu código para imprimir la tabla de la población ya estaba aquí y era correcto
            cromosoma_bin = decimales_a_binario(ind, fenotipo)
            cromosoma_str = "".join(map(str, cromosoma_bin))
            obj = suma_funcion(ind, valores_funcion_objetivo)
            factible = esFactible(ind, parametros["restriccion"], valores_funcion_restriccion)
            fenotipo_limpio = [int(v) for v in ind]  # convierte cada valor a int puro
            imprimir_y_guardar(f"{i+1:2d} | {cromosoma_str:28} | {fenotipo_limpio} | {obj:5.2f} | {'✔' if factible else '❌'}\n")

        # TERCERO: Actualizar la tabla visual con la navegación
        indice_generacion_actual = len(json_generaciones) - 1
        mostrar_generacion(indice_generacion_actual)

        # CUARTO: Mostrar el resumen de la mejor solución encontrada
        imprimir_y_guardar("\n--- Mejor Solución Global Encontrada ---\n")
        mejor_cromosoma_bin = decimales_a_binario(mejor, fenotipo)
        imprimir_y_guardar(f"Cromosoma: {"".join(map(str, mejor_cromosoma_bin))}\n")
        imprimir_y_guardar(f"Fenotipo decodificado: {valores}\n")

        expresion = funcion_objetivo_str.get()
        valores_str = " + ".join(f"{funcion_objetivo[i]}*{valores[i]}" for i in range(len(funcion_objetivo)))
        imprimir_y_guardar(f"Función objetivo: {expresion} = {valores_str} = {resultado:.2f}\n")

        restriccion_str = funcion_restriccion_str.get()
        restriccion_expr = " + ".join(f"{funcion_restriccion[i]}*{valores[i]}" for i in range(len(valores)))
        restriccion_valor = suma_funcion(valores, valores_funcion_restriccion) # Corregido para usar la función correcta
        
        cumple = "✔ Cumple restricción" if restriccion_valor <= parametros["restriccion"] else "❌ No cumple restricción"
        imprimir_y_guardar(f"Restricción: {restriccion_str} => {restriccion_expr} = {restriccion_valor:.2f} <= {parametros['restriccion']} → {cumple}\n")

        # --- FIN DEL BLOQUE CORREGIDO ---

        try:
            with open("registro_generaciones.json", "w", encoding="utf-8") as json_file:
                json.dump(json_generaciones, json_file, indent=4, ensure_ascii=False)
        except Exception as e:
            print("No se pudo guardar el archivo JSON:", e)
            
        
    except Exception as e:
        messagebox.showerror("Error", f"Error en entrada o ejecución: {str(e)}")
        print("Error detallado en consola:")
        traceback.print_exc()


def limpiar_campos():
    for entrada in [entrada_cruce, entrada_mutacion, entrada_convergencia, entrada_tam_poblacion, entrada_generaciones, entrada_elitismo, entrada_restriccion, entrada_numero_variables]:
        entrada.delete(0, 'end')
    funcion_objetivo_str.set("")
    funcion_restriccion_str.set("")
    resultados_text.delete("1.0", "end")

def guardar_csv():
    ruta = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if ruta:
        try:
        # Guardar solo los resultados mostrados
            with open(ruta, "w", encoding="utf-8-sig") as f:
                f.write(historial_resultados)

            # Guardar todas las generaciones
            ruta_generaciones = ruta.replace(".csv", "_todas_generaciones.csv")
            with open(ruta_generaciones, "w", encoding="utf-8-sig") as f_gen:
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

def mostrar_calculadora(label_tipo):
    """Muestra la sección de edición de funciones (objetivo o restricción) en la interfaz.
    Crea una sección con un campo de entrada para la función y botones para insertar operadores.
    Permite validar la cantidad de variables y guardar la función editada.
    """
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
        ("+", "+"), ("-", "-"), ("*", "*"), ("÷", "/"),
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

        # Contar x, X, y, Y
        cantidad_variables = sum(texto.count(var) for var in ["x", "X", "y", "Y"])

        try:
            cantidad_esperada = int(entrada_numero_variables.get())
        except ValueError:
            messagebox.showerror("Error", "El valor de cantidad de variables debe ser un número entero.")
            return

        if cantidad_variables != cantidad_esperada:
            messagebox.showwarning("Cantidad no coincide",
                                f"Cantidad de variables encontradas: {cantidad_variables}\n"
                                f"Cantidad esperada: {cantidad_esperada}")
            return

        # Guardar si pasa la validación
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

cantidad_var = tk.StringVar()
labels = ["Porcentaje de Cruce (%)", "Porcentaje de Mutación (%)", "Porcentaje de Convergencia (%)", 
        "Tamaño de Población", "Número de Generaciones", "Elitismo", 
        "Restricción de Factibilidad", "Cantidad de variables"]

entradas = []

# Número de elementos por columna
mitad = len(labels) // 2

for i, texto in enumerate(labels):
    col = 0 if i < mitad else 2         # Columna izquierda o derecha
    row = i if i < mitad else i - mitad # Reajuste de fila para derecha

    tk.Label(frame_parametros, text=texto).grid(row=row, column=col, sticky="w", padx=5, pady=5)

    if texto == "Cantidad de variables":
        entrada = tk.Entry(frame_parametros, textvariable=cantidad_var)
    else:
        entrada = tk.Entry(frame_parametros)

    entrada.grid(row=row, column=col + 1, padx=5, pady=5)
    entradas.append(entrada)

entrada_cruce, entrada_mutacion, entrada_convergencia, entrada_tam_poblacion, entrada_generaciones, entrada_elitismo, entrada_restriccion, entrada_numero_variables = entradas
# === MÉTODOS ===
frame_metodos = tk.LabelFrame(frame_izquierda, text="🧬 Operadores Genéticos", padx=10, pady=10)
frame_metodos.pack(fill="x", pady=5)

metodo_seleccion = ttk.Combobox(frame_metodos, values=["Ruleta", "Torneo", "Ranking"], state="readonly")
metodo_cruce = ttk.Combobox(frame_metodos, values=["Un punto", "Dos puntos", "Uniforme"], state="readonly")
metodo_mutacion = ttk.Combobox(frame_metodos, values=["Bit flip", "Intercam bio", "Inversión"], state="readonly")

tk.Label(frame_metodos, text="Método de Selección:").grid(row=0, column=0, sticky="w")
metodo_seleccion.grid(row=0, column=1, pady=5)
metodo_seleccion.current(0)

tk.Label(frame_metodos, text="Método de Cruce:").grid(row=1, column=0, sticky="w")
metodo_cruce.grid(row=1, column=1, pady=5)
metodo_cruce.current(0)

tk.Label(frame_metodos, text="Método de Mutación:").grid(row=0, column=2, sticky="w")
metodo_mutacion.grid(row=0, column=3, pady=5)
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

# ==== Frame dinámico para las variables de decisión (se muestra sin evento externo) ====
valores_variables_decision = []  # Lista inicializada con 1s cuando haya cantidad válida

frame_variables_decision = tk.LabelFrame(frame_izquierda, text="🔢 Variables de Decisión", padx=10, pady=10)
frame_variables_decision.pack(fill="x", pady=5)

# Label que muestra el texto fijo
tk.Label(frame_variables_decision, text="Valor máximo de las variables de decisión:").grid(row=0, column=0, sticky="w")

# Label dinámico que muestra la lista de valores
var_lista_str = tk.StringVar(value="")
label_lista_valores = tk.Label(frame_variables_decision, textvariable=var_lista_str, fg="blue")
label_lista_valores.grid(row=0, column=1, padx=5)

# Botón para abrir el editor
def abrir_editor_variables():
    if not valores_variables_decision:
        return

    ventana = tk.Toplevel()
    ventana.title("Editar Variables de Decisión")
    entradas_locales = []

    for i, valor in enumerate(valores_variables_decision):
        tk.Label(ventana, text=f"Var {i+1}:").grid(row=i, column=0, padx=5, pady=5)
        var = tk.StringVar(value=str(valor))
        entry = tk.Entry(ventana, textvariable=var, width=10)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entradas_locales.append(var)

    def guardar():
        try:
            for i, var in enumerate(entradas_locales):
                valores_variables_decision[i] = int(var.get())
            var_lista_str.set(str(valores_variables_decision).replace(",", ""))
            ventana.destroy()
        except ValueError:
            messagebox.showerror("Error", "Todos los valores deben ser enteros.")

    def cancelar():
        ventana.destroy()

    # Botones
    tk.Button(ventana, text="Guardar", command=guardar, bg="green", fg="white").grid(row=len(valores_variables_decision), column=0, padx=5, pady=10)
    tk.Button(ventana, text="Cancelar", command=cancelar, bg="red", fg="white").grid(row=len(valores_variables_decision), column=1, padx=5, pady=10)

tk.Button(frame_variables_decision, text="Editar", command=abrir_editor_variables).grid(row=0, column=2, padx=10)

# Función que inicializa la lista al escribir cantidad válida en entrada_numero_variables
def inicializar_lista_variables(*args):
    global valores_variables_decision
    try:
        n = int(entrada_numero_variables.get())
        if n > 0:
            valores_variables_decision = [1] * n
            var_lista_str.set(str(valores_variables_decision).replace(",", ""))
        else:
            valores_variables_decision = []
            var_lista_str.set("")
    except ValueError:
        valores_variables_decision = []
        var_lista_str.set("")

cantidad_var.trace_add("write", inicializar_lista_variables)

# ==== Frame de Población ====
frame_poblacion = tk.LabelFrame(frame_izquierda, text="🧪 Población Inicial", padx=10, pady=10)
frame_poblacion.pack(fill="x", pady=5)

# Variable global para guardar la población actual
poblacion_guardada = None

def abrir_generar_aleatoria():
    # Validación de entradas requeridas
    if not entrada_tam_poblacion.get().strip() or \
        not entrada_restriccion.get().strip() or \
        not entrada_numero_variables.get().strip() or \
        not funcion_restriccion_str.get().strip() or \
        not valores_variables_decision:
        messagebox.showerror("Error", "Faltan valores necesarios para generar la población aleatoria.")
        return

    def generar():
        nonlocal matriz_generada
        for widget in frame_tabla.winfo_children():
            widget.destroy()

        restriccion = int(entrada_restriccion.get())
        poblacion = int(entrada_tam_poblacion.get())
        funcion_restriccion = funcion_restriccion_str.get().split("+")
        valores_funcion = resultados_funcion(funcion_restriccion, valores_variables_decision)

        matriz_generada = generarPoblacionInicial(restriccion, poblacion, valores_variables_decision, valores_funcion)

        for i, fila in enumerate(matriz_generada):
            for j, valor in enumerate(fila):
                tk.Label(frame_tabla, text=str(valor), borderwidth=1, relief="solid", width=8)\
                    .grid(row=i, column=j, padx=1, pady=1)

    def guardar():
        global poblacion_guardada
        poblacion_guardada = matriz_generada
        messagebox.showinfo("Guardado", "La población ha sido guardada.")
        ventana.destroy()

    def cancelar():
        ventana.destroy()

    ventana = tk.Toplevel()
    ventana.title("Generar Población Aleatoria")
    ventana.grab_set()

    matriz_generada = []

    frame_tabla = tk.Frame(ventana)
    frame_tabla.pack(padx=10, pady=10)

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=5)

    tk.Button(frame_botones, text="Guardar", command=guardar, width=10).pack(side="left", padx=5)
    tk.Button(frame_botones, text="Generar de nuevo", command=generar, width=15).pack(side="left", padx=5)
    tk.Button(frame_botones, text="Cancelar", command=cancelar, width=10).pack(side="left", padx=5)

    generar()

def abrir_ingresar_predefinida():
    # Validación de entradas requeridas
    if not entrada_tam_poblacion.get().strip() or \
        not entrada_numero_variables.get().strip() or \
        not valores_variables_decision:
        messagebox.showerror("Error", "Faltan valores necesarios para ingresar la población predefinida.")
        return

    entradas_tabla = []

    def guardar():
        global poblacion_guardada
        matriz = []

        for i, fila in enumerate(entradas_tabla):
            fila_valores = []
            for j, e in enumerate(fila):
                try:
                    valor = float(e.get())
                except ValueError:
                    messagebox.showerror("Error", f"Todos los valores deben ser numéricos. Fila {i+1}, Columna {j+1}")
                    return

                # Validación del rango
                if valor > valores_variables_decision[j]:
                    messagebox.showerror("Error",
                        f"El valor en la fila {i+1}, columna {j+1} excede el máximo permitido: {valores_variables_decision[j]}")
                    return

                fila_valores.append(valor)
            matriz.append(fila_valores)

        poblacion_guardada = matriz
        messagebox.showinfo("Guardado", "Población predefinida guardada exitosamente.")
        ventana.destroy()

    def cancelar():
        ventana.destroy()

    ventana = tk.Toplevel()
    ventana.title("Ingresar Población Predefinida")
    ventana.grab_set()

    filas = int(entrada_tam_poblacion.get())
    columnas = len(valores_variables_decision)

    frame_tabla = tk.Frame(ventana)
    frame_tabla.pack(padx=10, pady=10)

    for i in range(filas):
        fila_entries = []
        for j in range(columnas):
            e = tk.Entry(frame_tabla, width=8)

            # Si hay población guardada, insertar el valor correspondiente
            if poblacion_guardada and i < len(poblacion_guardada) and j < len(poblacion_guardada[i]):
                e.insert(0, str(poblacion_guardada[i][j]))

            e.grid(row=i, column=j, padx=1, pady=1)
            fila_entries.append(e)

        entradas_tabla.append(fila_entries)

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=5)

    tk.Button(frame_botones, text="Guardar", command=guardar, width=10).pack(side="left", padx=5)
    tk.Button(frame_botones, text="Cancelar", command=cancelar, width=10).pack(side="left", padx=5)



def mostrar_poblacion_guardada():
    if not poblacion_guardada:
        messagebox.showwarning("Sin datos", "Aún no has guardado ninguna población.")
        return

    ventana = tk.Toplevel()
    ventana.title("Población Guardada")
    ventana.grab_set()

    frame_tabla = tk.Frame(ventana)
    frame_tabla.pack(padx=10, pady=10)

    for i, fila in enumerate(poblacion_guardada):
        for j, valor in enumerate(fila):
            label = tk.Label(frame_tabla, text=str(valor), borderwidth=1, relief="solid", width=8)
            label.grid(row=i, column=j, padx=1, pady=1)

    tk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)

# === Botones principales ===
tk.Button(frame_poblacion, text="🎲 Generar Población Aleatorio", command=abrir_generar_aleatoria).pack(fill="x", pady=2)
tk.Button(frame_poblacion, text="📝 Ingresar Población Predefinida", command=abrir_ingresar_predefinida).pack(fill="x", pady=2)
tk.Button(frame_poblacion, text="📋 Ver Población", command=mostrar_poblacion_guardada).pack(fill="x", pady=2)


# === BOTONES ===
frame_botones = tk.Frame(frame_izquierda)
frame_botones.pack(pady=10)

tk.Button(frame_botones, text="▶ Ejecutar", bg="#4CAF50", fg="white", command=validar_y_ejecutar).grid(row=0, column=0, padx=10)
tk.Button(frame_botones, text="🧹 Limpiar", bg="#f0ad4e", fg="white", command=limpiar_campos).grid(row=0, column=1, padx=10)
tk.Button(frame_botones, text="💾 Guardar CSV", bg="#0275d8", fg="white", command=guardar_csv).grid(row=0, column=2, padx=10)
tk.Button(frame_botones, text="💾 Guardar Registro en JSON", bg="#0bbbe8", fg="white", command=guardar_json).grid(row=0, column=3, padx=10)
tk.Button(frame_botones, text="📊 Visualizar Gráfica", bg="#9b59b6", fg="white",command=mostrar_grafica).grid(row=0, column=4, padx=10)
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