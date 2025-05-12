# Simulador de escalonamento para o sistema operacional ELF
# Algoritmos: FCFS, SFJ, SRTF, RR, Prioridade Cooperativo e Prioridade Preemptivo
# Autor: Ana Júlia Pereira Corrêa
# Cada linha do arquivo deve conter: PID chegada duração prioridade tipo
# Tipo: CPU bound = 1 | I/O bound = 2 | Ambos = 3
# CPU Bound (1) = FCFS e SJF
# I/O Bound (2) = SRTF e Prioc
# Ambos (3) = PrioP e RR
# Observação: Maior número  = maior prioridade, e se der empate, ordem de ingresso (tempo de ingresso) é que conta

from collections import deque
import copy

class Processo:

    """
    Classe que representa um processo no sistema.

    Atributos:
        pid: Identificador único do processo
        chegada: Tempo de chegada na fila de prontos
        duracao: Tempo total necessário para execução
        prioridade: Nível de prioridade do processo
        tipo: Tipo do processo (1=CPU-bound, 2=I/O-bound, 3=ambos)
        tempo_restante: Tempo ainda necessário para completar a execução
    """

    def __init__(self, pid, chegada, duracao, prioridade, tipo):
        self.pid = pid
        self.chegada = int(chegada)
        self.duracao = int(duracao)
        self.prioridade = int(prioridade)
        self.tipo = int(tipo)

def ler_processos(nome_arquivo):

    """
    Lê processos de um arquivo texto.

    Args:
        nome_arquivo: Nome do arquivo contendo os processos

    Returns:
        Lista de objetos Processo

    Formato do arquivo:
    PID chegada duracao prioridade tipo
    """

    processos = []
    with open(nome_arquivo, 'r') as arquivo:
        for linha in arquivo:
            partes = linha.strip().split()
            if len(partes) == 5:
                processos.append(Processo(*partes))
    return processos

def calcular_tempos(resultados):

    """
    Calcula tempos médios de espera e turnaround.

    Args:
        resultados: Lista de tuplas (pid, chegada, termino, duracao)

    Returns:
        Tupla (tempo_médio_espera, tempo_médio_turnaround)
    """

    tempos_espera = []
    tempos_turnaround = []
    for pid, chegada, termino, duracao in resultados:
        turnaround = termino - chegada
        espera = turnaround - duracao
        tempos_espera.append(espera)
        tempos_turnaround.append(turnaround)
    return (sum(tempos_espera) / len(tempos_espera),
            sum(tempos_turnaround) / len(tempos_turnaround))

def exibir_resultados(ordem_execucao, tempos):

    """
    Exibe os resultados do escalonamento.

    Args:
        ordem_execucao: Lista com a ordem de execução dos PIDs
        tempos: Tupla (tempo_médio_espera, tempo_médio_turnaround)
    """

    print("\nOrdem de Execução (PID):")
    for pid in ordem_execucao:
        print(pid, end=' ')
    print("\n\nMétricas:")
    print(f"Tempo médio de espera: {tempos[0]:.2f}")
    print(f"Tempo médio de turnaround: {tempos[1]:.2f}")

def escalonamento_fcfs(processos):

    """
    Implementa o algoritmo First-Come, First-Served.

    Args:
        processos: Lista de objetos Processo

    Returns:
        Tupla (ordem_execucao, tempos_medios)
    """

    processos = copy.deepcopy(processos)  # Cria cópia para não modificar original
    fila = sorted(processos, key=lambda p: p.chegada)
    tempo_atual = 0
    ordem_execucao = []
    resultados = []

    for p in fila:
        tempo_atual = max(tempo_atual, p.chegada)
        tempo_termino = tempo_atual + p.duracao
        ordem_execucao.append(p.pid)
        resultados.append((p.pid, p.chegada, tempo_termino, p.duracao))
        tempo_atual = tempo_termino

    return ordem_execucao, calcular_tempos(resultados)

def escalonamento_sjf(processos):

    """
    Implementa o algoritmo Shortest Job First (não preemptivo).

    Args:
        processos: Lista de objetos Processo

    Returns:
        Tupla (ordem_execucao, tempos_medios)
    """

    processos = copy.deepcopy(processos)  # Cria cópia para não modificar original
    tempo_atual = 0
    ordem_execucao = []
    resultados = []
    processos_restantes = sorted(processos, key=lambda p: p.chegada)
    fila = []

    while processos_restantes or fila:
        while processos_restantes and processos_restantes[0].chegada <= tempo_atual:
            fila.append(processos_restantes.pop(0))

        if not fila:
            tempo_atual = processos_restantes[0].chegada
            continue

        processo_escolhido = min(fila, key=lambda p: (p.duracao, p.chegada))
        fila.remove(processo_escolhido)

        tempo_atual = max(tempo_atual, processo_escolhido.chegada)
        tempo_termino = tempo_atual + processo_escolhido.duracao
        ordem_execucao.append(processo_escolhido.pid)
        resultados.append((processo_escolhido.pid, processo_escolhido.chegada, tempo_termino, processo_escolhido.duracao))
        tempo_atual = tempo_termino

    return ordem_execucao, calcular_tempos(resultados)

def escalonamento_srtf(processos, quantum):

    """
    Implementa o algoritmo Shortest Remaining Time First (preemptivo) com quantum.
    Args:
        processos: Lista de objetos Processo
        quantum: Fatia de tempo para execução
    Returns:
        Tupla (ordem_execucao, tempos_medios)
    """
    
    processos = copy.deepcopy(processos)
    tempo_atual = 0
    ordem_execucao = []
    resultados = {}
    processos_restantes = sorted(processos, key=lambda p: p.chegada)
    fila = []

    for p in processos:
        p.tempo_restante = p.duracao

    while processos_restantes or fila:
        while processos_restantes and processos_restantes[0].chegada <= tempo_atual:
            fila.append(processos_restantes.pop(0))

        if not fila:
            tempo_atual = processos_restantes[0].chegada
            continue

        processo_escolhido = min(fila, key=lambda p: p.tempo_restante)

        if processo_escolhido.pid not in resultados:
            resultados[processo_escolhido.pid] = [processo_escolhido.pid, processo_escolhido.chegada, None, processo_escolhido.duracao]

        execucao = min(processo_escolhido.tempo_restante, quantum)
        processo_escolhido.tempo_restante -= execucao
        tempo_atual += execucao
        ordem_execucao.extend([processo_escolhido.pid] * execucao)

        # Adiciona processos que chegaram durante a execução
        while processos_restantes and processos_restantes[0].chegada <= tempo_atual:
            fila.append(processos_restantes.pop(0))

        if processo_escolhido.tempo_restante == 0:
            fila.remove(processo_escolhido)
            resultados[processo_escolhido.pid][2] = tempo_atual  # tempo de término absoluto

    return ordem_execucao, calcular_tempos([tuple(r) for r in resultados.values()])

def escalonamento_rr(processos, quantum):

    """
    Implementa o algoritmo Round Robin.

    Args:
        processos: Lista de objetos Processo
        quantum: Fatia de tempo para cada processo

    Returns:
        Tupla (ordem_execucao, tempos_medios)
    """

    processos = copy.deepcopy(processos)
    tempo_atual = 0
    fila = deque()
    processos_restantes = sorted(processos, key=lambda p: p.chegada)
    ordem_execucao = []
    resultados = {}

    for p in processos:
        p.tempo_restante = p.duracao

    while processos_restantes or fila:
        while processos_restantes and processos_restantes[0].chegada <= tempo_atual:
            fila.append(processos_restantes.pop(0))

        if fila:
            p = fila.popleft()
            execucao = min(p.tempo_restante, quantum)
            tempo_atual = max(tempo_atual, p.chegada)
            tempo_atual += execucao
            p.tempo_restante -= execucao
            ordem_execucao.append(p.pid)

            # Adiciona processos que chegaram durante a execução
            while processos_restantes and processos_restantes[0].chegada <= tempo_atual:
                fila.append(processos_restantes.pop(0))

            if p.tempo_restante > 0:
                fila.append(p)
            else:
                tempo_termino = tempo_atual
                resultados[p.pid] = (p.pid, p.chegada, tempo_termino, p.duracao)
        else:
            if processos_restantes:
                tempo_atual = processos_restantes[0].chegada
            else:
                break

    return ordem_execucao, calcular_tempos(resultados.values())

def escalonamento_prioridade_coop(processos):

    """
    Implementa o algoritmo de Prioridade Cooperativo (não preemptivo).

    Args:
        processos: Lista de objetos Processo

    Returns:
        Tupla (ordem_execucao, tempos_medios)
    """

    return escalonamento_prioridade(processos)

def escalonamento_prioridade(processos):

    """
    Implementa o algoritmo de Prioridade (não preemptivo).

    Args:
        processos: Lista de objetos Processo

    Returns:
        Tupla (ordem_execucao, tempos_medios)
    """

    processos = copy.deepcopy(processos)
    tempo_atual = 0
    ordem_execucao = []
    resultados = []
    processos_restantes = sorted(processos, key=lambda p: p.chegada)
    fila = []

    while processos_restantes or fila:
        while processos_restantes and processos_restantes[0].chegada <= tempo_atual:
            fila.append(processos_restantes.pop(0))

        if not fila:
            tempo_atual = processos_restantes[0].chegada
            continue

        # Prioridade 0 = sem prioridade (mínima)
        # Filtra processos com prioridade > 0
        fila_prioritaria = [p for p in fila if p.prioridade > 0]

        if fila_prioritaria:
            # Escolhe o processo com maior prioridade (maior valor), desempata pelo tempo de chegada menor
            processo_escolhido = max(fila_prioritaria, key=lambda p: (p.prioridade, -p.chegada))
        else:
            # Se todos têm prioridade 0, escolhe o que chegou primeiro
            processo_escolhido = min(fila, key=lambda p: p.chegada)

        fila.remove(processo_escolhido)

        tempo_atual = max(tempo_atual, processo_escolhido.chegada)
        tempo_termino = tempo_atual + processo_escolhido.duracao
        ordem_execucao.append(processo_escolhido.pid)
        resultados.append((processo_escolhido.pid, processo_escolhido.chegada, tempo_termino, processo_escolhido.duracao))
        tempo_atual = tempo_termino

    return ordem_execucao, calcular_tempos(resultados)

def escalonamento_prioridade_preemp(processos):

    """
    Implementa o algoritmo de Prioridade Preemptivo.

    Args:
        processos: Lista de objetos Processo

    Returns:
        Tupla (ordem_execucao, tempos_medios)
    """

    processos = copy.deepcopy(processos)
    tempo_atual = 0
    ordem_execucao = []
    resultados = {}
    processos_restantes = sorted(processos, key=lambda p: p.chegada)
    fila = []

    for p in processos:
        p.tempo_restante = p.duracao

    while processos_restantes or fila:
        while processos_restantes and processos_restantes[0].chegada <= tempo_atual:
            fila.append(processos_restantes.pop(0))

        if not fila:
            tempo_atual = processos_restantes[0].chegada
            continue

        # Prioridade 0 = sem prioridade (mínima)
        fila_prioritaria = [p for p in fila if p.prioridade > 0]

        if fila_prioritaria:
            processo_escolhido = max(fila_prioritaria, key=lambda p: (p.prioridade, -p.chegada))
        else:
            processo_escolhido = min(fila, key=lambda p: p.chegada)

        if processo_escolhido.pid not in resultados:
            resultados[processo_escolhido.pid] = [processo_escolhido.pid, processo_escolhido.chegada, None, processo_escolhido.duracao]

        processo_escolhido.tempo_restante -= 1
        tempo_atual += 1
        ordem_execucao.append(processo_escolhido.pid)

        if processo_escolhido.tempo_restante == 0:
            fila.remove(processo_escolhido)
            resultados[processo_escolhido.pid][2] = tempo_atual  # tempo de término absoluto

    return ordem_execucao, calcular_tempos([tuple(r) for r in resultados.values()])

# Interface principal
if __name__ == '__main__':
    
    print("\n=== SISTEMA DE ESCALONAMENTO ELF ===")

    # Lê o arquivo
    nome_arquivo = input("Informe o nome do arquivo com os processos: ")
    processos = ler_processos(nome_arquivo)

    # Agrupa processos por tipo
    processos_tipo1 = [p for p in processos if p.tipo == 1]
    processos_tipo2 = [p for p in processos if p.tipo == 2]
    processos_tipo3 = [p for p in processos if p.tipo == 3]

    # Variável para armazenar o quantum quando necessário
    quantum = None

    print("\nExecutando escalonamento para cada tipo de processo encontrado:")

    # Processa tipo 1 (CPU-bound) - FCFS e SJF
    if processos_tipo1:
        print("\n=== Processos CPU-bound (Tipo 1) ===")
        print(f"Quantidade de processos: {len(processos_tipo1)}")

        print("\nResultados First-Come, First-Served (FCFS):")
        exec_fcfs, tempos_fcfs = escalonamento_fcfs(processos_tipo1)
        exibir_resultados(exec_fcfs, tempos_fcfs)

        print("\nResultados Shortest Job First (SJF):")
        exec_sjf, tempos_sjf = escalonamento_sjf(processos_tipo1)
        exibir_resultados(exec_sjf, tempos_sjf)

    # Processa tipo 2 (I/O-bound) - SRTF e PrioC
    if processos_tipo2:
        print("\n=== Processos I/O-bound (Tipo 2) ===")
        print(f"Quantidade de processos: {len(processos_tipo2)}")

        if quantum is None:
            quantum = int(input("Informe o quantum para os algoritmos que necessitam: "))

        print("\nResultados Shortest Remaining Time First (SRTF):")
        exec_srtf, tempos_srtf = escalonamento_srtf(processos_tipo2, quantum)
        exibir_resultados(exec_srtf, tempos_srtf)

        print("\nResultados Prioridade Cooperativo (PrioC):")
        exec_prioc, tempos_prioc = escalonamento_prioridade_coop(processos_tipo2)
        exibir_resultados(exec_prioc, tempos_prioc)

    # Processa tipo 3 (ambos) - RR e PrioP
    if processos_tipo3:
        print("\n=== Processos mistos (Tipo 3) ===")
        print(f"Quantidade de processos: {len(processos_tipo3)}")

        if quantum is None:  # Só pede o quantum uma vez se ainda não foi pedido
            quantum = int(input("Informe o quantum para os algoritmos que necessitam: "))

        print("\nResultados Round Robin (RR):")
        exec_rr, tempos_rr = escalonamento_rr(processos_tipo3, quantum)
        exibir_resultados(exec_rr, tempos_rr)

        print("\nResultados Prioridade Preemptivo (PrioP):")
        exec_priop, tempos_priop = escalonamento_prioridade_preemp(processos_tipo3)
        exibir_resultados(exec_priop, tempos_priop)

    if not (processos_tipo1 or processos_tipo2 or processos_tipo3):
        print("\nNenhum processo encontrado no arquivo ou tipos inválidos!")
        exit(1)

    print("\nEscalonamento finalizado!")
