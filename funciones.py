import re
import math
import random 
import  numpy as np
from enum import Enum

def resultadoFuncion(individuo, fenotipo, funcion):
    """Calcula el valor de una función objetivo dado un individuo binario y su fenotipo asociado.

    Divide el cromosoma binario (`individuo`) en secciones según los tamaños definidos por `fenotipo`,
    convierte cada sección a decimal y multiplica por el coeficiente correspondiente de la función.

    Args:
        individuo (List[int]): Lista de bits (0s y 1s) que representa el cromosoma del individuo.
        fenotipo (List[int]): Lista con los tamaños (en bits) de cada variable codificada.
        funcion (List[int]): Lista de coeficientes correspondientes a cada variable.

    Returns:
        int or float: Resultado de evaluar la función objetivo con los valores decodificados del individuo.

    Example:
        Supónga:
            individuo = [1,0,1, 0,1]   (codifica 2 variables)
            fenotipo = [3, 2]          (primer var = 3 bits, segundo = 2 bits)
            funcion = [2, 5]           (coeficientes)
        
        Decodificado:
            [1,0,1] = 5  →  5 * 2 = 10
            [0,1]   = 1  →  1 * 5 = 5

        Resultado: 10 + 5 = 15

        >>> resultadoFuncion([1,0,1,0,1], [3,2], [2,5])
        15
    """
    inicio = 0
    fin = fenotipo[0]
    resultado = 0
    for i in range(len(fenotipo)):
        fraccion = individuo[inicio:fin]
        resultado += convertirBinarioADecimal(fraccion)* funcion[i]
        inicio = fin
        if fin < len(individuo):
            fin +=  fenotipo[i+1]
    return resultado

def generarPoblacionInicial(restriccion, tamPoblacion, variables_decision, valores_funcion):
    """Genera una población inicial de individuos decimales factibles.
    Crea una lista de individuos donde cada individuo es una lista de enteros aleatorios,
    asegurando que cada uno cumple con una restricción lineal definida por `restriccion`.
    Args:
        restriccion (int or float): Límite superior de la restricción lineal que los individuos deben cumplir.
        tamPoblacion (int): Número total de individuos a generar.
        variables_decision (List[int]): Lista con el número de variables de decisión (no se usa directamente aquí).
        valores_funcion (List[List[int]]): Matriz donde cada fila contiene los valores posibles para cada variable.
    Returns:
        List[List[int]]: Lista de individuos, donde cada individuo es una lista de enteros
        que representan los valores de las variables de decisión.
    Example:
        >>> generarPoblacionInicial(16000, 5, [3, 2], [[0, 1, 2], [0, 1]])
        [[1, 0], [2, 1], [0, 1], [1, 0], [2, 0]]
    """
    poblacion = []
    while len(poblacion) < tamPoblacion:
        individuo = []
        for valor in variables_decision:
            individuo.append(random.randint(0,valor))
        if esFactible(individuo, restriccion, valores_funcion, variables_decision):
            poblacion.append(individuo)
    return poblacion

def convertirBinarioADecimal(fraccion):
    """Convierte una fracción binaria (lista de bits) a su valor decimal equivalente.

    Interpreta los bits como una representación binaria con el bit más significativo al inicio.
    Usa la fórmula estándar de conversión binaria.

    Args:
        fraccion (List[int]): Lista de bits (0 o 1) que representa un número binario.

    Returns:
        int: Valor decimal correspondiente.

    Example:
        >>> convertirBinarioADecimal([1, 0, 1])
        5
        >>> convertirBinarioADecimal([1, 1, 1])
        7
    """
    decimal = 0
    for i in range(len(fraccion)):
        decimal += fraccion[i] * (2 ** ((len(fraccion) - i - 1)))
    return decimal

def decimales_a_binario(valores, tamaños):
    """Convierte una lista de valores decimales a su representación binaria con tamaños específicos.
    Cada valor decimal se convierte a binario y se rellena con ceros a la izquierda según el tamaño especificado.
    Args:
        valores (List[int]): Lista de valores decimales a convertir.
        tamaños (List[int]): Lista con el número de bits que debe tener cada valor en su representación binaria.
    Returns:
        List[int]: Lista de bits (0s y 1s) que representa la concatenación de todos los valores binarios.
    Example:
        >>> decimales_a_binario([5, 3], [3, 2])
        [1, 0, 1, 1, 1]  # 5 en binario es '101' y 3 en binario es '11'
    """
    resultado = []
    for valor, tamaño in zip(valores, tamaños):
        binario = format(valor, f'0{tamaño}b')  # Convierte a binario con ceros a la izquierda
        resultado.extend([int(bit) for bit in binario])  # Convierte cada bit a entero y lo añade a la lista
    return resultado

def listaDecimales(individuo, fenotipo):
    """
    Convierte un individuo binario en una lista de valores decimales por cada variable.

    Divide el cromosoma binario (`individuo`) en secciones según los tamaños definidos en `fenotipo`,
    y convierte cada sección binaria en su equivalente decimal.

    Args:
        individuo (List[int]): Lista de bits que representa un individuo.
        fenotipo (List[int]): Lista con la cantidad de bits por cada variable.

    Returns:
        List[int]: Lista de valores decimales correspondientes a cada variable.
    """
    resultado = []
    indice = 0
    for bits in fenotipo:
        segmento = individuo[indice:indice + bits]
        decimal = convertirBinarioADecimal(segmento)
        resultado.append(int(decimal))
        indice += bits
    return resultado

def esFactible(individuo, restriccion, valores_funcion, fenotipo):
    """Verifica si un individuo cumple con una restricción lineal.
    Calcula el valor de la función objetivo para el individuo dado y verifica si está dentro del límite permitido.
    Args:
        individuo (List[int]): Lista de enteros que representa un individuo en la población.
        restriccion (int or float): Límite superior de la restricción lineal que el individuo debe cumplir.
        valores_funcion (List[List[int]]): Matriz donde cada fila contiene los valores posibles para cada variable.
    Returns:
        bool: True si el individuo es factible (cumple la restricción), False en caso contrario.
    Example:
        >>> esFactible([1, 0,], 20, [[2, 3], [4, 5]])
        True
        >>> esFactible([0, 2], 10, [[2, 3], [4, 5]])
        False
    """
    resultado = 0
    for i in range(len(individuo)):
        if fenotipo[i]<individuo[i]:
            return False
        resultado += valores_funcion[i][individuo[i]]
    return resultado <= restriccion

def igualdad(poblacion, Pterminacion):
    """Verifica si una población ha convergido según un porcentaje de terminación dado.

    Compara cuántos individuos son idénticos entre sí y evalúa si el porcentaje de individuos 
    iguales supera el umbral de terminación. Si la proporción de individuos duplicados 
    es suficientemente alta, se considera que la población ha convergido.

    Args:
        poblacion (List[List[int]]): Lista de individuos (listas de bits) en la población actual.
        Pterminacion (float): Porcentaje de convergencia deseado (valor entre 0 y 1).

    Returns:
        bool: True si la población no ha alcanzado el porcentaje de convergencia, False si ha convergido.

    Example:
        >>> igualdad([[1,0,1], [1,0,1], [0,1,0]], 0.6)
        True  # No ha convergido aún (solo 2 de 3 son iguales)
    """
    mayor = 0
    for individuo1 in range(len(poblacion)-1):
        contador = 0
        for individuo2 in range(individuo1+1, len(poblacion)):
            if np.array_equal(poblacion[individuo1], poblacion[individuo2]):
                contador += 1
        if contador > mayor:
            mayor = contador
    return mayor/len(poblacion) < Pterminacion

def mayor(fitness):
    """Encuentra el índice del individuo con el mayor valor de fitness.

    Recorre la lista de valores de fitness y devuelve el índice del individuo con el valor más alto.

    Args:
        fitness (List[float] or List[int]): Lista de valores de aptitud (fitness) de cada individuo.

    Returns:
        int: Índice del individuo con el mayor fitness.

    Example:
        >>> mayor([12, 20, 18, 9])
        1
    """
    mayor = 0
    for i in range(len(fitness)):
        if fitness[i] > fitness[mayor]:
            mayor = i
    return mayor

def suma_funcion(individuo, resultado_funcion):
    """Calcula la suma de los valores de la función objetivo para un individuo dado.

    Suma los valores de la función objetivo para cada variable del individuo, usando los resultados
    previamente calculados en `resultado_funcion`.

    Args:
        individuo (List[int]): Lista de bits que representa un individuo.
        resultado_funcion (List[float]): Lista con los resultados de la función objetivo para cada variable.

    Returns:
        float: Suma total de los valores de la función objetivo para el individuo.

    Example:
        >>> suma_funcion([1, 0, 1], [2.0, 3.0, 4.0])
        9.0
    """
    suma = 0
    for i in range(len(individuo)):
        suma += resultado_funcion[i][individuo[i]]
    return suma

def resultados_funcion(funcion, fenotipo,):
    """Genera una matriz de resultados para cada valor del fenotipo según la función dada.
    Para cada valor en el fenotipo, evalúa la función con los coeficientes correspondientes y
    construye una matriz donde cada fila representa un valor del fenotipo y cada columna
    representa el resultado de aplicar la función a ese valor.
    Args:
        funcion (List[int]): Lista de coeficientes de la función objetivo.
        fenotipo (List[int]): Lista con los valores máximos de decisión para cada variable. 
    Returns:
        List[List[float]]: Matriz donde cada fila corresponde a un valor del fenotipo
        y cada columna es el resultado de aplicar la función a ese valor.
    Example:
        >>> funcion = [2, 3, 4]
        >>> fenotipo = [1, 2, 3]
        >>> resultados_funcion(funcion, fenotipo)
        [[2.0, 3.0, 4.0], [4.0, 6.0, 8.0], [6.0, 9.0, 12.0]]
    """
    matriz = []
    pos = 0
    for valor in fenotipo:
        fila = []
        for i in range(valor+1):
            fila.append(evaluar_funcion(funcion[pos],i))
        matriz.append(fila)
        pos += 1
    return matriz

def evaluar_funcion(funcion_str, valor_x):
    """Evalúa una función algebraica representada como string, reemplazando 'x' por un valor numérico.
    La función puede contener operaciones básicas, funciones trigonométricas y raíces.
    Args:
        funcion_str (str): Cadena que representa la función algebraica, como '2x'.
        valor_x (float or int): Valor numérico que reemplazará a 'x' en la función.
    Returns:
        float: Resultado de evaluar la función con el valor dado.
    Example:
        >>> evaluar_funcion("2*x")
        80.0
    """
    funcion_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', funcion_str)
    # Reemplazar 'x' por su valor numérico
    funcion_str = re.sub(r"[XxZz]", f"({valor_x})", funcion_str)    

    # Reemplazos básicos
    funcion_str = funcion_str.replace("^", "**")
    funcion_str = funcion_str.replace("pi", "math.pi")
    funcion_str = funcion_str.replace("e", "math.e")

    # funcion_stres estándar
    funcion_str = funcion_str.replace("sin(", "math.sin(")
    funcion_str = funcion_str.replace("cos(", "math.cos(")
    funcion_str = funcion_str.replace("tan(", "math.tan(")
    funcion_str = funcion_str.replace("log(", "math.log10(")
    funcion_str = funcion_str.replace("sqrt(", "math.sqrt(")

    # funcion_stres recíprocas
    funcion_str = funcion_str.replace("cot(", "1/math.tan(")
    funcion_str = funcion_str.replace("csc(", "1/math.sin(")
    funcion_str = funcion_str.replace("sec(", "1/math.cos(")

    # Reemplazo personalizado para root(n,x) → (x)**(1/n)
    def reemplazo_root(match):
        contenido = match.group(1)
        try:
            n_str, x_str = contenido.split(",")
            return f"({x_str})**(1/({n_str}))"
        except:
            raise ValueError("Error en la sintaxis de root(n,x). Use coma para separar n y x.")

    funcion_str = re.sub(r"root\((.*?)\)", reemplazo_root, funcion_str)
    try:
        resultado = eval(funcion_str, {"math": math})
        return resultado
    except Exception as e:
        raise ValueError(f"Error al evaluar la función: {e}")

# Funciones de excepción para manejar errores específicos en la entrada de datos.
# agregamos clases de excepción personalizadas para manejar errores comunes en la entrada de datos.
class EntradaInvalidaError(Exception):
    """Excepción base para todas las entradas inválidas del sistema.

    Esta clase sirve como superclase para errores específicos de entrada.
    Hereda directamente de la clase base `Exception`.
    """
    pass

class ValorVariableInvalidoError(EntradaInvalidaError):
    """Se lanza cuando el valor máximo de una variable de decisión es 0."""
    def __init__(self):
        super().__init__("El valor máximo para cada variable de decisión debe ser 1 o mayor. No se permiten ceros.")
class ValorNoEnteroError(EntradaInvalidaError):
    """Se lanza cuando se espera un número entero pero se recibe otro tipo de dato.

    Args:
        campo (str): Nombre del campo donde ocurrió el error.
    """
    def __init__(self, campo):
        super().__init__(f"El valor para {campo} debe ser un número entero")

class PorcentajeInvalidoError(EntradaInvalidaError):
    """Se lanza cuando un porcentaje proporcionado no está en el rango 0-100.

    Args:
        campo (str): Nombre del campo afectado.
    """
    def __init__(self, campo):
        super().__init__(f"El porcentaje para {campo} debe estar entre 0 y 100")

class FormatoFuncionInvalidoError(EntradaInvalidaError):
    """Se lanza cuando el formato de la función ingresada no es válido.

    El formato válido debe ser algo como: '2x+3x+5x' o '4z+1z'.
    """
    def __init__(self):
        super().__init__("El formato de la función debe ser similar a '2x+3X' o '4z+5z'")

class OpcionInvalidaError(EntradaInvalidaError):
    """Se lanza cuando se ingresa una opción no válida.

    Acepta únicamente las opciones 's' o 'n'.
    """
    def __init__(self):
        super().__init__("La opción debe ser 's' o 'n'")

class TamañoPoblacionInvalidoError(EntradaInvalidaError):
    """Se lanza cuando el tamaño de la población es menor al mínimo permitido.

    El valor debe ser un entero mayor o igual a 1.
    """
    def __init__(self):
        super().__init__("El tamaño de la población debe ser al menos 1")

class RestriccionInvalidaError(EntradaInvalidaError):
    """Se lanza cuando la restricción ingresada no es un número entero válido."""
    def __init__(self):
        super().__init__("La restricción debe ser un número entero válido")

class OpcionOperadorInvalidaError(EntradaInvalidaError):
    """Se lanza cuando se selecciona una opción inválida para un operador.

    Args:
        operador (str): Nombre del operador afectado (por ejemplo, 'mutación').
        opciones_validas (List[str] or List[int]): Lista de opciones válidas aceptadas.
    """
    def __init__(self, operador, opciones_validas):
        super().__init__(f"Opción inválida para {operador}. Las opciones válidas son: {opciones_validas}")
class RestriccionInvalidaError(Exception):
    pass

# Funciones de validación para asegurar que los datos ingresados por el usuario sean correctos.
def validar_entero(valor, campo):
    """Valida que el valor ingresado sea un número entero.

    Args:
        valor (Any): El valor a validar (puede venir como string).
        campo (str): Nombre del campo, usado para mensajes de error.

    Returns:
        int: Valor convertido a entero.

    Raises:
        ValorNoEnteroError: Si el valor no puede convertirse a entero.

    Example:
        >>> validar_entero("10", "generaciones")
        10
    """
    try:
        return int(valor)
    except ValueError:
        raise ValorNoEnteroError(campo)

def validar_porcentaje(valor, campo):
    """Valida que el valor sea un porcentaje válido entre 0 y 100.

    Args:
        valor (Any): Valor a validar (puede ser string o número).
        campo (str): Nombre del campo, usado para mensajes de error.

    Returns:
        float: Porcentaje convertido a decimal (por ejemplo, 0.75 para 75).

    Raises:
        PorcentajeInvalidoError: Si el valor está fuera de rango.
        ValorNoEnteroError: Si no es un entero.

    Example:
        >>> validar_porcentaje("80", "cruce")
        0.8
    """
    valor = validar_entero(valor, campo)
    if valor < 0 or valor > 100:
        raise PorcentajeInvalidoError(campo)
    return valor / 100

def validar_tamano_poblacion(valor):
    """Valida que el tamaño de población sea un entero mayor o igual a 1.

    Args:
        valor (Any): Valor del tamaño a validar.

    Returns:
        int: Tamaño de población válido.

    Raises:
        TamañoPoblacionInvalidoError: Si el valor es menor a 1.
        ValorNoEnteroError: Si el valor no es entero.

    Example:
        >>> validar_tamano_poblacion("30")
        30
    """
    valor = validar_entero(valor, "tamaño de población")
    if valor < 1:
        raise TamañoPoblacionInvalidoError()
    return valor

def validar_funcion(funcion_str):
    """Valida que la función tenga un formato algebraico básico válido.

    Args:
        funcion_str (str): String de la función, como '2x+3x+4x'.

    Returns:
        str: Función validada (sin modificaciones).

    Raises:
        FormatoFuncionInvalidoError: Si el formato no contiene variables válidas.

    Example:
        >>> validar_funcion("2x+3x+5x")
        '2x+3x+5x'
    """
    if not any(c in funcion_str for c in ['x', 'X', 'y', 'Y', 'z', 'Z']):
        raise FormatoFuncionInvalidoError()
    return funcion_str

def validar_opcion(opcion):
    """Valida que una opción sea 's' o 'n'.

    Args:
        opcion (str): Letra que representa la elección (sí/no).

    Returns:
        str: Letra en minúscula ('s' o 'n').

    Raises:
        OpcionInvalidaError: Si no es 's' ni 'n'.

    Example:
        >>> validar_opcion("S")
        's'
    """
    opcion = opcion.lower()
    if opcion not in ['s', 'n']:
        raise OpcionInvalidaError()
    return opcion

def validar_restriccion(valor):
    """Valida que la restricción sea un número entero válido.

    Args:
        valor (Any): Valor a validar.

    Returns:
        int: Valor entero de la restricción.

    Raises:
        RestriccionInvalidaError: Si no se puede convertir a entero.

    Example:
        >>> validar_restriccion("15")
        15
    """
    try:
        return int(valor)
    except ValueError:
        raise RestriccionInvalidaError()

def validar_opcion_operador(valor, operador, opciones_validas):
    """Valida que la opción seleccionada para un operador esté entre las válidas.

    Args:
        valor (Any): Valor de entrada a convertir y validar.
        operador (str): Nombre del operador ('selección', 'cruce', etc.).
        opciones_validas (List[int]): Lista con las opciones válidas (ej: [1,2,3]).

    Returns:
        int: Opción seleccionada convertida a entero.

    Raises:
        OpcionOperadorInvalidaError: Si no está dentro de las opciones válidas o no es entero.

    Example:
        >>> validar_opcion_operador("2", "cruce", [1,2,3])
        2
    """
    try:
        valor_int = int(valor)
        if valor_int not in opciones_validas:
            raise OpcionOperadorInvalidaError(operador, opciones_validas)
        return valor_int
    except ValueError:
        raise OpcionOperadorInvalidaError(operador, opciones_validas)