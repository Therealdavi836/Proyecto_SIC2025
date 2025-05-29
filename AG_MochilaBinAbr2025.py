import random
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate

# Configuración inicial
random.seed(1)  # Fijamos semilla para reproducibilidad

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

# Función de selección por ruleta
def seleccion_ruleta(fitness, total_fitness, poblacion):
    r = random.uniform(0, total_fitness)
    acumulado = 0
    for i, f in enumerate(fitness):
        acumulado += f
        if acumulado >= r:
            return poblacion[i].copy()
    return poblacion[-1].copy()  # Por si hay errores de redondeo

# Operador de cruce en un punto
def cruce_un_punto(padre1, padre2):
    punto = random.randint(1, x-1)
    hijo1 = np.concatenate((padre1[:punto], padre2[punto:]))
    hijo2 = np.concatenate((padre2[:punto], padre1[punto:]))
    return hijo1, hijo2

# Operador de mutación bit-flip
def mutar(individuo, prob_muta=Pmuta):
    mutado = individuo.copy()
    for i in range(len(mutado)):
        if random.random() < prob_muta:
            mutado[i] = 1 - mutado[i]
    return mutado

# Función para imprimir tabla detallada
def imprimir_tabla(poblacion, fitness, factibles, iteracion):
    total_fitness = np.sum(fitness)
    probabilidades = fitness / total_fitness if total_fitness > 0 else np.zeros(len(fitness))
    prob_acumulada = np.cumsum(probabilidades)
    
    headers = ["Individuo", "Cromosoma", "Z (Fitness)", "Factible", "Peso", "Probabilidad", "Prob. Acumulada"]
    tabla = []
    
    for i in range(len(poblacion)):
        # Convertir el array NumPy a lista para evitar problemas con tabulate
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
    
    # Imprimir tabla detallada
    imprimir_tabla(poblacion, fitness, factibles, generacion)
    
    # Crear nueva población
    nueva_poblacion = []
    
    # Aplicar elitismo (los mejores pasan directamente)
    if elitismo > 0:
        mejores_indices = np.argsort(fitness)[-elitismo:]
        for idx in mejores_indices:
            nueva_poblacion.append(poblacion[idx].copy())
    
    # Completar la nueva población
    while len(nueva_poblacion) < n:
        # Selección
        padre1 = seleccion_ruleta(fitness, total_fitness, poblacion)
        padre2 = seleccion_ruleta(fitness, total_fitness, poblacion)
        
        # Cruce
        if random.random() < Pcruce:
            hijo1, hijo2 = cruce_un_punto(padre1, padre2)
        else:
            hijo1, hijo2 = padre1.copy(), padre2.copy()
        
        # Mutación
        hijo1 = mutar(hijo1)
        hijo2 = mutar(hijo2)
        
        # Agregar a la nueva población (sin exceder el tamaño)
        if len(nueva_poblacion) < n:
            nueva_poblacion.append(hijo1)
        if len(nueva_poblacion) < n:
            nueva_poblacion.append(hijo2)
    
    # Actualizar población
    poblacion = np.array(nueva_poblacion)

# Gráficas de evolución
plt.figure(figsize=(12, 5))

# Gráfica de fitness
plt.subplot(1, 2, 1)
plt.plot(historico_fitness, marker='o')
plt.title("Evolución del Fitness Total")
plt.xlabel("Generación")
plt.ylabel("Fitness Total")
plt.grid(True)

# Gráfica de individuos factibles
plt.subplot(1, 2, 2)
plt.plot(historico_factibles, marker='o', color='orange')
plt.title("Evolución de Individuos Factibles")
plt.xlabel("Generación")
plt.ylabel("Número de Factibles")
plt.ylim(0, n)
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