
import pandas as pd
import re
import time
from mpi4py import MPI


def limpar_texto(texto):
    texto = str(texto).lower()
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tokenizar(texto):
    if not texto:
        return []
    return texto.split()


def similaridade_jaccard(tokens1, tokens2):
    set1 = set(tokens1)
    set2 = set(tokens2)

    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0

    intersecao = len(set1.intersection(set2))
    uniao = len(set1.union(set2))
    return intersecao / uniao


def carregar_csv_resiliente(arquivo):
    try:
        return pd.read_csv(arquivo, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(arquivo, encoding="latin1")


def preparar_perguntas(df, coluna, limite):
    perguntas = []

    for idx, texto in df[coluna].dropna().head(limite).items():
        texto_limpo = limpar_texto(texto)
        tokens = tokenizar(texto_limpo)

        if tokens:
            perguntas.append({
                "linha_original": int(idx),
                "texto_original": str(texto),
                "tokens": tokens
            })

    return perguntas


def calcular_faixa_i(n, rank, size):
    """
    Divide os índices i do laço externo entre os processos.
    Cada processo calcula os pares (i, j) com j > i.
    """
    total_i = max(0, n - 1)
    base = total_i // size
    resto = total_i % size

    inicio = rank * base + min(rank, resto)
    fim = inicio + base + (1 if rank < resto else 0)

    return inicio, fim


def processar_pares_localmente(perguntas, inicio_i, fim_i):
    resultados_locais = []
    n = len(perguntas)

    for i in range(inicio_i, fim_i):
        tokens_i = perguntas[i]["tokens"]

        for j in range(i + 1, n):
            sim = similaridade_jaccard(tokens_i, perguntas[j]["tokens"])

            resultados_locais.append({
                "indice_lista_1": i,
                "indice_lista_2": j,
                "linha_1": perguntas[i]["linha_original"],
                "linha_2": perguntas[j]["linha_original"],
                "pergunta_1": perguntas[i]["texto_original"],
                "pergunta_2": perguntas[j]["texto_original"],
                "similaridade": sim
            })

    return resultados_locais


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    arquivo = "nlp_features_train.csv"
    coluna = "question1"
    limite = 10000
    top_k = 20

    if rank == 0:
        print(f"Executando com {size} processo(s) MPI")
        print("Carregando dataset...")

        df = carregar_csv_resiliente(arquivo)

        if coluna not in df.columns:
            raise ValueError(
                f"A coluna '{coluna}' não existe no arquivo. "
                f"Colunas encontradas: {list(df.columns)}"
            )

        print("Preparando perguntas...")
        perguntas = preparar_perguntas(df, coluna, limite)
        n = len(perguntas)

        total_comparacoes = n * (n - 1) // 2
        print(f"Total de perguntas usadas: {n}")
        print(f"Total de comparações previstas: {total_comparacoes}")

        tempo_inicio = time.time()
    else:
        perguntas = None
        n = None
        tempo_inicio = None

    perguntas = comm.bcast(perguntas, root=0)
    n = comm.bcast(len(perguntas) if rank == 0 else None, root=0)

    inicio_i, fim_i = calcular_faixa_i(n, rank, size)

    print(
        f"[Processo {rank}] responsável pelos índices i de "
        f"{inicio_i} até {fim_i - 1}"
    )

    resultados_locais = processar_pares_localmente(perguntas, inicio_i, fim_i)

    qtd_local = len(resultados_locais)
    print(f"[Processo {rank}] comparações realizadas: {qtd_local}")

    todos_resultados = comm.gather(resultados_locais, root=0)

    if rank == 0:
        resultados = []
        for bloco in todos_resultados:
            resultados.extend(bloco)

        tempo_fim = time.time()

        resultados_ordenados = sorted(
            resultados,
            key=lambda x: x["similaridade"],
            reverse=True
        )

        print("\n=== RESULTADO FINAL ===")
        print(f"Tempo total MPI: {tempo_fim - tempo_inicio:.2f} segundos")
        print(f"Total de pares avaliados: {len(resultados)}")

        print(f"\nTop {top_k} pares mais similares:\n")
        for pos, item in enumerate(resultados_ordenados[:top_k], start=1):
            print(f"Par #{pos}")
            print(f"Similaridade: {item['similaridade']:.4f}")
            print(f"Linha pergunta 1: {item['linha_1']}")
            print(f"Linha pergunta 2: {item['linha_2']}")
            print(f"Pergunta 1: {item['pergunta_1']}")
            print(f"Pergunta 2: {item['pergunta_2']}")
            print("-" * 100)


if __name__ == "__main__":
    main()
