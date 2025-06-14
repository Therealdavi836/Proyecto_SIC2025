from funciones import *
from impresion import *
from metodos import *
import matplotlib.pyplot as plt
from tabulate import tabulate

#Parametros
Pcruce = int(input("Ingrese el numero de cruces: " )) / 100
Pmutacion = int(input("Ingrese el porcentaje de mutacion: ")) / 100
tamPoblacion = int(input("Ingrese el tamaño de la población: "))
funcionGlobal = funcionesAVectores(input("Ingrese la función global: "))
funcionFitnness = funcionesAVectores(input("Ingrese la función fitness: "))
restriccion = int(input("Ingrese la restricción: "))
elitismo = 1
respuesta = input("Desea crear una población inicial aleatoria? (s/n): ").lower()
fenotipo = valoresMaxFenotipoBin(tamPoblacion)
continuar = False
if respuesta == 's':
    continuar = True
while continuar:
    poblacionInicial = generarPoblacionInicial(funcionFitnness, restriccion, tamPoblacion, fenotipo)
    #imprimir_tabla(poblacionInicial, funcionFitnness, funcionGlobal, restriccion, 0)
    print(poblacionInicial)
    continuar = (input("Desea continuar con la evolución? (s/n): ").lower()) != 's'
else:
    poblacionInicial = []
iteraciones = int(input("Ingrese el número de iteraciones: "))
variablesDesicion = len(poblacionInicial[0])

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

seleccion = input("Ingrese el tipo de selección 1.ruleta, 2.torneo, 3.ranking: ")
cruce = input("Ingrese el tipo de cruce 1.un punto, 2.dos puntos, 3.uniforme: ")
mutacion = input("Ingrese el tipo de mutación 1.bit flip, 2.intercambio, 3.inversión: ")

operadores = {
        'seleccion': seleccion,
        'cruce': cruce,
        'mutacion': mutacion
    }

poblacion = np.array(poblacionInicial)

# Variables para almacenar estadísticas
historico_fitness = []
historico_factibles = []

# Algoritmo genético principal
for generacion in range(iteraciones):
    # Evaluar población actual
    fitness, total_fitness, factibles = evaluar_poblacion(poblacion, fenotipo, funcionFitnness, restriccion)
    
    # Guardar estadísticas
    historico_fitness.append(total_fitness)
    historico_factibles.append(sum(factibles))
    
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
    while len(nueva_poblacion) < tamPoblacion:
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
                hijo1, hijo2 = cruce_un_punto(padre1, padre2,  variablesDesicion)
            elif operadores['cruce'] == MetodoCruce.DOS_PUNTOS:
                hijo1, hijo2 = cruce_dos_puntos(padre1, padre2, variablesDesicion)
            else:
                hijo1, hijo2 = cruce_uniforme(padre1, padre2, variablesDesicion)
        else:
            hijo1, hijo2 = padre1.copy(), padre2.copy()
        
        # Mutación (usando el método seleccionado para esta generación)
        if operadores['mutacion'] == MetodoMutacion.BIT_FLIP:
            hijo1 = mutacion_bit_flip(hijo1, Pmutacion)
            hijo2 = mutacion_bit_flip(hijo2, Pmutacion)
        elif operadores['mutacion'] == MetodoMutacion.INTERCAMBIO:
            hijo1 = mutacion_intercambio(hijo1)
            hijo2 = mutacion_intercambio(hijo2)
        else:
            hijo1 = mutacion_inversion(hijo1, variablesDesicion)
            hijo2 = mutacion_inversion(hijo2, variablesDesicion)
        
        # Agregar a la nueva población (sin exceder el tamaño)
        if len(nueva_poblacion) < tamPoblacion:
            nueva_poblacion.append(hijo1)
        if len(nueva_poblacion) < tamPoblacion:
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
plt.ylim(0, variablesDesicion)
plt.grid(True)

# Gráfica de operadores usados
# plt.subplot(1, 3, 3)
# operadores_seleccion = [op['seleccion'].name for op in historico_operadores]
# operadores_cruce = [op['cruce'].name for op in historico_operadores]
# operadores_mutacion = [op['mutacion'].name for op in historico_operadores]
# plt.plot(operadores_seleccion, marker='o', label='Selección')
# plt.plot(operadores_cruce, marker='s', label='Cruce')
# plt.plot(operadores_mutacion, marker='^', label='Mutación')
# plt.title("Operadores Utilizados por Generación")
# plt.xlabel("Generación")
# plt.ylabel("Tipo de Operador")
# plt.yticks([])
# plt.legend()
# plt.grid(True)

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