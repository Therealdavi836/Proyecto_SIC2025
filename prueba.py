from sympy import symbols, sympify, lambdify, sin, cos, sqrt
import re

def parse_funcion(funcion_str):
    x = symbols('x')
    funcion_str = funcion_str.replace('sen', 'sin')  # Normaliza para sympy
    funcion_str = funcion_str.replace('^', '**')     # Potencias en Python
    try:
        funcion = sympify(funcion_str)
        return funcion
    except Exception as e:
        print("Error al parsear la función:", e)
        return None

def funcion_evaluable(funcion_sympy):
    x = symbols('x')
    return lambdify(x, funcion_sympy, modules=['math'])  # Usa funciones como sin, cos, etc.

def resultado_funcion_general(individuo, fenotipo, funcion_eval):
    inicio = 0
    fin = fenotipo[0]
    resultado_total = 0
    for i in range(len(fenotipo)):
        fraccion = individuo[inicio:fin]
        valor_x = convertirBinarioADecimal(fraccion)
        resultado_total += funcion_eval(valor_x)
        inicio = fin
        if i + 1 < len(fenotipo):
            fin += fenotipo[i + 1]
    return resultado_total

def valoresMaxFenotipoBin(tamFuncion):
    valores = []
    for i in range(tamFuncion):
        valor = int(input(f"Ingrese el valor máximo para la variable de decisión {i}: "))
        valores.append(valor.bit_length())
    return valores

def convertirBinarioADecimal(fraccion):
    decimal = 0
    for i in range(len(fraccion)):
        decimal += fraccion[i] * (2 ** ((len(fraccion) - i))-1)
    return decimal

funcion_str = "3*x**2 + sin(x) + 2*x"
funcion_sym = parse_funcion(funcion_str)
print("Función simbólica:", funcion_sym)
f_eval = funcion_evaluable(funcion_sym)
print("Función evaluable:", f_eval)

# Suponiendo un individuo binario y fenotipo
individuo = [1, 0, 1, 1, 1, 0]  # ejemplo
fenotipo = [3, 3]               # 2 variables de 3 bits cada una

resultado = resultado_funcion_general(individuo, fenotipo, f_eval)
print("Resultado:", resultado)
