import pandas as pd
import re
import time
from itertools import combinations


def limpar_texto(texto):
    """
    Normaliza o texto:
    - converte para minúsculas
    - remove caracteres especiais
    - remove espaços extras
    """
    texto = str(texto).lower()
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tokenizar(texto):
    """
    Divide o texto em palavras.
    """
    if not texto:
        return []
    return texto.split()


def similaridade_jaccard(tokens1, tokens2):
    """
    Calcula a similaridade de Jaccard entre dois conjuntos de tokens.
    """
    set1 = set(tokens1)
    set2 = set(tokens2)

    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0

    intersecao = len(set1.intersection(set2))
    uniao = len(set1.union(set2))

    return intersecao / uniao


def preparar_perguntas(df, coluna, limite):
    perguntas = []

    for idx, texto in df[coluna].dropna().head(limite).items():
        texto_limpo = limpar_texto(texto)
        tokens = tokenizar(texto_limpo)

        if len(tokens) > 0:
            perguntas.append({
                "linha_original": idx,
                "texto_original": texto,
                "texto_limpo": texto_limpo,
                "tokens": tokens
            })

    return perguntas


def main():
    arquivo = "nlp_features_train.csv"      # arquivo do dataset Quora Question Pairs
    coluna = "question1"       # pode trocar para question2
    limite = 5000              # ajuste conforme a máquina
    top_k = 20                 # quantidade de pares mais similares

    print("Carregando dataset...")
    #df = pd.read_csv(arquivo)
    df = pd.read_csv(arquivo, encoding="latin1")

    print("Preparando perguntas...")
    perguntas = preparar_perguntas(df, coluna, limite)

    total_perguntas = len(perguntas)
    total_comparacoes = total_perguntas * (total_perguntas - 1) // 2

    print(f"Total de perguntas usadas: {total_perguntas}")
    print(f"Total de comparações a realizar: {total_comparacoes}")

    resultados = []

    inicio = time.time()

    contador = 0
    for i, j in combinations(range(total_perguntas), 2):
        sim = similaridade_jaccard(
            perguntas[i]["tokens"],
            perguntas[j]["tokens"]
        )

        resultados.append({
            "indice_lista_1": i,
            "indice_lista_2": j,
            "linha_1": perguntas[i]["linha_original"],   # 👈 NOVO
            "linha_2": perguntas[j]["linha_original"],   # 👈 NOVO
            "pergunta_1": perguntas[i]["texto_original"],
            "pergunta_2": perguntas[j]["texto_original"],
            "similaridade": sim
        })

        contador += 1
        if contador % 100000 == 0:
            print(f"Comparações realizadas: {contador}/{total_comparacoes}")

    fim = time.time()

    resultados_ordenados = sorted(
        resultados,
        key=lambda x: x["similaridade"],
        reverse=True
    )

    print("\n=== RESULTADO ===")
    print(f"Tempo total serial: {fim - inicio:.2f} segundos")
    print(f"Total de pares avaliados: {len(resultados)}")

    print(f"\nTop {top_k} pares mais similares:\n")
    for pos, item in enumerate(resultados_ordenados[:top_k], start=1):
        print(f"Par #{pos}")
        print(f"Similaridade: {item['similaridade']:.4f}")
        print(f"Linha pergunta 1: {item['linha_1']}")
        print(f"Linha pergunta 2: {item['linha_2']}")
        print(f"Pergunta 1: {item['pergunta_1']}")
        print(f"Pergunta 2: {item['pergunta_2']}")
        print("-" * 80)


if __name__ == "__main__":
    main()