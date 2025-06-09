from funciones import *

#Parametros
Pcruce = int(input("Ingrese el numero de cruces: " )) / 100
Pmutacion = int(input("Ingrese el porcentaje de mutacion: ")) / 100
tamPoblacion = int(input("Ingrese el tamaño de la población: "))
funconGlobal = funcionesAVectores(input("Ingrese la función global: "))
funconFitnness = funcionesAVectores(input("Ingrese la función fitness: "))
restriccion = int(input("Ingrese la restricción: "))
poblacionInicial = generarPoblacionInicial(funconFitnness, restriccion, tamPoblacion, funconGlobal)