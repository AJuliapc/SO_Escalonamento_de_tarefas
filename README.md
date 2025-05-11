# 1º Trabalho de Sistemas Operacionais - Escalonamento de Tarefas

Aluno (a): Ana Júlia Pereira Corrêa
____
O sistema operacional ELF possui implementado em seu núcleo seis (6) algoritmos de escalonamento de processo (FCFS, RR, SJF, SRTF preemptivo, Prioc e Priop). Desta forma, implemente um (mas podem ser seis) programa(s) (código(s)) – COM BASE NOS ALGORITMOS DISPONIBILIZADOS - que ao receber como entrada uma sequência de processos contendo PID, tempo de ingresso na fila de prontos, duração, prioridade e tipo (CPU bound, I/O bound ou ambos) os coloque em execução da melhor forma possível. Seu código precisa definir no início quais algoritmos poderão ser usados (no mínimo dois) e o quantum. Como saída, seu código deve informar a ordem de execução dos processos (PID) de acordo com o algoritmo escolhido com base do tipo do processo. Também deve ser fornecido o tempo médio de execução e de espera.

IMPORTANTE:

* Sugestão: utilizar a linguagem C, java ou python.
* Prioridade 0 (zero) significa sem prioridade
* Quanto maior o valor, maior a prioridade
* Tipo de processo: CPU bound = 1; I/O bound = 2; ambos = 3; 
* CPU Bound (1) = FCFS e SJF
* I/O Bound (2) = SRTF e Prioc
* Ambos (3) = PrioP e RR
* Comentar o código fonte;
_____

# Código desenvolvido

* A linguagem escolhida para o desenvolvimento do Escalanador de Tarefas foi **Python**. 
* Os arquivos usados para teste estão em anexo e são: `FCFS_SJF_6.txt, Prio-6.txt, RR-6.txt e STRF.txt.`  

# Compilação e saídas

Para compilar, basta entrar com o seguinte caminho no terminal:

```python 
python escalanador.py
```

Que então irá pedir para digitar o caminho `.txt` do arquivo que você quer verificar o escalonamento:

```python
=== SISTEMA DE ESCALONAMENTO ELF ===
Informe o nome do arquivo com os processos: <nome_do_arquivo.txt>
```

Testando com o arquivos de teste anexados, por exemplo, temos as seguintes saídas:

```python 
python escalanador.py
```

```python
=== SISTEMA DE ESCALONAMENTO ELF ===
Informe o nome do arquivo com os processos: FCFS_SJF_6.txt

Executando escalonamento para cada tipo de processo encontrado:

=== Processos CPU-bound (Tipo 1) ===
Quantidade de processos: 6

Resultados First-Come, First-Served (FCFS):

Ordem de Execução (PID):
P1 P2 P3 P4 P5 P6 

Métricas:
Tempo médio de espera: 5.50
Tempo médio de turnaround: 9.00

Resultados Shortest Job First (SJF):

Ordem de Execução (PID):
P1 P2 P3 P4 P5 P6 

Métricas:
Tempo médio de espera: 5.50
Tempo médio de turnaround: 9.00

Escalonamento finalizado!
```

