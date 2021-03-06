import random
import copy
import numpy as np
import matplotlib.pyplot as plt
from schedueling import cargar_calendario

def sigma_dispersion(tabla):
    sigma = np.mean([(tabla[x].puntaje - tabla[x+1].puntaje) for x in range(1,len(tabla)-2)])
    #maxs = np.mean([((tabla[x].puntaje - tabla[x+1].puntaje)-mean)**2 for x in range(1,len(tabla)-2)])
    return sigma
    #return 1/ sum([(tabla[x].puntaje - tabla[x+1].puntaje)/maxs for x in range(1,len(tabla)-2)])
        

def potencialmente_interesante(a):
    interesantes = []
    for j in range(1, len(a)):
        if 1 < a[0].puntaje - a[j].puntaje <= 3:
            interesantes.append((a[j],"campeonato"))
            #print("El partido de {} es interesante porque si gana puede quedar primero".format(a[j].nombre))

        elif a[0].puntaje - a[j].puntaje == 1:
            interesantes.append((a[j],"campeonato"))
            #print("El partido de {} es interesante porque si empata o gana puede quedar primero".format(a[j].nombre))

        elif 1 < a[5].puntaje - a[j].puntaje <= 3:
            interesantes.append((a[j],"internacional"))
            #print("El partido de {} es interesante porque si gana puede quedar en zona de clasificacion a torneo internacional".format(a[j].nombre))

        elif a[5].puntaje - a[j].puntaje == 1:
            interesantes.append((a[j],"internacional"))
            #print("El partido de {} es interesante porque si empata o gana  puede quedar en zona de clasificacion a torneo internacional".format(a[j].nombre))

        elif 1 < a[13].puntaje - a[j].puntaje <= 3:
            interesantes.append((a[j],"descenso"))
            #print("El partido de {} es interesante porque si gana puede salir de posicion de descenso".format(a[j].nombre))

        elif a[13].puntaje - a[j].puntaje == 1:
            interesantes.append((a[j],"descenso"))
            #print("El partido de {} es interesante porque si empata o gana puede salir de posicion de descenso".format(a[j].nombre))
    return interesantes


class Simulacion:
    def __init__(self, calendario,equipos,montecarlo=False):
        self.calendario = calendario
        self.tabla = []
        self.equipos = copy.deepcopy(equipos)
        self.fecha = 0
        self._results = {}
        self.first_leg = True
        self.montecarlo = montecarlo
        self._pdraw = 0.26 #Dato historico de empates | analisis sensibilidad
        self._localwin = 0.4396 #Probabilidad de que un equipo local gane
        self.epsilon = 1 #Factor que le da mas chances de ganar a A
        self.plot = []
        self.suma_atractividad = 0
        self.atractividad_por_fecha ={}

    def guardar_fechas(self):
        with open('calendario.csv','w') as archivo:
            archivo.write('FECHA;LOCAL;VISITA;RESULTADO\n')
        for fecha in self.calendario:
            for partidos in fecha.partidos:
                with open('calendario.csv','a') as archivo:
                    archivo.write('{};{};{};{}\n'.format(fecha,*partidos.split(","),self._results[int(fecha.numero)][partidos]))
        with open('tabla_final.csv','w') as file:
            file.write('EQUIPO;PUNTAJE;VICTORIAS;EMPATES;DERROTAS\n')
        for x in self.equipos:
            with open('tabla_final.csv','a') as archivo:
                archivo.write('{};{};{};{};{}\n'.format(x.nombre,x.puntaje,len(x.victorias),len(x.empates),len(x.derrotas)))

                    
    def attr_funcion(self,tipo,num):
        data_dic = {"descenso":2/15,"internacional":1/15,"campeonato":0.2}
        if tipo in data_dic:
            if self.fecha > 15:
                return data_dic[tipo]*num
            else:
                return 0
    @property
    def atractividad(self):
        self.equipos.sort(key=lambda x: x.puntaje, reverse = True)
        interesantes = potencialmente_interesante(self.equipos)
        #n =sum(self.attr_funcion(x[1],self.fecha) for x in interesantes)
        a  = 0
        for x in interesantes:
            a += self.attr_funcion(x[1],self.fecha)
        return a
        
    def agregar_fechas(self,fechas):
        for x in fechas:
            self.calendario.append(x)
            
    def buscar_equipo(self,name):    
        for x in self.equipos:
            if x.nombre == name:
                return x
            
    def no_jugados(self,team):
        e_local = self.equipos[:]
        e_visita = self.equipos[:]
        for x in team.partidos_local:
            for y in e_local:
                if x.nombre == y.nombre or team.nombre == y.nombre:
                    e_local.remove(y)
        for x in team.partidos_visita:
                for y in e_visita:
                    if x.nombre == y.nombre or team.nombre == y.nombre:
                        e_visita.remove(y)
        return e_local, e_visita

    def add_victoria(self,a,b):
        a.victorias.append(b)
        b.derrotas.append(a)

    def p_empate(self):
        if self.first_leg:
            return self._pdraw
        n_empates_actuales = sum([len(x.empates) for x in self.equipos])/2
        n_partidos = len([keys for keys in self._results])*8
        return max(self._pdraw - 0.05 , min(self._pdraw + 0.05, 
            n_empates_actuales / n_partidos  ))

    def p_alpha (self,A):
        if self.first_leg:
            return 0.5
        n_partidos = len([keys for keys in self._results])
        #Tengo que arreglar aca ya que es el numero de partidos ganados como local
        #Esto se debe arreglar
        return max(0.5, len(A.victorias)/n_partidos)

    def p_betha (self,A,B):
        if self.first_leg:
            return 0.5
        return (A.rendimiento /(A.rendimiento + B.rendimiento))
    
    def p_delta(self,A,B):
        return  (A.presupuesto /(A.presupuesto + B.presupuesto))

    def p_gamma (self,A,B):
        return (A.ranking/(A.ranking + B.ranking))

    def p_local(self,A,B):
        if self.first_leg:
            factor = self.p_gamma(A,B)+ self.p_delta(A,B)
            p = factor / 2

        else:
            factor = 2*(self.p_alpha(A) + self.p_betha(A,B))
            factor += (self.p_gamma(A,B)+ self.p_delta(A,B))
            p = factor / 6

        return (1-self.p_empate())* p * self.epsilon


    def match_ending(self, victory, draw):
        x = random.uniform(0,1)
        if x <= victory:
            return "LW"
        elif x > victory and x < (draw + victory):
            return "D"
        else:
            return "AW" 

    def evento(self,local,visita):
        empate = self.p_empate()
        victoria_local = self.p_local(local,visita)
        r = self.match_ending(victoria_local,empate)
        
        if r == "LW":
            self.add_victoria(local,visita)
            return "LW"
        elif r == "AW":
            self.add_victoria(visita,local)
            return "AW"
        else:
            local.empates.append(visita)
            visita.empates.append(local)
            return "D"
    
    def publico(self,local,visita):
        return round(min(local.capacidad*1000
                   ,(local.espectadores + min(0.3*local.capacidad*1000
                                         ,visita.espectadores))))
           
           
    def results(self,match):
        local, away = match.split(",")
        
        eqlocal = [x for x in self.equipos if x.nombre == local.strip()]
        eqvis = [x for x in self.equipos if x.nombre == away.strip()]
        resultado = self.evento(*(eqlocal + eqvis))
        eqlocal[0].partidos_local.append(*eqvis)
        eqvis[0].partidos_visita.append(*eqlocal)
        return resultado
    
    def run(self):
        n = int(self.fecha)
        for fechas in self.calendario[n:]:
            self.fecha += 1
            if self.fecha == 16:
                self.first_leg = False
            self._results[fechas.numero]= {}
            for x in fechas.partidos:
                self._results[fechas.numero][x]=self.results(x)
            self.equipos.sort(key=lambda x: x.puntaje, reverse = True)
            self.suma_atractividad += int(self.atractividad)
            self.atractividad_por_fecha[str(self.fecha)] = self.suma_atractividad
            if not self.montecarlo:
                y = np.float(self.suma_atractividad)
                x = np.int(self.fecha)
                self.plot.append((x, y))
        #If simulation finishes then we plot a nice graph
        if self.fecha == 30 and not self.montecarlo:
            for elems in self.plot:
               plt.scatter(*elems,color = 'blue')
               plt.ylabel('Atrractividad acumulada')
               plt.title('Instancia')
            
            plt.show()
            for fecha in self.calendario:
                print ("\n")
                print (fecha)
                for partido in fecha.partidos:
                    print (partido)
            print ("\n")
            self.guardar_fechas()
                    
    def show_results(self):
        for x in self.equipos:
            print(x)
            #print x
        print("-"*50)
        #print "-"*50 
        #potencialmente_interesante(self.equipos)
        return self.equipos
    
def crear_simulacion(calendario,equipos):
    simulation = Simulacion(calendario,equipos)
    simulation.run()
    simulation.show_results()
    result_dict = {}
    for teams in simulation.equipos:
        result_dict[teams.nombre] = teams.puntaje
    return result_dict, simulation

def simulacion_unica(simulation):
    simulation.run()
    simulation.show_results()
    result_dict = {}
    for teams in simulation.equipos:
        result_dict[teams.nombre] = teams.puntaje
    return result_dict, simulation
    



