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
        print("Ingresa la cantidad de valores de decisión maxima para el fenotipo ", i, ":")
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
                return poblacionInicial
            else:
                print("El individuo no es factible según la restricción.")