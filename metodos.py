import random 
import  numpy as np
from funciones import *

# Función de evaluación con penalización
def evaluar_poblacion(poblacion, fenotipo, funcion, restriccion):
    """Evalúa el fitness de cada individuo en la población y determina su factibilidad.

    Recorre cada individuo, verifica si es factible según la restricción, y si lo es,
    calcula su fitness usando la función objetivo. En caso contrario, se le asigna un
    valor de fitness de 0 (penalización por inviabilidad).

    Args:
        poblacion (List[List[int]]): Lista de individuos binarios (listas de bits).
        fenotipo (List[int]): Lista con el número de bits por variable.
        funcion (List[int]): Coeficientes de la función objetivo.
        restriccion (int): Valor máximo permitido por la restricción.

    Returns:
        Tuple[np.ndarray, float, np.ndarray]:
            - fitness (np.ndarray): Fitness calculado para cada individuo.
            - total (float): Suma total del fitness (útil para selección por ruleta).
            - factibles (np.ndarray): Arreglo booleano indicando factibilidad de cada individuo.

    Example:
        >>> evaluar_poblacion([[1,0,1,1], [0,1,1,0]], [2,2], [3,2], 10)
        (array([9., 0.]), 9.0, array([ True, False]))
    """
    fitness = np.zeros(len(poblacion))
    factibles = np.zeros(len(poblacion), dtype=bool)
    
    for i, ind in enumerate(poblacion):
        factibles[i] = esFactible(ind, fenotipo, funcion, restriccion)
        if factibles[i]:
            fitness[i] = resultadoFuncion(ind, fenotipo, funcion)
        else:
            fitness[i] = 0  # Penalización por muerte
    
    total = np.sum(fitness)
    return fitness, total, factibles

def seleccion_ruleta(fitness, total_fitness, poblacion):
    """Selecciona un individuo de la población usando el método de ruleta.

    Cada individuo tiene una probabilidad de ser seleccionado proporcional a su fitness.
    Se genera un número aleatorio entre 0 y total_fitness, y se selecciona el primer individuo
    cuyo fitness acumulado lo alcance.

    Args:
        fitness (List[float] or np.ndarray): Lista de valores de fitness por individuo.
        total_fitness (float): Suma total de fitness, usada como límite superior para la ruleta.
        poblacion (List[List[int]]): Lista de individuos (cada uno como lista de bits).

    Returns:
        List[int]: Una copia del individuo seleccionado.

    Raises:
        IndexError: Si la población está vacía o los tamaños de las listas no coinciden.

    Example:
        >>> seleccion_ruleta([10, 30, 60], 100, [[0],[1],[2]])
        [1]  # (resultado puede variar por aleatoriedad)
    """
    if total_fitness > 0:
        r = random.uniform(0, total_fitness)
        acumulado = 0
        for i, f in enumerate(fitness):
            acumulado += f
            if acumulado >= r:
                return poblacion[i].copy()
    return poblacion[-1].copy()

def seleccion_torneo(fitness, poblacion, k=3):
    """Selecciona un individuo usando el método de torneo.

    Se seleccionan aleatoriamente `k` individuos de la población, y se escoge el que tenga
    el mayor valor de fitness. Este método favorece a los individuos más aptos sin eliminar
    totalmente la diversidad.

    Args:
        fitness (List[float] or np.ndarray): Lista de valores de fitness por individuo.
        poblacion (List[List[int]]): Lista de individuos representados como listas de bits.
        k (int, optional): Tamaño del torneo. Debe ser menor o igual al tamaño de la población. Default es 3.

    Returns:
        List[int]: Una copia del individuo ganador del torneo.

    Raises:
        ValueError: Si `k` es mayor que el tamaño de la población.
        IndexError: Si índices generados están fuera del rango.

    Example:
        >>> seleccion_torneo([10, 50, 30], [[0],[1],[2]], k=2)
        [1]  # (puede variar según aleatoriedad)
    """
    participantes = random.sample(range(len(poblacion)), k)
    fitness_array = np.array(fitness)
    mejor_idx = participantes[np.argmax(fitness_array[participantes])]
    return poblacion[mejor_idx].copy()

def seleccion_ranking(fitness, poblacion):
    """Selecciona un individuo usando el método de ranking.

    En lugar de usar directamente los valores de fitness, se ordena la población
    por ranking (de peor a mejor) y se asignan probabilidades proporcionalmente
    a la posición del individuo en ese ranking.

    Esto reduce el riesgo de que un solo individuo con fitness muy alto
    domine la selección, ayudando a mantener la diversidad poblacional.

    Args:
        fitness (List[float] or np.ndarray): Valores de fitness de la población.
        poblacion (List[List[int]]): Lista de individuos (cromosomas binarios).

    Returns:
        List[int]: Una copia del individuo seleccionado por ranking.

    Example:
        >>> seleccion_ranking([10, 30, 20], [[0],[1],[2]])
        [1]  # o [2], dependiendo de las probabilidades generadas
    """
    fitness = np.array(fitness)
    # Ordenar índices por fitness ascendente (menor a mayor)
    indices_ordenados = np.argsort(fitness)
    # Asignar probabilidades basadas en ranking
    probabilidades = np.arange(1, len(poblacion)+1)
    probabilidades = probabilidades / np.sum(probabilidades)
    seleccionado = np.random.choice(indices_ordenados, p=probabilidades)
    return poblacion[seleccionado].copy()

# Métodos de cruce
def cruce_un_punto(padre1, padre2, x):
    """Realiza el cruce de un punto entre dos padres para generar dos hijos.

    Se elige un punto de cruce aleatorio entre 1 y x-1, y se intercambian los
    segmentos de los padres a partir de ese punto. Esto simula la recombinación genética
    simple en algoritmos genéticos.

    Args:
        padre1 (List[int] or np.ndarray): Primer padre (lista de bits).
        padre2 (List[int] or np.ndarray): Segundo padre (lista de bits).
        x (int): Longitud total del cromosoma (debe ser mayor que 1).

    Returns:
        Tuple[np.ndarray, np.ndarray]: Dos hijos resultantes del cruce.

    Raises:
        ValueError: Si x es menor que 2 (no hay punto válido para cruce).

    Example:
        >>> cruce_un_punto(np.array([1, 0, 1]), np.array([0, 1, 0]), 3)
        (array([1, 1, 0]), array([0, 0, 1]))  # resultado puede variar
    """
    punto = random.randint(1, x-1)
    hijo1 = np.concatenate((padre1[:punto], padre2[punto:]))
    hijo2 = np.concatenate((padre2[:punto], padre1[punto:]))
    return hijo1, hijo2

def cruce_dos_puntos(padre1, padre2, x):
    """Realiza un cruce de dos puntos entre dos padres para generar dos hijos.

    Se seleccionan dos puntos de corte aleatorios dentro del cromosoma, y se intercambia
    la sección intermedia entre ambos padres para formar los hijos.

    Args:
        padre1 (List[int] or np.ndarray): Primer padre representado como lista o arreglo de bits.
        padre2 (List[int] or np.ndarray): Segundo padre representado como lista o arreglo de bits.
        x (int): Longitud total del cromosoma (debe ser al menos 3).

    Returns:
        Tuple[np.ndarray, np.ndarray]: Dos hijos resultantes del cruce.

    Raises:
        ValueError: Si x es menor que 3 (no hay espacio suficiente para dos puntos distintos).

    Example:
        >>> cruce_dos_puntos(np.array([1, 1, 0, 0, 1]), np.array([0, 0, 1, 1, 0]), 5)
        (array([1, 0, 1, 0, 1]), array([0, 1, 0, 1, 0]))  # resultado variable
    """
    puntos = sorted(random.sample(range(1, x), 2))
    hijo1 = np.concatenate((padre1[:puntos[0]], padre2[puntos[0]:puntos[1]], padre1[puntos[1]:]))
    hijo2 = np.concatenate((padre2[:puntos[0]], padre1[puntos[0]:puntos[1]], padre2[puntos[1]:]))
    return hijo1, hijo2

def cruce_uniforme(padre1, padre2, x):
    """Realiza un cruce uniforme entre dos padres para generar dos hijos.

    Se genera una máscara binaria aleatoria del mismo tamaño que los padres.
    En cada posición, la máscara decide de cuál padre se toma el gen para
    formar cada hijo. Este método permite una mezcla más equilibrada de los genes.

    Args:
        padre1 (List[int] or np.ndarray): Primer padre representado como arreglo o lista de bits.
        padre2 (List[int] or np.ndarray): Segundo padre representado como arreglo o lista de bits.
        x (int): Longitud del cromosoma (debe coincidir con la longitud de los padres).

    Returns:
        Tuple[np.ndarray, np.ndarray]: Dos hijos resultantes del cruce uniforme.

    Raises:
        ValueError: Si las longitudes de los padres no coinciden con `x`.

    Example:
        >>> cruce_uniforme(np.array([1, 0, 1]), np.array([0, 1, 0]), 3)
        (array([1, 1, 0]), array([0, 0, 1]))  # resultado puede variar
    """
    mascara = np.random.randint(0, 2, size=x)
    hijo1 = np.where(mascara, padre1, padre2)
    hijo2 = np.where(mascara, padre2, padre1)
    return hijo1, hijo2

# Métodos de mutación
def mutacion_bit_flip(individuo, prob_muta):
    """Aplica mutación tipo bit-flip a un individuo con una probabilidad dada.

    Este operador recorre cada bit del cromosoma y, con probabilidad `prob_muta`,
    invierte su valor (0 → 1 o 1 → 0). Es una de las mutaciones más comunes
    en algoritmos genéticos con codificación binaria.

    Args:
        individuo (List[int] or np.ndarray): Cromosoma a mutar.
        prob_muta (float): Probabilidad de mutación por bit (entre 0 y 1).

    Returns:
        List[int] or np.ndarray: Individuo mutado (con posibles bits invertidos).

    Example:
        >>> mutacion_bit_flip([1, 0, 1, 1], 0.25)
        [1, 0, 0, 1]  # resultado puede variar
    """
    mutado = individuo.copy()
    for i in range(len(mutado)):
        if random.random() < prob_muta:
            mutado[i] = 1 - mutado[i]
    return mutado

def mutacion_intercambio(individuo):
    """Aplica mutación por intercambio entre dos genes activos (1s) del individuo.

    Este operador busca dos posiciones donde el gen sea igual a 1 (activo)
    y las intercambia. Solo se realiza si existen al menos dos genes activos.

    Es útil cuando se quiere mantener constante el número de bits activos,
    como en ciertos problemas de optimización con restricciones de cardinalidad.

    Args:
        individuo (List[int] or np.ndarray): Cromosoma a mutar (binario).

    Returns:
        List[int] or np.ndarray: Individuo mutado con intercambio aplicado (si procede).

    Example:
        >>> mutacion_intercambio([0, 1, 0, 1, 1])
        [0, 1, 1, 1, 0]  # resultado puede variar
    """
    mutado = individuo.copy()
    if sum(mutado) > 1:  # Solo si hay al menos dos genes activos
        posiciones = random.sample([i for i, gen in enumerate(mutado) if gen == 1], 2)
        mutado[posiciones[0]], mutado[posiciones[1]] = mutado[posiciones[1]], mutado[posiciones[0]]
    return mutado

def mutacion_inversion(individuo, x):
    """Aplica mutación por inversión de un segmento del cromosoma.

    Se seleccionan dos puntos aleatorios dentro del rango `[0, x]`, y se invierte
    el segmento del cromosoma comprendido entre ellos. Esta mutación es útil
    para explorar nuevas combinaciones preservando parte del orden del individuo.

    Args:
        individuo (List[int] or np.ndarray): Cromosoma binario a mutar.
        x (int): Longitud total del cromosoma.

    Returns:
        List[int] or np.ndarray: Individuo con el segmento invertido.

    Raises:
        ValueError: Si x < 2, ya que no hay segmento invertible.

    Example:
        >>> mutacion_inversion([1, 0, 0, 1, 1], 5)
        [1, 1, 0, 0, 1]  # resultado puede variar
    """
    mutado = individuo.copy()
    puntos = sorted(random.sample(range(x+1), 2))
    mutado[puntos[0]:puntos[1]] = mutado[puntos[0]:puntos[1]][::-1]
    return mutado