import re
import math
import random 
import  numpy as np
from enum import Enum

def funcionesAVectores(funcion):
    """Convierte una función algebraica en formato string a una lista de coeficientes enteros.

    La función espera un string con términos separados por '+' y variables representadas como 
    'x', 'X', 'z' o 'Z' (por ejemplo: "2x+3X+4Z+5x"). Extrae los coeficientes numéricos y 
    los convierte a una lista de enteros.

    Args:
        funcion (str): Una cadena con la función en notación algebraica, como "2x+3X+4X".

    Returns:
        List[int]: Una lista de coeficientes enteros extraídos del string.

    Example:
        >>> funcionesAVectores("2x+3X+4X")
        [2, 3, 4]
    """
    funcion = funcion.replace(" ", "")
    funcion = funcion.replace("+", "")
    funcion = re.split(r"[XxZz]", funcion)
    funcion.pop()
    for i in range(len(funcion)):
        funcion[i] = int(funcion[i])
    return funcion

def valoresMaxFenotipoBin(tamFuncion):
    """Solicita al usuario el valor máximo de decisión por fenotipo y calcula los bits necesarios para representarlos.

    Para cada variable (fenotipo), esta función pide al usuario ingresar la cantidad máxima de valores posibles.
    Luego calcula cuántos bits son necesarios para representar dichos valores en binario usando `bit_length()`.

    Args:
        tamFuncion (int): Número de fenotipos o variables de decisión.

    Returns:
        List[int]: Lista con la cantidad de bits necesarios para cada fenotipo.

    Example:
        Supónga que se ingresan los siguientes valores máximos:
        10 → necesita 4 bits
        30 → necesita 5 bits

        >>> valoresMaxFenotipoBin(2)
        Ingresa la cantidad de valores de decisión maxima para el fenotipo (por cada variable son 4 bits) 0 :
        10
        Ingresa la cantidad de valores de decisión maxima para el fenotipo (por cada variable son 4 bits) 1 :
        30
        [4, 5]
    """
    valores = []
    for i in range(tamFuncion):
        print("Ingresa la cantidad de valores de decisión maxima para el fenotipo (por cada variable son 4 bits) ", i, ":")
        valor = (int(input())).bit_length()
        valores.append(valor)
    return valores

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

def generarPoblacionInicial(funcion, restriccion, tamPoblacion, fenotipo):
    """Genera una población inicial de individuos binarios factibles.

    Cada individuo es una lista de bits (0 o 1) cuya longitud total corresponde
    a la suma de los bits necesarios para codificar todas las variables según `fenotipo`.
    Se asegura que cada individuo cumpla con la restricción dada mediante la función `esFactible`.

    Args:
        funcion (List[int]): Coeficientes de la función objetivo.
        restriccion (List[int]): Coeficientes de la función de restricción.
        tamPoblacion (int): Número deseado de individuos en la población.
        fenotipo (List[int]): Lista que indica cuántos bits representa cada variable.

    Returns:
        List[List[int]]: Lista de individuos factibles, donde cada uno es una lista de bits.

    Example:
        >>> generarPoblacionInicial([2, 3], [1, 1], 3, [3, 2])
        [[1, 0, 0, 1, 1], [0, 1, 0, 0, 1], [1, 1, 0, 1, 0]]
    """
    poblacion = []
    while len(poblacion) < tamPoblacion:
        individuo = []
        for i in range(np.sum(fenotipo)):
            individuo.append(random.randint(0,1))
        if esFactible(individuo, fenotipo, funcion, restriccion):
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
        decimal += fraccion[i] * (2 ** ((len(fraccion) - i))-1)
    return decimal

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
        resultado.append(decimal)
        indice += bits
    return resultado

def esFactible(individuo, fenotipo, coef_restriccion, limite_restriccion):
    """
    Verifica si un individuo cumple con la restricción lineal:
    coef1*X1 + coef2*X2 + ... <= limite_restriccion

    Args:
        individuo (List[int]): Cromosoma binario del individuo.
        fenotipo (List[int]): Número de bits por cada variable.
        coef_restriccion (List[int]): Coeficientes de la restricción lineal.
        limite_restriccion (int or float): Límite superior de la restricción.

    Returns:
        bool: True si el individuo cumple la restricción, False si no.
    """
    valores = listaDecimales(individuo, fenotipo)

    suma = sum(c * v for c, v in zip(coef_restriccion, valores))

    return suma <= limite_restriccion

def ingresarPoblacionInicial(poblacionInicial, fenotipo, funcionFitnness, restriccion, tamPoblacion):
    """Permite al usuario ingresar manualmente una población inicial de individuos binarios factibles.

    Para cada individuo, se solicita al usuario una secuencia de bits separados por espacios. 
    Se valida que el número de bits coincida con el tamaño total del fenotipo, y que el individuo cumpla la restricción.

    Args:
        poblacionInicial (List[List[int]]): Lista donde se irán agregando los individuos válidos.
        fenotipo (List[int]): Lista con la cantidad de bits por cada variable (tamaños de fracciones).
        funcionFitnness (List[int]): Coeficientes de la función objetivo usada para verificar factibilidad.
        restriccion (int or float): Límite que los individuos no deben sobrepasar.
        tamPoblacion (int): Número total de individuos que se desea ingresar.

    Returns:
        List[List[int]]: Lista de individuos ingresados manualmente que son válidos.

    Example:
        >>> ingresarPoblacionInicial([], [3,2], [2,3], 20, 2)
        Ingresa los valores binarios del individuo separados por espacios: 1 0 1 0 1
        Ingresa los valores binarios del individuo separados por espacios: 1 1 1 1 0
        [[1, 0, 1, 0, 1], [1, 1, 1, 1, 0]]
    """
    while len(poblacionInicial) < tamPoblacion:
        individuo = input("Ingresa los valores binarios del individuo separados por espacios: ").split(" ")
        if len(individuo) != np.sum(fenotipo):
            print("El número de bits no coincide con el tamaño del fenotipo.")
        else:
            individuo = [int(bit) for bit in individuo]
            if esFactible(individuo, fenotipo, funcionFitnness, restriccion):
                poblacionInicial.append(individuo)
            else:
                print("El individuo no es factible según la restricción.")
    return poblacionInicial

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

def funcionPesos(poblacion, funcion, fenotipo):
    """Calcula el valor de evaluación (peso o fitness) de cada individuo en una población.

    Para cada individuo en la población, aplica la función objetivo decodificando las variables
    a partir de su representación binaria usando el fenotipo.

    Args:
        poblacion (List[List[int]]): Lista de individuos binarios (listas de bits).
        funcion (List[int]): Coeficientes de la función objetivo.
        fenotipo (List[int]): Lista con el número de bits por variable para decodificar cada individuo.

    Returns:
        np.ndarray: Arreglo de valores numéricos (pesos o fitness) correspondientes a cada individuo.

    Example:
        >>> funcionPesos([[1,0,1,0,1], [1,1,0,1,0]], [2,3], [3,2])
        array([13, 17])  # Según cómo decodifique resultadoFuncion()
    """
    pesos = []
    for individuo in poblacion:
        peso = resultadoFuncion(individuo, funcion, fenotipo)
        pesos.append(peso)
    return np.array(pesos)

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
        for i in range(valor):
            fila.append(evaluar_funcion(funcion[pos],valor))
        matriz.append(fila)
        pos += 1
    return matriz

def evaluar_funcion(funcion_str, valor_x):
    """Evalúa una función algebraica representada como string, reemplazando 'x' por un valor numérico.
    La función puede contener operaciones básicas, funciones trigonométricas y raíces.
    Args:
        funcion_str (str): Cadena que representa la función algebraica, como '2x+3x+5x'.
        valor_x (float or int): Valor numérico que reemplazará a 'x' en la función.
    Returns:
        float: Resultado de evaluar la función con el valor dado.
    Example:
        >>> evaluar_funcion("2*x + 3*x + 5*x", 10
        80.0
    """
    # Reemplazar 'x' por su valor numérico
    funcion_str = funcion_str.replace(r"[XxZz]", f"({valor_x})")
    
    # Reemplazos básicos
    funcion = funcion.replace("^", "**")
    funcion = funcion.replace("pi", "math.pi")
    funcion = funcion.replace("e", "math.e")

    # Funciones estándar
    funcion = funcion.replace("sin(", "math.sin(")
    funcion = funcion.replace("cos(", "math.cos(")
    funcion = funcion.replace("tan(", "math.tan(")
    funcion = funcion.replace("log(", "math.log10(")
    funcion = funcion.replace("sqrt(", "math.sqrt(")

    # Funciones recíprocas
    funcion = funcion.replace("cot(", "1/math.tan(")
    funcion = funcion.replace("csc(", "1/math.sin(")
    funcion = funcion.replace("sec(", "1/math.cos(")

    # Reemplazo personalizado para root(n,x) → (x)**(1/n)
    def reemplazo_root(match):
        contenido = match.group(1)
        try:
            n_str, x_str = contenido.split(",")
            return f"({x_str})**(1/({n_str}))"
        except:
            raise ValueError("Error en la sintaxis de root(n,x). Use coma para separar n y x.")

    funcion = re.sub(r"root\((.*?)\)", reemplazo_root, funcion)

    try:
        resultado = eval(funcion, {"math": math})
        return resultado
    except Exception as e:
        raise ValueError(f"Error al evaluar la función: {e}")


def parsear_restriccion(expresion):
    """
    Parsea una expresión como:
    "4130X1 + 4210X2 + 2400X3 + ... <= 16000"
    y retorna:
    ([4130, 4210, 2400, ...], 16000)
    """
    try:
        if "<=" not in expresion:
            raise RestriccionInvalidaError("Falta el operador '<=' en la restricción.")
        
        izquierda, derecha = expresion.split("<=")
        derecha = derecha.strip()

        if not derecha.isdigit():
            raise RestriccionInvalidaError("El valor límite a la derecha de '<=' no es válido.")

        limite = int(derecha)

        # Extraer los coeficientes antes de cada 'Xn'
        coeficientes = re.findall(r'([+-]?\s*\d+)\s*X\d+', izquierda)
        coeficientes = [int(c.replace(" ", "")) for c in coeficientes]

        if not coeficientes:
            raise RestriccionInvalidaError("No se encontraron coeficientes válidos en la restricción.")

        return coeficientes, limite

    except Exception as e:
        raise RestriccionInvalidaError(f"Restricción inválida: {str(e)}")

# Funciones de excepción para manejar errores específicos en la entrada de datos.
# agregamos clases de excepción personalizadas para manejar errores comunes en la entrada de datos.
class EntradaInvalidaError(Exception):
    """Excepción base para todas las entradas inválidas del sistema.

    Esta clase sirve como superclase para errores específicos de entrada.
    Hereda directamente de la clase base `Exception`.
    """
    pass

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