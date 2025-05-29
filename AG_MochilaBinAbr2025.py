import random
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
from enum import Enum

# Configuración inicial
random.seed(1)  # Fijamos semilla para reproducibilidad

# Enumeración para métodos de selección
class MetodoSeleccion(Enum):
    RULETA = 1
    TORNEO = 2
    RANKING = 3

# Enumeración para métodos de cruce
class MetodoCruce(Enum):
    UN_PUNTO = 1
    DOS_PUNTOS = 2
    UNIFORME = 3

# Enumeración para métodos de mutación
class MetodoMutacion(Enum):
    BIT_FLIP = 1
    INTERCAMBIO = 2
    INVERSION = 3

# Parámetros del algoritmo
x = 6  # Número de variables de decisión (proyectos)
n = 6  # Número de individuos en la población
Pcruce = 0.95  # Probabilidad de cruce
Pmuta = 0.05   # Probabilidad de mutación
elitismo = 1    # Número de individuos elitistas que pasan directamente
iteraciones = 5 # Número de iteraciones

# Datos del problema
utilidad = [409, 1718, 2000, 2008, 2075, 1800]  # Coeficientes de Z
pesos = [4130, 4210, 2400, 2420, 2020, 5200]    # Coeficientes de P
capacidad_max = 16000  # Restricción de presupuesto

# Población inicial (del Excel)
cromosomas = [
    [0, 1, 1, 0, 0, 0],  # Individuo 1
    [1, 0, 0, 0, 1, 1],  # Individuo 2
    [0, 0, 0, 1, 1, 0],  # Individuo 3
    [1, 0, 1, 1, 1, 0],  # Individuo 4
    [0, 1, 0, 0, 1, 1],  # Individuo 5
    [0, 1, 1, 1, 0, 0]   # Individuo 6
]
poblacion = np.array(cromosomas)

# Variables para almacenar estadísticas
historico_fitness = []
historico_factibles = []
historico_operadores = []

# Función para verificar factibilidad
def es_factible(cromosoma):
    peso_total = np.sum(cromosoma * pesos)
    return peso_total <= capacidad_max

# Función de evaluación con penalización
def evaluar_poblacion(poblacion):
    fitness = np.zeros(len(poblacion))
    factibles = np.zeros(len(poblacion), dtype=bool)
    
    for i, ind in enumerate(poblacion):
        factibles[i] = es_factible(ind)
        if factibles[i]:
            fitness[i] = np.sum(ind * utilidad)
        else:
            fitness[i] = 0  # Penalización por muerte
    
    total = np.sum(fitness)
    return fitness, total, factibles

# Métodos de selección
def seleccion_ruleta(fitness, total_fitness, poblacion):
    r = random.uniform(0, total_fitness)
    acumulado = 0
    for i, f in enumerate(fitness):
        acumulado += f
        if acumulado >= r:
            return poblacion[i].copy()
    return poblacion[-1].copy()

def seleccion_torneo(fitness, poblacion, k=3):
    participantes = random.sample(range(len(poblacion)), k)
    mejor_idx = participantes[np.argmax(fitness[participantes])]
    return poblacion[mejor_idx].copy()

def seleccion_ranking(fitness, poblacion):
    # Ordenar por fitness
    indices_ordenados = np.argsort(fitness)
    # Asignar probabilidades basadas en ranking
    probabilidades = np.arange(1, len(poblacion)+1)
    probabilidades = probabilidades / np.sum(probabilidades)
    seleccionado = np.random.choice(indices_ordenados, p=probabilidades)
    return poblacion[seleccionado].copy()

def seleccion_aleatoria(fitness, total_fitness, poblacion):
    metodo = random.choice(list(MetodoSeleccion))
    if metodo == MetodoSeleccion.RULETA:
        return seleccion_ruleta(fitness, total_fitness, poblacion)
    elif metodo == MetodoSeleccion.TORNEO:
        return seleccion_torneo(fitness, poblacion)
    else:
        return seleccion_ranking(fitness, poblacion)

# Métodos de cruce
def cruce_un_punto(padre1, padre2):
    punto = random.randint(1, x-1)
    hijo1 = np.concatenate((padre1[:punto], padre2[punto:]))
    hijo2 = np.concatenate((padre2[:punto], padre1[punto:]))
    return hijo1, hijo2

def cruce_dos_puntos(padre1, padre2):
    puntos = sorted(random.sample(range(1, x), 2))
    hijo1 = np.concatenate((padre1[:puntos[0]], padre2[puntos[0]:puntos[1]], padre1[puntos[1]:]))
    hijo2 = np.concatenate((padre2[:puntos[0]], padre1[puntos[0]:puntos[1]], padre2[puntos[1]:]))
    return hijo1, hijo2

def cruce_uniforme(padre1, padre2):
    mascara = np.random.randint(0, 2, size=x)
    hijo1 = np.where(mascara, padre1, padre2)
    hijo2 = np.where(mascara, padre2, padre1)
    return hijo1, hijo2

def cruce_aleatorio(padre1, padre2):
    metodo = random.choice(list(MetodoCruce))
    if metodo == MetodoCruce.UN_PUNTO:
        return cruce_un_punto(padre1, padre2)
    elif metodo == MetodoCruce.DOS_PUNTOS:
        return cruce_dos_puntos(padre1, padre2)
    else:
        return cruce_uniforme(padre1, padre2)

# Métodos de mutación
def mutacion_bit_flip(individuo, prob_muta=Pmuta):
    mutado = individuo.copy()
    for i in range(len(mutado)):
        if random.random() < prob_muta:
            mutado[i] = 1 - mutado[i]
    return mutado

def mutacion_intercambio(individuo):
    mutado = individuo.copy()
    if sum(mutado) > 1:  # Solo si hay al menos dos genes activos
        posiciones = random.sample([i for i, gen in enumerate(mutado) if gen == 1], 2)
        mutado[posiciones[0]], mutado[posiciones[1]] = mutado[posiciones[1]], mutado[posiciones[0]]
    return mutado

def mutacion_inversion(individuo):
    mutado = individuo.copy()
    puntos = sorted(random.sample(range(x+1), 2))
    mutado[puntos[0]:puntos[1]] = mutado[puntos[0]:puntos[1]][::-1]
    return mutado

def mutacion_aleatoria(individuo, prob_muta=Pmuta):
    metodo = random.choice(list(MetodoMutacion))
    if metodo == MetodoMutacion.BIT_FLIP:
        return mutacion_bit_flip(individuo, prob_muta)
    elif metodo == MetodoMutacion.INTERCAMBIO:
        return mutacion_intercambio(individuo)
    else:
        return mutacion_inversion(individuo)

# Función para imprimir tabla detallada
def imprimir_tabla(poblacion, fitness, factibles, iteracion, operadores=None):
    total_fitness = np.sum(fitness)
    probabilidades = fitness / total_fitness if total_fitness > 0 else np.zeros(len(fitness))
    prob_acumulada = np.cumsum(probabilidades)
    
    headers = ["Individuo", "Cromosoma", "Z (Fitness)", "Factible", "Peso", "Probabilidad", "Prob. Acumulada"]
    tabla = []
    
    for i in range(len(poblacion)):
        cromosoma_lista = poblacion[i].tolist()
        peso = np.sum(poblacion[i] * pesos)
        tabla.append([
            i+1,
            cromosoma_lista,
            fitness[i],
            "Sí" if factibles[i] else "No",
            peso,
            f"{probabilidades[i]:.4f}" if total_fitness > 0 else "0.0000",
            f"{prob_acumulada[i]:.4f}" if total_fitness > 0 else "0.0000"
        ])
    
    print(f"\n--- Generación {iteracion} ---")
    if operadores:
        print(f"Operadores usados: Selección={operadores['seleccion'].name}, Cruce={operadores['cruce'].name}, Mutación={operadores['mutacion'].name}")
    print(f"Fitness total: {total_fitness:.2f}")
    print(f"Individuos factibles: {sum(factibles)}/{len(factibles)}")
    print(tabulate(tabla, headers=headers, tablefmt="grid", floatfmt=".4f"))

# Algoritmo genético principal
for generacion in range(iteraciones):
    # Evaluar población actual
    fitness, total_fitness, factibles = evaluar_poblacion(poblacion)
    
    # Guardar estadísticas
    historico_fitness.append(total_fitness)
    historico_factibles.append(sum(factibles))
    
    # Seleccionar operadores aleatoriamente para esta generación
    operadores = {
        'seleccion': random.choice(list(MetodoSeleccion)),
        'cruce': random.choice(list(MetodoCruce)),
        'mutacion': random.choice(list(MetodoMutacion))
    }
    historico_operadores.append(operadores)
    
    # Imprimir tabla detallada
    imprimir_tabla(poblacion, fitness, factibles, generacion, operadores)
    
    # Crear nueva población
    nueva_poblacion = []
    
    # Aplicar elitismo (los mejores pasan directamente)
    if elitismo > 0:
        mejores_indices = np.argsort(fitness)[-elitismo:]
        for idx in mejores_indices:
            nueva_poblacion.append(poblacion[idx].copy())
    
    # Completar la nueva población
    while len(nueva_poblacion) < n:
        # Selección (usando el método seleccionado para esta generación)
        if operadores['seleccion'] == MetodoSeleccion.RULETA:
            padre1 = seleccion_ruleta(fitness, total_fitness, poblacion)
            padre2 = seleccion_ruleta(fitness, total_fitness, poblacion)
        elif operadores['seleccion'] == MetodoSeleccion.TORNEO:
            padre1 = seleccion_torneo(fitness, poblacion)
            padre2 = seleccion_torneo(fitness, poblacion)
        else:
            padre1 = seleccion_ranking(fitness, poblacion)
            padre2 = seleccion_ranking(fitness, poblacion)
        
        # Cruce (usando el método seleccionado para esta generación)
        if random.random() < Pcruce:
            if operadores['cruce'] == MetodoCruce.UN_PUNTO:
                hijo1, hijo2 = cruce_un_punto(padre1, padre2)
            elif operadores['cruce'] == MetodoCruce.DOS_PUNTOS:
                hijo1, hijo2 = cruce_dos_puntos(padre1, padre2)
            else:
                hijo1, hijo2 = cruce_uniforme(padre1, padre2)
        else:
            hijo1, hijo2 = padre1.copy(), padre2.copy()
        
        # Mutación (usando el método seleccionado para esta generación)
        if operadores['mutacion'] == MetodoMutacion.BIT_FLIP:
            hijo1 = mutacion_bit_flip(hijo1)
            hijo2 = mutacion_bit_flip(hijo2)
        elif operadores['mutacion'] == MetodoMutacion.INTERCAMBIO:
            hijo1 = mutacion_intercambio(hijo1)
            hijo2 = mutacion_intercambio(hijo2)
        else:
            hijo1 = mutacion_inversion(hijo1)
            hijo2 = mutacion_inversion(hijo2)
        
        # Agregar a la nueva población (sin exceder el tamaño)
        if len(nueva_poblacion) < n:
            nueva_poblacion.append(hijo1)
        if len(nueva_poblacion) < n:
            nueva_poblacion.append(hijo2)
    
    # Actualizar población
    poblacion = np.array(nueva_poblacion)

# Gráficas de evolución
plt.figure(figsize=(15, 5))

# Gráfica de fitness
plt.subplot(1, 3, 1)
plt.plot(historico_fitness, marker='o')
plt.title("Evolución del Fitness Total")
plt.xlabel("Generación")
plt.ylabel("Fitness Total")
plt.grid(True)

# Gráfica de individuos factibles
plt.subplot(1, 3, 2)
plt.plot(historico_factibles, marker='o', color='orange')
plt.title("Evolución de Individuos Factibles")
plt.xlabel("Generación")
plt.ylabel("Número de Factibles")
plt.ylim(0, n)
plt.grid(True)

# Gráfica de operadores usados
plt.subplot(1, 3, 3)
operadores_seleccion = [op['seleccion'].name for op in historico_operadores]
operadores_cruce = [op['cruce'].name for op in historico_operadores]
operadores_mutacion = [op['mutacion'].name for op in historico_operadores]
plt.plot(operadores_seleccion, marker='o', label='Selección')
plt.plot(operadores_cruce, marker='s', label='Cruce')
plt.plot(operadores_mutacion, marker='^', label='Mutación')
plt.title("Operadores Utilizados por Generación")
plt.xlabel("Generación")
plt.ylabel("Tipo de Operador")
plt.yticks([])
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# Mostrar mejor solución encontrada
fitness_final, _, factibles_final = evaluar_poblacion(poblacion)
mejor_idx = np.argmax(fitness_final)
mejor_individuo = poblacion[mejor_idx]
mejor_fitness = fitness_final[mejor_idx]
mejor_factible = factibles_final[mejor_idx]
mejor_peso = np.sum(mejor_individuo * pesos)

print("\n--- Mejor Solución Encontrada ---")
print(f"Cromosoma: {mejor_individuo.tolist()}")
print(f"Fitness (Z): {mejor_fitness}")
print(f"Factible: {'Sí' if mejor_factible else 'No'}")
print(f"Peso total: {mejor_peso} (Límite: {capacidad_max})")
print(f"Proyectos seleccionados: {[i+1 for i, gen in enumerate(mejor_individuo) if gen == 1]}")