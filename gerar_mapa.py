import pandas as pd
import folium
import requests
import time

# =====================================================================
# 1. CARREGAR COORDENADAS
# =====================================================================
ARQUIVO_COORDENADAS = "Base_Geografica_Escolas_Maceio_SEDUC.xlsx"
NOME_ABA = "Pontos (Escolas+Sede)"

print("A ler as coordenadas geográficas do Excel...")
df = pd.read_excel(ARQUIVO_COORDENADAS, sheet_name=NOME_ABA)

coordenadas = {}
for _, linha in df.iterrows():
    coordenadas[int(linha['ID'])] = (linha['Latitude'], linha['Longitude'], linha['Nome'])

# =====================================================================
# 2. ROTAS VENCEDORAS DE TODAS AS INSTÂNCIAS (Resultados do ILS-RVND)
# =====================================================================
todas_as_rotas = {
    "Instancia_1_Dia_Normal": [
        [0, 44, 59, 20, 25, 65, 0],
        [0, 15, 64, 45, 18, 70, 0]
    ],
    "Instancia_2_Dia_Caos": [
        [0, 60, 43, 75, 40, 0],
        [0, 95, 67, 102, 36, 0]
    ],
    "Instancia_3_Crise_Frota": [
        [0, 50, 64, 32, 75, 72, 49, 86, 0]
    ],
    "Instancia_4_Escala_Completa": [
        [0, 70, 78, 58, 47, 22, 25, 0],
        [0, 15, 54, 56, 14, 90, 0],
        [0, 82, 92, 73, 76, 95, 16, 89, 23, 21, 68, 0]
    ],
    "Instancia_5_Grande": [
        [0, 102, 53, 1, 76, 11, 3, 95, 0],
        [0, 15, 5, 28, 23, 79, 12, 50, 0],
        [0, 83, 69, 55, 8, 97, 17, 80, 0]
    ],
    "Instancia_6_Malha_Completa_SEDUC": [
        [0, 65, 34, 78, 37, 27, 42, 17, 0],
        [0, 93, 99, 56, 4, 48, 8, 44, 69, 7, 102, 0],
        [0, 66, 95, 101, 6, 21, 86, 28, 49, 5, 0],
        [0, 43, 74, 1, 63, 73, 89, 100, 41, 68, 0],
        [0, 64, 50, 29, 30, 104, 16, 2, 52, 0]
    ]
}

cores = ['blue', 'red', 'green']

# =====================================================================
# 3. GERADOR DE MAPAS POR INSTÂNCIA
# =====================================================================
lat_sede, lon_sede, nome_sede = coordenadas[0]

for nome_instancia, rotas_instancia in todas_as_rotas.items():
    print(f"\nA gerar mapa para: {nome_instancia}...")
    
    # Inicializa um novo mapa limpo
    mapa = folium.Map(location=[lat_sede, lon_sede], zoom_start=13, tiles='CartoDB positron')

    # Marcador da Sede (CEPA)
    folium.Marker(
        [lat_sede, lon_sede],
        popup=f"<b>SEDE (CEPA):</b><br>{nome_sede}",
        icon=folium.Icon(color='black', icon='home', prefix='fa')
    ).add_to(mapa)

    # Iterar sobre as viaturas dessa instância
    for i, rota in enumerate(rotas_instancia):
        cor = cores[i % len(cores)] # Garante que não falta cor se houver mais viaturas
        coords_para_osrm = []
        
        # Adicionar marcadores e preparar string para o GPS
        for id_escola in rota:
            lat, lon, nome = coordenadas[id_escola]
            coords_para_osrm.append(f"{lon},{lat}")
            
            if id_escola != 0:
                folium.Marker(
                    [lat, lon],
                    popup=f"<b>Viatura {i+1}</b><br>{nome}",
                    icon=folium.Icon(color=cor, icon='wrench', prefix='fa')
                ).add_to(mapa)

        # Chamar a API pública do OSRM
        coordenadas_str = ";".join(coords_para_osrm)
        url_osrm = f"http://router.project-osrm.org/route/v1/driving/{coordenadas_str}?overview=full&geometries=geojson"
        
        try:
            resposta = requests.get(url_osrm)
            dados = resposta.json()
            
            if dados.get('code') == 'Ok':
                rota_geojson = dados['routes'][0]['geometry']
                pontos_reais_ruas = [(coord[1], coord[0]) for coord in rota_geojson['coordinates']]
                
                folium.PolyLine(
                    pontos_reais_ruas,
                    color=cor,
                    weight=5,
                    opacity=0.8,
                    tooltip=f"Rota da Viatura {i+1}"
                ).add_to(mapa)
            else:
                print(f"  [Aviso] OSRM falhou na Viatura {i+1}.")
                
        except Exception as e:
            print(f"  [Erro] Falha ao ligar à API do OSRM: {e}")
            
        # Pausa de 1 segundo para não sobrecarregar a API pública
        time.sleep(1)

    # Salvar o ficheiro HTML específico para esta instância
    nome_arquivo_saida = f"mapa_{nome_instancia}.html"
    mapa.save(nome_arquivo_saida)
    print(f"  -> Concluído! Salvo como '{nome_arquivo_saida}'.")

print("\nTodos os mapas foram gerados com sucesso!")