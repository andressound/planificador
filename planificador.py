import random
import os
from collections import deque

def generar_procesos(cantidad):
    prefijo = "procesos/proceso_"
    if not os.path.exists("procesos"):
        os.makedirs("procesos")
    for i in range(cantidad):
        nombre_archivo = prefijo + str(i) + ".txt"
        cant_instrucciones = random.randrange(10, 16)
        with open(nombre_archivo, 'w') as archivo:
            for _ in range(cant_instrucciones):
                archivo.write('EXEC\n' if random.randrange(4) else 'WAIT\n')
            archivo.write('EXEC')

def generar_bash(cantidad):
    procesos = os.listdir("procesos")
    with open("bash.txt", 'w') as archivo:
        for i in range(cantidad):
            indice = random.randrange(len(procesos))
            archivo.write(f"{procesos[indice]} {random.randrange(1, i+2)} {random.randrange(1, 4)}\n")

def leer_bash():
    with open("bash.txt", 'r') as archivo:
        return archivo.readlines()

def ajustar_formato(proceso):
    nombre, burst_time, prioridad = proceso.strip().split()
    return [nombre, int(burst_time), int(prioridad)]

def ordenar_procesos(procesos):
    return sorted(procesos, key=lambda x: (x[1], -x[2]))

def bash_procesos():
    bash = leer_bash()
    procesos = [ajustar_formato(proceso) for proceso in bash]
    return ordenar_procesos(procesos)

class Process:
    def __init__(self, name, burst_time, priority=0):
        self.name = name
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.waiting_time = 0
        self.turnaround_time = 0

class Scheduler:
    def __init__(self):
         self.processes = []
         self.total_time = 0
         self.context_switch_time = 2

    def add_process(self, process):
        self.processes.append(process)

    def calculate_metrics(self):
        avg_waiting_time = sum(p.waiting_time for p in self.processes) / len(self.processes)
        avg_turnaround_time = sum(p.turnaround_time for p in self.processes) / len(self.processes)
        avg_penalty = sum(p.turnaround_time / p.burst_time for p in self.processes) / len(self.processes)
        return avg_waiting_time, avg_turnaround_time, avg_penalty

    def print_results(self):
        print(f"\nResultados para {self.__class__.__name__}:")
        for p in self.processes:
            print(f"{p.name}: Tiempo de espera = {p.waiting_time}, Tiempo de respuesta = {p.turnaround_time}")
        avg_waiting, avg_turnaround, avg_penalty = self.calculate_metrics()
        print(f"Promedio - Tiempo de espera: {avg_waiting:.2f}, Tiempo de respuesta: {avg_turnaround:.2f}, Penalización: {avg_penalty:.2f}")
        print(f"Tiempo total de ejecución: {self.total_time}")

    def run(self):
        raise NotImplementedError("Cada planificador debe implementar su propio método run()")

class FIFOScheduler(Scheduler):
    def run(self):
        current_time = 0
        for process in self.processes:
            if current_time > 0:
                current_time += self.context_switch_time
            process.waiting_time = current_time
            current_time += process.burst_time
            process.turnaround_time = current_time
        self.total_time = current_time
        self.print_results()

class SJFScheduler(Scheduler):
    def run(self):
        sorted_processes = sorted(self.processes, key=lambda p: p.burst_time)
        current_time = 0
        for process in sorted_processes:
            if current_time > 0:
                current_time += self.context_switch_time
            process.waiting_time = current_time
            current_time += process.burst_time
            process.turnaround_time = current_time
        self.total_time = current_time
        self.print_results()

class PriorityScheduler(Scheduler):
    def run(self):
        sorted_processes = sorted(self.processes, key=lambda p: p.priority, reverse=True)
        current_time = 0
        for process in sorted_processes:
            if current_time > 0:
                current_time += self.context_switch_time
            process.waiting_time = current_time
            current_time += process.burst_time
            process.turnaround_time = current_time
        self.total_time = current_time
        self.print_results()

class RoundRobinScheduler(Scheduler):
    def __init__(self, quantum):
        super().__init__()
        self.quantum = quantum

    def run(self):
        queue = deque(self.processes)
        current_time = 0
        while queue:
            process = queue.popleft()
            if current_time > 0:
                current_time += self.context_switch_time
            execution_time = min(self.quantum, process.remaining_time)
            current_time += execution_time
            process.remaining_time -= execution_time
            
            for other_process in self.processes:
                if other_process != process and other_process.remaining_time > 0:
                    other_process.waiting_time += execution_time + self.context_switch_time
            
            if process.remaining_time > 0:
                queue.append(process)
            else:
                process.turnaround_time = current_time
        
        self.total_time = current_time
        self.print_results()

class SRTFScheduler(Scheduler):
    def run(self):
        remaining_processes = self.processes.copy()
        current_time = 0
        while remaining_processes:
            available_processes = [p for p in remaining_processes if p.remaining_time > 0]
            if not available_processes:
                break
            process = min(available_processes, key=lambda p: p.remaining_time)
            if current_time > 0:
                current_time += self.context_switch_time
            execution_time = min(process.remaining_time, 1)  # Ejecutar por 1 unidad de tiempo o menos
            current_time += execution_time
            process.remaining_time -= execution_time
            for p in remaining_processes:
                if p != process and p.remaining_time > 0:
                    p.waiting_time += execution_time + self.context_switch_time
            if process.remaining_time == 0:
                process.turnaround_time = current_time
                remaining_processes.remove(process)
        self.total_time = current_time
        self.print_results()

def main():
    # Generate processes and bash file
    generar_procesos(5)
    generar_bash(10)

    # Read and process the bash file
    processes = bash_procesos()

    schedulers = [
        FIFOScheduler(),
        SJFScheduler(),
        PriorityScheduler(),
        RoundRobinScheduler(quantum=1),
        SRTFScheduler()
    ]

    for scheduler in schedulers:
        for process in processes:
            scheduler.add_process(Process(process[0], process[1], process[2]))
        scheduler.run()

if __name__ == "__main__":
    main()