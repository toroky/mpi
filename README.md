================================================================================
         RELATÓRIO DE AVALIAÇÃO DE PERFORMANCE — PARALELIZAÇÃO MPI
          Detecção de Similaridade entre Pares de Perguntas (MPI)
================================================================================
Data: 08/04/2026
================================================================================


================================================================================
1. DESCRIÇÃO DO PROBLEMA
================================================================================

Qual é o objetivo do programa?
--------------------------------
O programa implementa um sistema de detecção de similaridade semântica entre
pares de perguntas em linguagem natural. O objetivo é identificar, dentre um
conjunto de perguntas, aquelas que possuem significado equivalente ou próximo.

Qual o volume de dados processado?
------------------------------------
O conjunto de dados contém 5.000 perguntas, resultando em 12.497.500 pares
avaliados — equivalente à combinação C(5000, 2). Cada par é analisado
individualmente para o cálculo do índice de similaridade.

Qual algoritmo foi utilizado?
------------------------------
Similaridade do Cosseno (Cosine Similarity) sobre representações vetoriais
de texto (Bag-of-Words / TF). Para cada par (qi, qj):

    sim(qi, qj) = (qi · qj) / (||qi|| × ||qj||)

Qual a complexidade aproximada do algoritmo?
---------------------------------------------
O(n² × d), onde n = 5.000 perguntas e d = dimensão dos vetores.
Isso resulta em ~12,5 milhões de operações de produto interno, tornando a
paralelização essencial para execução em tempo hábil.

Resumo:
  - Número de perguntas      : 5.000
  - Total de pares avaliados : 12.497.500
  - Tempo serial medido      : 25,00 segundos
  - Objetivo da paralelização: distribuir os pares entre processos MPI


================================================================================
2. AMBIENTE EXPERIMENTAL
================================================================================

  Item                        | Descrição
  ----------------------------|-----------------------------------------
  Processador                 | Intel Core i7
  Número de núcleos           | 12 núcleos físicos
  Memória RAM                 | 16 GB DDR4
  Sistema Operacional         | Ubuntu 22.04 LTS
  Linguagem utilizada         | C
  Biblioteca de paralelização | MPI (Open MPI 4.x)
  Compilador / Versão         | mpicc / GCC 11.4


================================================================================
3. METODOLOGIA DE TESTES
================================================================================

Medição do tempo:
  O tempo foi medido com MPI_Wtime() pelo processo de rank 0, capturado antes
  do início do processamento e após a coleta de todos os resultados.

Configurações testadas:
  - 1  processo  (versão serial — baseline)
  - 2  processos MPI
  - 4  processos MPI
  - 8  processos MPI
  - 12 processos MPI

Procedimento experimental:
  - Execuções por configuração : 3 execuções independentes
  - Cálculo do tempo final     : média aritmética das 3 execuções
  - Entrada                    : fixa em todas as execuções (12.497.500 pares)
  - Condições                  : máquina com carga mínima do sistema

Distribuição da carga:
  Carga estática dividida em blocos iguais entre os processos. O rank 0
  distribui os pares via MPI_Scatter e coleta os resultados via MPI_Gather.


================================================================================
4. RESULTADOS EXPERIMENTAIS — TEMPOS MÉDIOS DE EXECUÇÃO
================================================================================

  Nº de Processos | Tempo de Execução (s)
  ----------------|----------------------
        1         |        25,00
        2         |        13,21
        4         |         7,04
        8         |         4,18
       12         |         3,37

  Nota: tempos obtidos com entrada fixa de 12.497.500 pares de perguntas.


================================================================================
5. CÁLCULO DE SPEEDUP E EFICIÊNCIA
================================================================================

Fórmulas utilizadas:

    Speedup(p)    = T(1) / T(p)
    Eficiência(p) = Speedup(p) / p

Onde:
    T(1) = tempo da execução serial
    T(p) = tempo com p processos
    p    = número de processos MPI


================================================================================
6. TABELA DE RESULTADOS
================================================================================

  Processos | Tempo (s) | Speedup | Speedup Ideal | Eficiência | Efic. Ideal
  ----------|-----------|---------|---------------|------------|------------
      1     |   25,00   |  1,0000 |     1,0000    |   1,0000   |   1,0000
      2     |   13,21   |  1,8925 |     2,0000    |   0,9462   |   1,0000
      4     |    7,04   |  3,5511 |     4,0000    |   0,8878   |   1,0000
      8     |    4,18   |  5,9809 |     8,0000    |   0,7476   |   1,0000
     12     |    3,37   |  7,4184 |    12,0000    |   0,6182   |   1,0000


================================================================================
7. GRÁFICO DE TEMPO DE EXECUÇÃO
================================================================================

  Eixo X: Número de processos | Eixo Y: Tempo de execução (segundos)

   25 |█████████████████████████████  25,00s
      |
   20 |
      |
   15 |
      |
   13 |█████████████  13,21s
      |
   10 |
      |
    7 |███████  7,04s
      |
    4 |████  4,18s
    3 |███  3,37s
      +--------------------------------------------------
         1p        2p        4p        8p       12p

  Observação: queda expressiva de 1→4 processos; ganho marginal a partir de 8.


================================================================================
8. GRÁFICO DE SPEEDUP
================================================================================

  Eixo X: Número de processos | Eixo Y: Speedup (obtido vs. ideal)

   12 |············································ ideal
      |
   10 |
      |
    8 |···················· ideal (8p)
      |
    7 |                                        ██  7,42 (12p obtido)
    6 |                          ██  5,98 (8p obtido)
      |
    4 |············ ideal (4p)
    4 |          ██  3,55 (4p obtido)
      |
    2 |····  ideal (2p)
    2 |  ██  1,89 (2p obtido)
    1 |█  1,00 (1p)
      +--------------------------------------------------
         1p        2p        4p        8p       12p

  (···) = speedup ideal (linear)   (██) = speedup obtido

  Observação: divergência crescente do ideal a partir de 4 processos.


================================================================================
9. GRÁFICO DE EFICIÊNCIA
================================================================================

  Eixo X: Número de processos | Eixo Y: Eficiência (0 a 1)

  1,00 |█  ████████████████████████████  (ideal = 1,00 para todos)
  0,95 |   █  0,946 (2p)
       |
  0,89 |         █  0,888 (4p)
       |
  0,75 |                  █  0,748 (8p)
       |
  0,62 |                           █  0,618 (12p)
       |
  0,00 +--------------------------------------------------
            1p       2p       4p       8p      12p

  Observação: eficiência aceitável até 8p; queda mais pronunciada em 12p.


================================================================================
10. ANÁLISE DOS RESULTADOS
================================================================================

O speedup obtido foi próximo do ideal?
----------------------------------------
Para 2 e 4 processos, o speedup foi próximo ao ideal: 1,89 de 2,00 e 3,55 de
4,00 esperados. A partir de 8 processos, a divergência se amplia (5,98 vs 8,00
ideal e 7,42 vs 12,00 ideal), reflexo do overhead de comunicação MPI e da
fração serial do código (Lei de Amdahl).

A aplicação apresentou escalabilidade?
----------------------------------------
Sim. A aplicação demonstrou boa escalabilidade até 4 processos (eficiência
> 88%). Entre 8 e 12 processos, a escalabilidade reduz, mas ainda há ganho
real de desempenho. Trata-se de escalabilidade do tipo Amdahl, limitada pela
fração serial do algoritmo.

Em qual ponto a eficiência começou a cair?
-------------------------------------------
A queda se inicia já em 2 processos (de 1,00 para 0,946), porém de forma
suave. A queda mais pronunciada ocorre ao passar de 4 para 8 processos
(de 0,888 para 0,748), e se acentua novamente de 8 para 12 processos
(de 0,748 para 0,618).

O número de processos ultrapassa o número de núcleos físicos?
--------------------------------------------------------------
Não. A máquina possui 12 núcleos físicos e o teste máximo utiliza exatamente
12 processos, o que é ideal — sem contenção de CPU ou troca de contexto
desnecessária. Os 12 processos podem ser mapeados 1:1 aos núcleos físicos.

Houve overhead de paralelização?
----------------------------------
Sim. Os principais overheads identificados foram:

  - Comunicação MPI   : MPI_Scatter e MPI_Gather introduzem latências
                        crescentes com o número de processos.
  - Sincronização     : a barreira de coleta aguarda o processo mais lento,
                        prejudicando o balanceamento.
  - Fração serial     : leitura dos dados, pré-processamento e impressão dos
                        resultados são feitos sequencialmente pelo rank 0.
  - Overhead de rede  : mesmo em memória compartilhada, a pilha MPI tem custo
                        de inicialização e envio de mensagens.

Possíveis gargalos:
  - Desbalanceamento de carga caso os vetores tenham tamanhos variados.
  - Coleta dos top-K resultados requer ordenação global, que é serial.
  - Banda de memória compartilhada disputada por todos os processos.


================================================================================
11. CONCLUSÃO
================================================================================

O experimento demonstrou que a paralelização com MPI trouxe ganhos reais e
significativos de desempenho. O tempo caiu de 25,00 s (serial) para 3,37 s
com 12 processos — redução de 86,5% no tempo total de execução.

O melhor custo-benefício entre speedup e eficiência foi obtido com 2 a 4
processos (eficiência > 88%, speedup próximo ao linear). Com 12 processos
a eficiência cai para 61,8%, mas o speedup absoluto de 7,42x ainda representa
ganho expressivo, especialmente considerando que não há ultrapassagem do
número de núcleos físicos da máquina.

O programa escala bem dentro do intervalo testado, com degradação progressiva
esperada para algoritmos com fração serial não desprezível.

Melhorias sugeridas:
  1. Balanceamento dinâmico de carga para equalizar o trabalho entre processos.
  2. Comunicação não bloqueante (MPI_Isend/MPI_Irecv) para sobrepor
     computação e comunicação, reduzindo tempo ocioso.
  3. Paralelismo híbrido MPI + OpenMP: processos MPI entre nós e threads
     OpenMP dentro de cada nó para melhor uso de memória compartilhada.
  4. MPI_Allreduce para coleta eficiente dos top-K pares similares.
  5. Vetorização SIMD das operações de produto interno para acelerar
     a computação local de cada processo.

================================================================================
                             FIM DO RELATÓRIO
================================================================================
