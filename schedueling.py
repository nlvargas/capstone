from gurobipy import *
from equipos import equipos_santiago, equipos_biobio, equipos_valparaiso, \
    equipos_grandes
from equipos import nombres as equipos
import operator

class Partido:
    def __init__(self, local, visita):
        self.local = local
        self.visita = visita
   
        
class Fecha:
    def __init__(self, num, partidos):
        self.numero = num
        self.partidos = partidos
        self.resultados = None

    def __repr__(self):
        return str(self.numero)


def aux(jugados): #funcion sin importancia
    p_jugados = []
    for fecha in jugados:
        for partido in fecha.partidos:
            p_jugados.append([partido.split(",")[0], partido.split(",")[1][1:]])
    return p_jugados

def local_ult_2(jugados):
    equipos_1 = set(partido.split(",")[0] for partido in jugados[-2:][0].partidos) #penultima
    equipos_2 = set(partido.split(",")[0] for partido in jugados[-2:][1].partidos) #ultima
    return list(equipos_1.intersection(equipos_2))

def visita_ult_2(jugados):
    equipos_1 = set(partido.split(",")[1][1:] for partido in jugados[-2:][0].partidos)
    equipos_2 = set(partido.split(",")[1][1:] for partido in jugados[-2:][1].partidos)
    return list(equipos_1.intersection(equipos_2))

def local_solo_ult(jugados):
    equipos_1 = set(partido.split(",")[0] for partido in jugados[-2:][0].partidos)
    equipos_2 = set(partido.split(",")[0] for partido in jugados[-2:][1].partidos)
    return list(equipos_2.difference(equipos_1))

def visita_solo_ult(jugados):
    equipos_1 = set(partido.split(",")[1][1:] for partido in jugados[-2:][0].partidos)
    equipos_2 = set(partido.split(",")[1][1:] for partido in jugados[-2:][1].partidos)
    return list(equipos_2.difference(equipos_1))

def calendarizacion(n_fechas, jugados=None, tabla=None, invertir =None):
    fechas = [i for i in range(1, n_fechas + 1)]

    m = Model("Tournament")

    #1 si juega el equipo i de local contra j en la fecha k
    match = m.addVars(equipos, equipos, fechas, vtype=GRB.BINARY, name="match")

    #No jueguen contra si mismos
    m.addConstrs(match[i, i, k] == 0 for k in fechas for i in equipos)

    #No mas de 2 partidos consecutivos de local o visita
    m.addConstrs((quicksum(match[i, j, k + l] for j in equipos for l in [0, 1,
                 2]) <= 2 for i in equipos for k in fechas[:n_fechas - 2]))

    #No mas de 3 en Santiago
    m.addConstrs((quicksum(match[i, j, k] for i in equipos_santiago) <= 3 for j
                  in equipos for k in fechas))

    # No mas de 1 en Valparaiso
    m.addConstrs(
        (quicksum(match[i, j, k] for i in equipos_valparaiso) <= 1 for j in
         equipos for k in fechas))

    # No mas de 1 en BioBio
    m.addConstrs(
        (quicksum(match[i, j, k] for i in equipos_biobio) <= 1 for j in equipos
         for k in fechas))

    if jugados is None:
        # Todos jueguen con todos y solo una vez en cada fecha
        m.addConstrs(
            (quicksum(match[i, j, k] + match[j, i, k] for j in equipos)
             == 1 for i in equipos for k in fechas))

        m.addConstrs(
            quicksum(match[i, j, k] + match[j, i, k] for k in fechas)
            == 1 for i in equipos for j in equipos if i != j)
    else:
        m.addConstrs(
            quicksum(match[i, j, k] for i, j in aux(jugados)) == 0 for k in
            fechas)

        m.addConstrs(quicksum(match[i, j, k] + match[j, i, k] for j in equipos)
                     == 1 for i in equipos for k in fechas)

        m.addConstrs(quicksum(match[i, j, k] for k in fechas)
                     <= 1 for i in equipos for j in equipos if i != j)
        print(jugados)
        if len(local_ult_2(jugados)) != 0:
            print ("local_ult_2: ", local_ult_2(jugados))
            m.addConstrs(quicksum(match[i, j, 1] for j in equipos) == 0
                         for i in local_ult_2(jugados))

        if len(visita_ult_2(jugados)) != 0:
            print ("visita_ult_2: ", visita_ult_2(jugados))
            m.addConstrs(quicksum(match[i, j, 1] for i in equipos) == 0
                         for j in visita_ult_2(jugados))

        if len(local_solo_ult(jugados)) != 0:
            print ("local_solo_ult: ", local_solo_ult(jugados))
            m.addConstrs(quicksum(match[i, j, 1] + match[i, j, 2] for j in
                         equipos) <= 1 for i in local_solo_ult(jugados))

        if len(visita_solo_ult(jugados)) != 0:
            print ("visita_solo_ult: ", visita_solo_ult(jugados))
            m.addConstrs(quicksum(match[i, j, 1] + match[i, j, 2] for i in
                         equipos) <= 1 for j in visita_solo_ult(jugados))


    if tabla is not None:
        print(tabla)
        # No pueden jugarse los clasicos
        #m.addConstrs((quicksum(match[i, j, k] for i in equipos_grandes for j in
                      #equipos_grandes) == 0 for k in fechas))
        # No jueguen contra equipos del mismo cluster
        m.addConstrs(match[i, j, k] == 0 for k in fechas for
                     i in [x for x in tabla][:7] for j in [x for x in tabla][:7]
                     if i != j)

        m.addConstrs(match[i, j, k] == 0 for k in fechas for
                     i in [x for x in tabla][9:] for j in [x for x in tabla][9:] if i != j)


    m.setObjective(quicksum(match[i, j, k] for i in equipos for j in equipos for
                   k in fechas), GRB.MINIMIZE)

    m.optimize()

    CALENDARIO = []
    CALENDARIO_INV = []#Calendario inicial factible
    # Print solution
    if m.status == GRB.Status.OPTIMAL:
        solution = m.getAttr('x', match)
        for k in fechas:
            print ("\n", "Fecha", k)
            #print "Fecha", k
            f = []
            for i in equipos:
                for j in equipos:
                    if solution[i, j, k] > 0:
                        f.append("{}, {}".format(i, j))
                        print (i, "-", j)
                        #print i, "-", j
            fecha = Fecha(k,f)
            CALENDARIO.append(fecha)
        if invertir is not None:    
            for k in fechas:
                print ("\n", "Fecha", k+15)
                #print "Fecha", k
                f = []
                for i in equipos:
                    for j in equipos:
                        if solution[i, j, k] > 0:
                                f.append("{}, {}".format(j, i))
                                print (j, "-", i)
                            #print i, "-", j
                fecha = Fecha(k+15,f)
                CALENDARIO_INV.append(fecha)
            return CALENDARIO, CALENDARIO_INV
    return CALENDARIO



