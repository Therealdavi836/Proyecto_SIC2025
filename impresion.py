import  numpy as np
from tabulate import tabulate
from funciones import *

# Función para imprimir tabla detallada
def imprimir_tabla(poblacion, fitness, factibles, pesos, iteracion, operadores=None,):
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

#Funsion imprimir tabal de mejores individuos
def imprimir_tabla_mejores_individuos(totalpoblacion, totalpesos, totalfitness, iteracion,):
    
    headers = ["Individuo", "Cromosoma", "Z (Fitness)", "Costo Mejor individuo", "Probabilidad", "Prob. Acumulada"]
    tabla = []
    
    for i in range(len(totalpoblacion)):
        fitness = totalfitness[i]
        total_fitness = np.sum(fitness)
        pesos = totalpesos[i]
        poblacion = totalpoblacion[i]
        probabilidades = fitness / total_fitness if total_fitness > 0 else np.zeros(len(fitness))
        prob_acumulada = np.cumsum(probabilidades)
        mayorIndividuo = mayor(fitness)
        tabla.append([
            i,
            poblacion[mayorIndividuo],
            fitness[mayorIndividuo],
            pesos[mayorIndividuo],
            f"{probabilidades[mayorIndividuo]:.4f}" if total_fitness > 0 else "0.0000",
            f"{prob_acumulada[mayorIndividuo]:.4f}" if total_fitness > 0 else "0.0000"
        ])

    print(f"\n--- Generación {iteracion} ---")
    if operadores:
        print(f"Operadores usados: Selección={operadores['seleccion'].name}, Cruce={operadores['cruce'].name}, Mutación={operadores['mutacion'].name}")
    print(f"Fitness total: {total_fitness:.2f}")
    print(f"Individuos factibles: {sum(factibles)}/{len(factibles)}")
    print(tabulate(tabla, headers=headers, tablefmt="grid", floatfmt=".4f"))
