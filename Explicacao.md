# Explicação linha a linha do código

## Importações

```python
from collections import deque
import copy
```

Importa `deque` para filas eficientes (usado no Round Robin) e `copy` para criar cópias profundas dos objetos, evitando modificar os dados originais. Mais detalhadamente, essas importações tratam-se de:
* collections (para usar deque, que é uma estrutura de dados de fila eficiente, mas não um algoritmo de escalonamento).
* copy (para copiar objetos e evitar modificar os originais).

Essas bibliotecas são utilitários gerais do Python, não fazem escalonamento de processos.

---

## Definição da classe Processo

```python
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
        self.tempo_restante = int(duracao)
```

Define a estrutura de dados para representar um processo, com seus atributos principais. `tempo_restante` é inicializado com a duração total, usado para algoritmos preemptivos.

---

## Função para ler processos de arquivo

```python
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
```

Abre o arquivo, lê linha a linha, separa os campos, cria objetos `Processo` e retorna uma lista com todos os processos.

---

## Função para calcular tempos médios

```python
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
```

Recebe uma lista com dados de execução dos processos e calcula o tempo médio de espera e o tempo médio de turnaround (tempo total desde a chegada até o término).

---

## Função para exibir resultados

```python
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
```

Imprime a ordem em que os processos foram executados e as métricas calculadas.

---

## Algoritmo FCFS (First-Come, First-Served)

```python
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
```

Ordena os processos pela chegada e executa um por vez na ordem de chegada, atualizando o tempo atual e registrando os resultados.

---

## Algoritmo SJF (Shortest Job First) não preemptivo

```python
def escalonamento_sjf(processos):
    """
    Implementa o algoritmo Shortest Job First (não preemptivo).
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

        processo_escolhido = min(fila, key=lambda p: (p.duracao, p.chegada))
        fila.remove(processo_escolhido)

        tempo_atual = max(tempo_atual, processo_escolhido.chegada)
        tempo_termino = tempo_atual + processo_escolhido.duracao
        ordem_execucao.append(processo_escolhido.pid)
        resultados.append((processo_escolhido.pid, processo_escolhido.chegada, tempo_termino, processo_escolhido.duracao))
        tempo_atual = tempo_termino

    return ordem_execucao, calcular_tempos(resultados)
```

Executa o processo com menor duração disponível no momento, sem preempção. Atualiza o tempo atual e resultados.

---

## Algoritmo SRTF (Shortest Remaining Time First) preemptivo

```python
def escalonamento_srtf(processos):
    """
    Implementa o algoritmo Shortest Remaining Time First (preemptivo).
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

        processo_escolhido = min(fila, key=lambda p: p.tempo_restante)

        if processo_escolhido.pid not in resultados:
            resultados[processo_escolhido.pid] = [processo_escolhido.pid, processo_escolhido.chegada, None, processo_escolhido.duracao]

        processo_escolhido.tempo_restante -= 1
        tempo_atual += 1
        ordem_execucao.append(processo_escolhido.pid)

        if processo_escolhido.tempo_restante == 0:
            fila.remove(processo_escolhido)
            resultados[processo_escolhido.pid][2] = tempo_atual  # tempo de término absoluto

    return ordem_execucao, calcular_tempos([tuple(r) for r in resultados.values()])
```

Executa o processo com menor tempo restante, preemptivamente, um passo de tempo por vez, atualizando o tempo restante e removendo processos terminados.

---

## Algoritmo Round Robin (RR)

```python
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
```

Executa processos em fatias de tempo (quantum), alternando entre eles. Se o processo não termina, volta para o fim da fila.

---

## Algoritmo Prioridade Cooperativo (não preemptivo)

```python
def escalonamento_prioridade_coop(processos):
    """
    Implementa o algoritmo de Prioridade Cooperativo (não preemptivo).
    Args:
        processos: Lista de objetos Processo
    Returns:
        Tupla (ordem_execucao, tempos_medios)
    """
    return escalonamento_prioridade(processos)
```

Chama a função genérica de escalonamento por prioridade não preemptiva.

---

## Algoritmo Prioridade (não preemptivo)

```python
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

        fila_prioritaria = [p for p in fila if p.prioridade > 0]

        if fila_prioritaria:
            processo_escolhido = max(fila_prioritaria, key=lambda p: (p.prioridade, -p.chegada))
        else:
            processo_escolhido = min(fila, key=lambda p: p.chegada)

        fila.remove(processo_escolhido)

        tempo_atual = max(tempo_atual, processo_escolhido.chegada)
        tempo_termino = tempo_atual + processo_escolhido.duracao
        ordem_execucao.append(processo_escolhido.pid)
        resultados.append((processo_escolhido.pid, processo_escolhido.chegada, tempo_termino, processo_escolhido.duracao))
        tempo_atual = tempo_termino

    return ordem_execucao, calcular_tempos(resultados)
```

Executa processos com maior prioridade primeiro (maior número), desempata pelo tempo de chegada. Não preemptivo.

---

## Algoritmo Prioridade Preemptivo

```python
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
```

Semelhante ao SRTF, mas escolhe o processo com maior prioridade para executar a cada unidade de tempo, preemptivamente.

---

## Interface principal (main)

```python
if __name__ == '__main__':

    print("\n=== SISTEMA DE ESCALONAMENTO ELF ===")

    # Lê o arquivo
    nome_arquivo = input("Informe o nome do arquivo com os processos: ")
    processos = ler_processos(nome_arquivo)

    # Agrupa processos por tipo
    processos_tipo1 = [p for p in processos if p.tipo == 1]
    processos_tipo2 = [p for p in processos if p.tipo == 2]
    processos_tipo3 = [p for p in processos if p.tipo == 3]

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
        exec_srtf, tempos_srtf = escalonamento_srtf(processos_tipo2)
        exibir_resultados(exec_srtf, tempos_srtf)

        print("\nResultados Prioridade Cooperativo (PrioC):")
        exec_prioc, tempos_prioc = escalonamento_prioridade_coop(processos_tipo2)
        exibir_resultados(exec_prioc, tempos_prioc)

    # Processa tipo 3 (ambos) - RR e PrioP
    if processos_tipo3:
        print("\n=== Processos mistos (Tipo 3) ===")
        print(f"Quantidade de processos: {len(processos_tipo3)}")

        if quantum is None:
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
```

Executa o programa principal: lê o arquivo, separa os processos por tipo, executa os algoritmos correspondentes para cada tipo, pede o quantum se necessário, exibe os resultados e finaliza.
