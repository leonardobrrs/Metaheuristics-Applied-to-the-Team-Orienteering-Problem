import pandas as pd
import random
import json

# ==========================================================
# FICHEIROS
# ==========================================================
NOME_FICHEIRO_PONTOS = "Base_Geografica_Escolas_Maceio_SEDUC.xlsx"
NOME_ABA = "Pontos (Escolas+Sede)"

FICHEIRO_MATRIZ_TEMPO = "matriz_tempo_min.csv"
FICHEIRO_MATRIZ_DISTANCIA = "matriz_distancia_km.csv"

FICHEIRO_SAIDA = "instancia_6.json"


# ==========================================================
# LEITURA DOS DADOS
# ==========================================================
df = pd.read_excel(
    NOME_FICHEIRO_PONTOS,
    sheet_name=NOME_ABA
)

# Ordena pelos IDs
df = df.sort_values("ID")

# Remove a sede (ID = 0)
df_escolas = df[df["ID"] > 0]

# ==========================================================
# MATRIZ DE TEMPOS
# ==========================================================
matriz_tempo = pd.read_csv(
    FICHEIRO_MATRIZ_TEMPO,
    index_col=0
)

matriz_tempo.columns = matriz_tempo.columns.astype(int)
matriz_tempo.index = matriz_tempo.index.astype(int)

# ==========================================================
# MATRIZ DE DISTÂNCIAS
# ==========================================================
matriz_distancia = pd.read_csv(
    FICHEIRO_MATRIZ_DISTANCIA,
    index_col=0
)

matriz_distancia.columns = matriz_distancia.columns.astype(int)
matriz_distancia.index = matriz_distancia.index.astype(int)


# ==========================================================
# SORTEIO DE URGÊNCIA
# ==========================================================
def sortear_urgencia(prob_alta):

    chance = random.random()

    if chance < prob_alta:
        # Prioridade máxima
        return random.randint(8, 10), random.randint(90, 120)

    elif chance < prob_alta + 0.4:
        # Prioridade média
        return random.randint(4, 7), random.randint(45, 60)

    else:
        # Prioridade baixa
        return random.randint(1, 3), random.randint(20, 30)


# ==========================================================
# GERAÇÃO DA INSTÂNCIA
# ==========================================================
def gerar_instancia(
        df_escolas,
        nome,
        num_viaturas,
        turno_minutos,
        qtd_escolas,
        prob_alta):

    escolas_sorteadas = df_escolas.sample(n=qtd_escolas)

    chamados = []

    # Nó 0 = SEDUC
    ids_nos = [0]

    for _, escola in escolas_sorteadas.iterrows():

        score, tempo_atendimento = sortear_urgencia(prob_alta)

        id_escola = int(escola["ID"])

        ids_nos.append(id_escola)

        chamados.append({
            "id": id_escola,
            "nome": escola["Nome"],
            "score": score,
            "tempo_atendimento_min": tempo_atendimento
        })

    # Ordena os IDs
    ids_nos.sort()

    # ======================================================
    # SUBMATRIZES
    # ======================================================
    submatriz_tempos = []

    submatriz_distancias = []

    for i in ids_nos:

        linha_tempo = []

        linha_distancia = []

        for j in ids_nos:

            linha_tempo.append(
                round(
                    float(
                        matriz_tempo.loc[i, j]
                    ),
                    2
                )
            )

            linha_distancia.append(
                round(
                    float(
                        matriz_distancia.loc[i, j]
                    ),
                    2
                )
            )

        submatriz_tempos.append(linha_tempo)

        submatriz_distancias.append(linha_distancia)

    # ======================================================
    # VETORES AUXILIARES
    # ======================================================
    premios = [0]

    tempos_servico = [0]

    for chamado in chamados:

        premios.append(
            chamado["score"]
        )

        tempos_servico.append(
            chamado["tempo_atendimento_min"]
        )

    return {

        "nome_cenario": nome,

        "num_viaturas": num_viaturas,

        "turno_minutos": turno_minutos,

        # IDs dos nós da instância
        "nos": ids_nos,

        # Informações das escolas
        "chamados": chamados,

        # Lucros
        "premios": premios,

        # Tempos de serviço
        "tempos_servico": tempos_servico,

        # Matriz de deslocamento em minutos
        "matriz_tempos": submatriz_tempos,

        # Matriz de deslocamento em quilômetros
        "matriz_distancias": submatriz_distancias
    }


# ==========================================================
# MAIN
# ==========================================================
def main():

    print("Gerando instâncias...")

    instancias = {}


    
    # ======================================================
    # Instância 6
    # ======================================================
    instancias["Instancia_6_Estadual"] = gerar_instancia(
        df_escolas,
        nome="Instância Estadual (Stress Épico)",
        num_viaturas=5,
        turno_minutos=480,
        qtd_escolas=100,
        prob_alta=0.20
    )

    # ======================================================
    # SALVAR JSON
    # ======================================================
    with open(
            FICHEIRO_SAIDA,
            "w",
            encoding="utf-8") as f:

        json.dump(
            instancias,
            f,
            ensure_ascii=False,
            indent=4
        )

    print()
    print("Instâncias geradas com sucesso!")
    print(f"Ficheiro criado: {FICHEIRO_SAIDA}")


# ==========================================================
# EXECUÇÃO
# ==========================================================
if __name__ == "__main__":

    random.seed()

    main()
