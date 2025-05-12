## CREADO NDD Sept 2019
# Miembros:
# Juan David Fajardo Betancourt
# Sebastian Giraldo Montoya

import random
import numpy as np


"""   Comentarios son Una Linea: #
O triple comilla doble: Un bloque"""

"""Si se desea una población inicial no aleatoria"""
cromosoma1 = [0, 1, 1, 0, 0, 0]  # Individuo 1 del Excel
cromosoma2 = [1, 0, 0, 0, 1, 1]  # Individuo 2 del Excel
cromosoma3 = [0, 0, 0, 1, 1, 0]  # Individuo 3 del Excel
cromosoma4 = [1, 0, 1, 1, 1, 0]  # Individuo 4 del Excel
cromosoma5 = [0, 1, 0, 0, 1, 1]  # Individuo 5 del Excel
cromosoma6 = [0, 1, 1, 1, 0, 0]  # Individuo 6 del Excel
poblInicial = np.array([cromosoma1, cromosoma2, cromosoma3, cromosoma4, cromosoma5, cromosoma6])

# MEJORA: Tamaño de la Población como parametro 
random.seed(1)  # Fijamos semilla para reproducibilidad
#print("\n","aletorio:", random.randrange(2)) #Entero 0 o 1

##### FUNCIONES PARA OPERADORES

def tablaMutaciones():
  mutaciones = []
  for x in range(n):
    mutaciones.append(np.random.rand())
  return mutaciones

def muta(mutacion, hijo):
  condicion = 5/100
  for x in range(n):
    if mutacion[x]<condicion:
      if hijo[x] == 0:
        hijo[x] = 1
      else:
        hijo[x] = 0

def evalua(n,x,poblIt,utilidad):
    suma=0
    total=0
    for i in range(0, n):
      for j in range(0,x):
        suma+=poblIt[i,j]*utilidad[j]
      fitness[i]=suma
      total+=suma
      suma=0
    return fitness,total

def imprime(n,total,fitness,poblIt):
    #Tabla de evaluación de la Población
    acumula=0
    print ("\n",'Tabla Iteración:',"\n")
    for i in range(0, n):
      probab=fitness[i]/total
      acumula+=probab
      print([i+1]," ",poblIt[i],"  ",fitness[i]," ","{0:.3f}".format(probab)," ","{0:.3f}".format(acumula))
      acumulado[i]=acumula
    print("Total Fitness:      ", total)
    return acumulado

def seleccion(acumulado):
    escoje=np.random.rand()
    print("escoje:      ", escoje)
    
    for i in range(0,n):
      if acumulado[i]>escoje:
        padre=poblIt[i]
        break
    return (padre)
    
    
def cruce(a1,p1,p2):
    if a1<Pcruce:
      print("Mas grande", Pcruce, "que ", a1, "-> Si Cruzan")
      puntoCorte = random.randint(1,5)
      print("El punto de corte es entre el gen ", puntoCorte-1, " y el gen ", puntoCorte)
      temp1=p1[0:puntoCorte] #[i:j] corta desde [i a j)
      temp2=p1[puntoCorte:6]
      print(temp1,temp2)
      temp3=p2[0:puntoCorte]
      temp4=p2[puntoCorte:6]
      print(temp3,temp4)
# Convert to list and then back to ndarray with dtype=int:
      hijo1 = np.array(temp1.tolist() + temp4.tolist(), dtype=int)
      hijo2 = np.array(temp3.tolist() + temp2.tolist(), dtype=int)
    else:
      print("Menor", Pcruce, "que ", a1, "-> NO Cruzan")
      hijo1=p1
      hijo2=p2

    return hijo1,hijo2
    
      
    
#### Parametros #####
x=6  #numero de variables de decision - 6 proyectos
n=6  #numero de individuos en la poblacion - 6 cromosomas
Pcruce=0.95  #Probabilidad de Cruce (95% como en Excel)
Pmuta=0.05   #Probabilidad de Mutación (5% como en Excel)


fitness= np.empty((n))
acumulado= np.empty((n))
suma=0
total=0

# Ingresar los datos del Problema de Energía - Costo y Utilidad de los Proyectos
utilidad = [409, 1718, 2000, 2008, 2075, 1800]  # Coeficientes de Z
pesos = [4130, 4210, 2400, 2420, 2020, 5200]    # Coeficientes de P
capacidad_max = 16000  # Restricción de presupuesto

print("Poblacion inicial (Del Excel):","\n", poblInicial)
print("\n","Utilidad:", utilidad) 
print("\n","Pesos", pesos)   
poblIt=poblInicial

######  FIN DE LOS DATOS INICIALES

## Función para verificar factibilidad (restricción de presupuesto)
def es_factible(cromosoma):
    peso_total = sum(cromosoma * pesos)
    return peso_total <= capacidad_max

## Modificación de la función evalua para incluir restricción
def evalua(n,x,poblIt,utilidad):
    fitness = np.zeros(n)
    total = 0
    for i in range(n):
        if es_factible(poblIt[i]):
            fitness[i] = sum(poblIt[i] * utilidad)
            total += fitness[i]
        else:
            fitness[i] = 0  # Penaliza soluciones inviables
    return fitness, total

##Llama función evalua, para calcular el fitness de cada individuo
fitness,total=evalua(n,x,poblIt,utilidad)
#####print("\n","Funcion Fitness por individuos",  fitness)
#####print("\n","Suma fitness: ",  total)

##### imprime la tabla de la iteracion
imprime(n,total,fitness,poblIt)

##### ***************************************
# Inicia Iteraciones

# Crear vector de 5x2 vacio  a = numpy.zeros(shape=(5,2))
for iter in range(5):  # 5 iteraciones como en el Excel
  print("\n","Iteración ", iter+1)
  
  for i in [0,2,4]:  ## Para el bloque de 2 hijos cada vez (3 parejas para 6 individuos)
    papa1=seleccion(acumulado) # Padre 1
    print("padre 1:", papa1)
    papa2=seleccion(acumulado) # Padre 2
    print("padre 2:", papa2)
    
    hijoA,hijoB=cruce(np.random.rand(),papa1,papa2)
    print("hijo1: ", hijoA)
    mutacionHijoA = tablaMutaciones()
    print("Mutacion del hijo1 ", mutacionHijoA)
    muta(mutacionHijoA, hijoA)
    print("hijo1 despues de la mutacion: ", hijoA)
    poblIt[i]=hijoA
    print("hijo2: ", hijoB)
    mutacionHijoB = tablaMutaciones()
    print("Mutacion del hijo2 ", mutacionHijoB)
    muta(mutacionHijoB, hijoB)
    print("hijo2 despues de la mutacion: ", hijoB, "\n")
    poblIt[i+1]=hijoB
    
  print("\n","Poblacion Iteración ", iter+1,"\n", poblIt)
  fitness,total=evalua(n,x,poblIt,utilidad)
  #### print("\n","Funcion Fitness por individuos",  fitness)
  #### print("\n","Suma fitness: ",  total)

  ##### imprime la tabla de la iteracion
  imprime(n,total,fitness,poblIt)