from schedueling import *
from montecarlo import simulacion_montecarlo
from min_var import min_var
from simulation import simulacion_unica
from equipos import EQUIPOS

def potencialmente_interesante(a):
    interesantes = 0
    for j in range(1, len(a)):
        if 1 < a[0].puntaje - a[j].puntaje <= 3:
            interesantes += 1
            print("El partido de {} es interesante porque si gana puede quedar primero".format(a[j].nombre))

        elif a[0].puntaje - a[j].puntaje == 1:
            interesantes += 1
            print("El partido de {} es interesante porque si empata o gana puede quedar primero".format(
                    a[j].nombre))

        elif 1 < a[5].puntaje - a[j].puntaje <= 3:
            interesantes += 1
            print(
                "El partido de {} es interesante porque si gana puede quedar en zona de clasificacion a torneo internacional".format(
                    a[j].nombre))

        elif a[5].puntaje - a[j].puntaje == 1:
            interesantes += 1
            print(
                "El partido de {} es interesante porque si empata o gana  puede quedar en zona de clasificacion a torneo internacional".format(
                    a[j].nombre))

        elif 1 < a[13].puntaje - a[j].puntaje <= 3:
            interesantes += 1
            print(
                "El partido de {} es interesante porque si gana puede salir de posicion de descenso".format(
                    a[j].nombre))

        elif a[13].puntaje - a[j].puntaje == 1:
            interesantes += 1
            print(
                "El partido de {} es interesante porque si empata o gana puede salir de posicion de descenso".format(
                    a[j].nombre))

def modelo():
    primeras_15_fechas = calendarizacion(15)
    #sim1 = simulacion_montecarlo(primeras_15_fechas, True)
    sim2, s = simulacion_unica(primeras_15_fechas,None,EQUIPOS,None)
    segundas_7_fechas = calendarizacion(7, primeras_15_fechas, sim2)
    s.agregar_fechas(segundas_7_fechas)
    simulacion_unica(primeras_15_fechas,None,EQUIPOS,s)
    terceras_5_fechas = min_var(5, primeras_15_fechas, sim2)


if __name__ == "__main__" :
    modelo()


