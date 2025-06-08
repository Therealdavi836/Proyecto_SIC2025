import random 
import  numpy as np
from funciones import esFactible

# Función de evaluación con penalización
def evaluar_poblacion(poblacion, funcion):
    fitness = np.zeros(len(poblacion))
    factibles = np.zeros(len(poblacion), dtype=bool)
    
    for i, ind in enumerate(poblacion):
        factibles[i] = esFactible(ind)
        if factibles[i]:
            fitness[i] = np.sum(ind * funcion)
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

# Métodos de cruce
def cruce_un_punto(padre1, padre2, x):
    punto = random.randint(1, x-1)
    hijo1 = np.concatenate((padre1[:punto], padre2[punto:]))
    hijo2 = np.concatenate((padre2[:punto], padre1[punto:]))
    return hijo1, hijo2

def cruce_dos_puntos(padre1, padre2, x):
    puntos = sorted(random.sample(range(1, x), 2))
    hijo1 = np.concatenate((padre1[:puntos[0]], padre2[puntos[0]:puntos[1]], padre1[puntos[1]:]))
    hijo2 = np.concatenate((padre2[:puntos[0]], padre1[puntos[0]:puntos[1]], padre2[puntos[1]:]))
    return hijo1, hijo2

def cruce_uniforme(padre1, padre2, x):
    mascara = np.random.randint(0, 2, size=x)
    hijo1 = np.where(mascara, padre1, padre2)
    hijo2 = np.where(mascara, padre2, padre1)
    return hijo1, hijo2

# Métodos de mutación
def mutacion_bit_flip(individuo, prob_muta):
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

def mutacion_inversion(individuo, x):
    mutado = individuo.copy()
    puntos = sorted(random.sample(range(x+1), 2))
    mutado[puntos[0]:puntos[1]] = mutado[puntos[0]:puntos[1]][::-1]
    return mutado