import re
import random 
import  numpy as np
from enum import Enum


# Función que toma un string y devuelve una lista de enteros.
# El string debe estar en el formato "2x+3X+4X+5X" o similar, donde los números son los coeficientes
def funcionesAVectores(funcion):
    funcion = funcion.replace(" ", "")
    funcion = funcion.replace("+", "")
    funcion = re.split(r"[XxZz]", funcion)
    funcion.pop()
    for i in range(len(funcion)):
        funcion[i] = int(funcion[i])
    return funcion

# Función que solicita al usuario la cantidad de valores máximos de decisión para cada fenotipo.
# Todo esto para saber cuántos bits se necesitan para representar cada fenotipo en binario.
# Ademas para saber los rangos de los valores de cada fenotipo.
def valoresMaxFenotipoBin(tamFuncion):
    valores = []
    for i in range(tamFuncion):
        print("Ingresa la cantidad de valores de decisión maxima para el fenotipo (por cada variable son 4 bits) ", i, ":")
        valor = (int(input())).bit_length()
        valores.append(valor)
    return valores

# Función que calcula el resultado de una función dada un individuo y su fenotipo.
# El individuo es una lista de bits y el fenotipo es una lista de enteros que indica el tamaño de cada fracción.
def resultadoFuncion(individuo, fenotipo, funcion):
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

# Función que genera una población inicial de individuos.
# Cada individuo es una lista de bits que representa un fenotipo.
def generarPoblacionInicial(funcion, restriccion, tamPoblacion, fenotipo):
    poblacion = []
    while len(poblacion) < tamPoblacion:
        individuo = []
        for i in range(np.sum(fenotipo)):
            individuo.append(random.randint(0,1))
        if esFactible(individuo, fenotipo, funcion, restriccion):
            poblacion.append(individuo)
    return poblacion

# Función que convierte una fracción binaria a decimal.
# La fracción es una lista de bits y se convierte a decimal usando la fórmula de conversión binaria.
def convertirBinarioADecimal(fraccion):
    decimal = 0
    for i in range(len(fraccion)):
        decimal += fraccion[i] * (2 ** ((len(fraccion) - i))-1)
    return decimal

# Función que convierte un individuo en una lista de decimales.
# El individuo es una lista de bits y el fenotipo es una lista de enteros que indica el tamaño de cada fracción.
def listaDecimales(individuo, fenotipo):
    inicio = 0
    fin = fenotipo[0]
    resultado = []
    for i in range(len(fenotipo)-1):
        fraccion = individuo[inicio:fin]
        resultado.append(convertirBinarioADecimal(fraccion))
        inicio += fin
        fin +=  fenotipo[i+1]
    return resultado

# Función que verifica si un individuo es factible según una restricción.
def esFactible(individuo, fenotipo, funcion, restriccion):
    """
    Verifica si un individuo es factible según la restricción dada.
    Un individuo es factible si el resultado de la función es menor que la restricción.
    """
    return resultadoFuncion(individuo, fenotipo, funcion) < restriccion

# Función que ingresa una población inicial de individuos.
# La función solicita al usuario que ingrese los valores binarios de cada individuo.
def ingresarPoblacionInicial(poblacionInicial, fenotipo, funcionFitnness, restriccion, tamPoblacion):
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

# Función que verifica si los individuos de una población son iguales según un porcentaje de terminación.
# La función compara cada individuo con los demás y cuenta cuántos son iguales.
def igualdad(poblacion, Pterminacion):
    mayor = 0
    for individuo1 in range(len(poblacion)-1):
        contador = 0
        for individuo2 in range(individuo1+1, len(poblacion)):
            if np.array_equal(poblacion[individuo1], poblacion[individuo2]):
                contador += 1
        if contador > mayor:
            mayor = contador
    return mayor/len(poblacion) < Pterminacion

# Funciones de excepción para manejar errores específicos en la entrada de datos.
# agregamos clases de excepción personalizadas para manejar errores comunes en la entrada de datos.

class EntradaInvalidaError(Exception):
    """Excepción base para entradas inválidas"""
    pass

class ValorNoEnteroError(EntradaInvalidaError):
    """Se lanza cuando se espera un entero pero se recibe otro tipo de dato"""
    def __init__(self, campo):
        super().__init__(f"El valor para {campo} debe ser un número entero")

class PorcentajeInvalidoError(EntradaInvalidaError):
    """Se lanza cuando un porcentaje está fuera del rango 0-100"""
    def __init__(self, campo):
        super().__init__(f"El porcentaje para {campo} debe estar entre 0 y 100")

class FormatoFuncionInvalidoError(EntradaInvalidaError):
    """Se lanza cuando el formato de la función no es válido"""
    def __init__(self):
        super().__init__("El formato de la función debe ser similar a '2x+3X' o '4z+5z'")

class OpcionInvalidaError(EntradaInvalidaError):
    """Se lanza cuando se ingresa una opción no válida (s/n)"""
    def __init__(self):
        super().__init__("La opción debe ser 's' o 'n'")

class TamañoPoblacionInvalidoError(EntradaInvalidaError):
    """Se lanza cuando el tamaño de población es menor a 1"""
    def __init__(self):
        super().__init__("El tamaño de la población debe ser al menos 1")

class RestriccionInvalidaError(EntradaInvalidaError):
    """Se lanza cuando la restricción no es un número válido"""
    def __init__(self):
        super().__init__("La restricción debe ser un número entero válido")

# Agregar esta nueva excepción al archivo existente
class OpcionOperadorInvalidaError(EntradaInvalidaError):
    """Se lanza cuando se ingresa una opción no válida para los operadores"""
    def __init__(self, operador, opciones_validas):
        super().__init__(f"Opción inválida para {operador}. Las opciones válidas son: {opciones_validas}")

# Funciones de validación para asegurar que los datos ingresados por el usuario sean correctos.
def validar_entero(valor, campo):
    """Valida que el valor sea un entero"""
    try:
        return int(valor)
    except ValueError:
        raise ValorNoEnteroError(campo)

def validar_porcentaje(valor, campo):
    """Valida que el valor sea un porcentaje entre 0 y 100"""
    valor = validar_entero(valor, campo)
    if valor < 0 or valor > 100:
        raise PorcentajeInvalidoError(campo)
    return valor / 100

def validar_tamano_poblacion(valor):
    """Valida el tamaño de la población"""
    valor = validar_entero(valor, "tamaño de población")
    if valor < 1:
        raise TamañoPoblacionInvalidoError()
    return valor

def validar_funcion(funcion_str):
    """Valida el formato básico de la función (implementación básica)"""
    # Esta es una validación sencilla, se puede expandir según requerimientos
    if not any(c in funcion_str for c in ['x', 'X', 'y', 'Y', 'z', 'Z']):
        raise FormatoFuncionInvalidoError()
    return funcion_str

def validar_opcion(opcion):
    """Valida que la opción sea s/n"""
    opcion = opcion.lower()
    if opcion not in ['s', 'n']:
        raise OpcionInvalidaError()
    return opcion

def validar_restriccion(valor):
    """Valida la restricción"""
    try:
        return int(valor)
    except ValueError:
        raise RestriccionInvalidaError()

# Función para validar la opción del operador (selección, cruce, mutación).
def validar_opcion_operador(valor, operador, opciones_validas):
    """Valida que la opción del operador sea válida"""
    try:
        valor_int = int(valor)
        if valor_int not in opciones_validas:
            raise OpcionOperadorInvalidaError(operador, opciones_validas)
        return valor_int
    except ValueError:
        raise OpcionOperadorInvalidaError(operador, opciones_validas)