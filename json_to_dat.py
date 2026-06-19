import json
import os

ARQUIVO_JSON = "instancia_6.json"

PASTA_SAIDA = "instancias_opl"

os.makedirs(PASTA_SAIDA, exist_ok=True)

# ==========================================================
# LER JSON
# ==========================================================
with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
    instancias = json.load(f)


# ==========================================================
# GERAR UM .dat PARA CADA INSTÂNCIA
# ==========================================================
for nome_instancia, dados in instancias.items():

    caminho_saida = os.path.join(
        PASTA_SAIDA,
        nome_instancia + ".dat"
    )

    nbNodes = len(dados["nos"])
    nbVehicles = dados["num_viaturas"]
    Tmax = dados["turno_minutos"]

    Score = dados["premios"]
    ServiceTime = dados["tempos_servico"]
    TravelTime = dados["matriz_tempos"]

    with open(caminho_saida, "w", encoding="utf-8") as arq:

        # --------------------------------------------------
        # Parâmetros básicos
        # --------------------------------------------------
        arq.write(f"nbNodes = {nbNodes};\n")
        arq.write(f"nbVehicles = {nbVehicles};\n")
        arq.write(f"Tmax = {Tmax};\n\n")

        # --------------------------------------------------
        # Score
        # --------------------------------------------------
        arq.write("Score = [\n")

        for i, valor in enumerate(Score):

            if i < len(Score)-1:
                arq.write(f"{valor}, ")
            else:
                arq.write(f"{valor}")

        arq.write("\n];\n\n")

        # --------------------------------------------------
        # Tempo de serviço
        # --------------------------------------------------
        arq.write("ServiceTime = [\n")

        for i, valor in enumerate(ServiceTime):

            if i < len(ServiceTime)-1:
                arq.write(f"{valor}, ")
            else:
                arq.write(f"{valor}")

        arq.write("\n];\n\n")

        # --------------------------------------------------
        # Matriz de tempos
        # --------------------------------------------------
        arq.write("TravelTime = [\n")

        for linha in TravelTime:

            arq.write("[")

            for j, valor in enumerate(linha):

                if j < len(linha)-1:
                    arq.write(f"{valor}, ")
                else:
                    arq.write(f"{valor}")

            arq.write("]")

            if linha != TravelTime[-1]:
                arq.write(",\n")

        arq.write("\n];\n")

    print(f"{nome_instancia}.dat criado.")

print("\nTodos os ficheiros OPL foram gerados com sucesso.")