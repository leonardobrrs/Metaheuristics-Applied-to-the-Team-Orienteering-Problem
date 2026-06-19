import json
import time
import random
import copy

# =====================================================================
# BLOCO 1: LEITURA E REPRESENTAÇÃO DOS DADOS
# =====================================================================
def carregar_instancias(arquivos):
    """Lê os arquivos JSON e junta todas as instâncias num único dicionário."""
    instancias = {}
    for arquivo in arquivos:
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                instancias.update(dados)
        except FileNotFoundError:
            print(f"[Aviso] Arquivo {arquivo} não encontrado. O script continuará com as instâncias disponíveis.\n")
    return instancias

# =====================================================================
# BLOCO 2: CONSTRUÇÃO GULOSA (SOLUÇÃO INICIAL)
# =====================================================================
def construcao_gulosa(instancia):
    """Cria a rota inicial priorizando escolas com o melhor custo-benefício."""
    num_viaturas = instancia['num_viaturas']
    tmax = instancia['turno_minutos']
    nos = instancia['nos']
    matriz_tempo = instancia['matriz_tempos'] 
    chamados = instancia['chamados']
    
    # Mapear o ID real da escola (ex: 59) para o índice na matriz (ex: 1)
    id_to_idx = {no: idx for idx, no in enumerate(nos)}
    idx_sede = id_to_idx[0]
    
    # Organizar informações dos chamados
    escolas_info = {c['id']: c for c in chamados}
    escolas_pendentes = list(escolas_info.keys())
    
    # Inicializar as rotas (todas saem da Sede = 0)
    rotas = [[0] for _ in range(num_viaturas)]
    tempos_viaturas = [0.0 for _ in range(num_viaturas)]
    score_total = 0
    
    # Loop de preenchimento das viaturas
    while escolas_pendentes:
        melhor_escola = None
        melhor_viatura = -1
        melhor_razao = -1
        melhor_acrescimo = 0
        
        for k in range(num_viaturas):
            no_atual = rotas[k][-1]
            idx_atual = id_to_idx[no_atual]
            
            for escola in escolas_pendentes:
                idx_escola = id_to_idx[escola]
                
                tempo_ida = matriz_tempo[idx_atual][idx_escola]
                tempo_servico = escolas_info[escola]['tempo_atendimento_min']
                tempo_volta_sede = matriz_tempo[idx_escola][idx_sede]
                
                tempo_necessario = tempo_ida + tempo_servico + tempo_volta_sede
                
                if tempos_viaturas[k] + tempo_necessario <= tmax:
                    razao = escolas_info[escola]['score'] / (tempo_ida + tempo_servico)
                    
                    if razao > melhor_razao:
                        melhor_razao = razao
                        melhor_escola = escola
                        melhor_viatura = k
                        melhor_acrescimo = tempo_ida + tempo_servico
        
        if melhor_escola is not None:
            rotas[melhor_viatura].append(melhor_escola)
            tempos_viaturas[melhor_viatura] += melhor_acrescimo
            score_total += escolas_info[melhor_escola]['score']
            escolas_pendentes.remove(melhor_escola)
        else:
            break 
            
    # Fechar as rotas, obrigando as viaturas a voltar para a Sede (0)
    for k in range(num_viaturas):
        no_atual = rotas[k][-1]
        idx_atual = id_to_idx[no_atual]
        tempos_viaturas[k] += matriz_tempo[idx_atual][idx_sede]
        rotas[k].append(0)
        
    return rotas, score_total, tempos_viaturas, escolas_pendentes

# =====================================================================
# BLOCO 3: BUSCA LOCAL (RVND)
# =====================================================================
def calcular_tempo_rota(rota, matriz_tempo, chamados_info, id_to_idx):
    """Calcula o tempo total exato (Viagem + Serviço) de uma rota."""
    tempo_total = 0.0
    for i in range(len(rota) - 1):
        atual = rota[i]
        prox = rota[i+1]
        idx_atual = id_to_idx[atual]
        idx_prox = id_to_idx[prox]
        
        tempo_viagem = matriz_tempo[idx_atual][idx_prox]
        tempo_servico = chamados_info[prox]['tempo_atendimento_min'] if prox != 0 else 0
            
        tempo_total += tempo_viagem + tempo_servico
    return tempo_total

def vizinhanca_swap(rotas, tempos_viaturas, matriz_tempo, chamados_info, id_to_idx, tmax):
    """Troca duas escolas de posição na mesma rota para economizar tempo no trânsito."""
    for k in range(len(rotas)):
        rota = rotas[k]
        if len(rota) < 4: continue # Precisa de pelo menos 2 escolas na rota para trocar
        
        for i in range(1, len(rota) - 2):
            for j in range(i + 1, len(rota) - 1):
                rota[i], rota[j] = rota[j], rota[i] # Faz o swap
                novo_tempo = calcular_tempo_rota(rota, matriz_tempo, chamados_info, id_to_idx)
                
                # Aceita se economizar tempo
                if novo_tempo < tempos_viaturas[k]:
                    tempos_viaturas[k] = novo_tempo
                    return True
                else:
                    rota[i], rota[j] = rota[j], rota[i] # Desfaz o swap
    return False

def vizinhanca_add(rotas, tempos_viaturas, score_total, pendentes, matriz_tempo, chamados_info, id_to_idx, tmax):
    """Tenta inserir uma escola pendente em qualquer posição de qualquer viatura se sobrar tempo."""
    for k in range(len(rotas)):
        rota = rotas[k]
        for escola in pendentes:
            for pos in range(1, len(rota)):
                rota.insert(pos, escola) # Tenta encaixar no meio
                novo_tempo = calcular_tempo_rota(rota, matriz_tempo, chamados_info, id_to_idx)
                
                if novo_tempo <= tmax: # Se couber no turno, lucro!
                    tempos_viaturas[k] = novo_tempo
                    score_total += chamados_info[escola]['score']
                    pendentes.remove(escola)
                    return score_total, True
                else:
                    rota.pop(pos) # Desfaz
    return score_total, False

def vizinhanca_replace(rotas, tempos_viaturas, score_total, pendentes, matriz_tempo, chamados_info, id_to_idx, tmax):
    """Remove uma escola atendida e tenta colocar uma de fora que dê um Score maior ou igual."""
    for k in range(len(rotas)):
        rota = rotas[k]
        for i in range(1, len(rota) - 1):
            escola_atual = rota[i]
            
            for escola_nova in pendentes:
                score_atual = chamados_info[escola_atual]['score']
                score_novo = chamados_info[escola_nova]['score']
                
                if score_novo >= score_atual:
                    rota[i] = escola_nova # Tenta a substituição
                    novo_tempo = calcular_tempo_rota(rota, matriz_tempo, chamados_info, id_to_idx)
                    ganho_score = score_novo - score_atual
                    
                    # Aceita se der mais pontos E couber no turno OR se der o mesmo ponto e economizar tempo
                    if novo_tempo <= tmax and (ganho_score > 0 or novo_tempo < tempos_viaturas[k]):
                        tempos_viaturas[k] = novo_tempo
                        score_total += ganho_score
                        pendentes.remove(escola_nova)
                        pendentes.append(escola_atual) # A antiga volta pro banco de reservas
                        return score_total, True
                    else:
                        rota[i] = escola_atual # Desfaz
    return score_total, False

def rvnd(rotas, score, tempos, pendentes, instancia):
    """O motor central que embaralha e aplica as vizinhanças até atingir o ótimo local."""
    tmax = instancia['turno_minutos']
    matriz_tempo = instancia['matriz_tempos']
    chamados_info = {c['id']: c for c in instancia['chamados']}
    id_to_idx = {no: idx for idx, no in enumerate(instancia['nos'])}
    
    vizinhancas = [1, 2, 3] # 1: Swap, 2: Add, 3: Replace
    
    while vizinhancas:
        v = random.choice(vizinhancas)
        melhorou = False
        
        if v == 1:
            melhorou = vizinhanca_swap(rotas, tempos, matriz_tempo, chamados_info, id_to_idx, tmax)
        elif v == 2:
            score, melhorou = vizinhanca_add(rotas, tempos, score, pendentes, matriz_tempo, chamados_info, id_to_idx, tmax)
        elif v == 3:
            score, melhorou = vizinhanca_replace(rotas, tempos, score, pendentes, matriz_tempo, chamados_info, id_to_idx, tmax)
            
        if melhorou:
            vizinhancas = [1, 2, 3] # Encontrou melhoria, reseta a busca para tentar tudo de novo
        else:
            vizinhancas.remove(v) # Esgotou essa vizinhança, remove da lista
            
    return rotas, score, tempos

# =====================================================================
# BLOCO 4: PERTURBAÇÃO E ITERATED LOCAL SEARCH (ILS)
# =====================================================================
def perturbacao(rotas, score_total, tempos_viaturas, pendentes, instancia, forca=0.3):
    """
    Destrói parcialmente as rotas atuais (remove % de escolas aleatórias)
    para tentar escapar de ótimos locais.
    """
    novas_rotas = copy.deepcopy(rotas)
    novo_score = score_total
    novos_tempos = list(tempos_viaturas)
    novos_pendentes = list(pendentes)
    
    matriz_tempo = instancia['matriz_tempos']
    chamados_info = {c['id']: c for c in instancia['chamados']}
    id_to_idx = {no: idx for idx, no in enumerate(instancia['nos'])}
    
    # Percorre cada viatura e remove escolas aleatoriamente
    for k in range(len(novas_rotas)):
        rota = novas_rotas[k]
        
        # Só perturba se a rota tiver pelo menos 2 escolas atendidas (além da Sede 0 na ponta)
        if len(rota) > 3: 
            qtd_remover = max(1, int((len(rota) - 2) * forca)) # Remove pelo menos 1
            
            # Escolhe posições aleatórias para remover (ignorando a sede na ponta 0 e -1)
            posicoes_para_remover = random.sample(range(1, len(rota) - 1), qtd_remover)
            posicoes_para_remover.sort(reverse=True) # Remove de trás pra frente para não bagunçar os índices
            
            for pos in posicoes_para_remover:
                escola_removida = rota.pop(pos)
                novo_score -= chamados_info[escola_removida]['score']
                novos_pendentes.append(escola_removida)
                
            # Recalcula o tempo da viatura após os cortes
            novos_tempos[k] = calcular_tempo_rota(rota, matriz_tempo, chamados_info, id_to_idx)
            
    return novas_rotas, novo_score, novos_tempos, novos_pendentes

def iteradas_local_search(instancia, iteracoes_max=250):
    """
    O loop principal do ILS.
    """
    # 1. Solução Inicial Gulosa
    rotas, score, tempos, pendentes = construcao_gulosa(instancia)
    
    # 2. Primeira Busca Local (RVND)
    rotas_best, score_best, tempos_best = rvnd(rotas, score, tempos, pendentes, instancia)
    pendentes_best = list(pendentes)
    
    iteracoes_sem_melhoria = 0
    
    # Loop do ILS
    while iteracoes_sem_melhoria < iteracoes_max:
        # A. Perturba a solução atual (O pontapé)
        r_pert, s_pert, t_pert, p_pert = perturbacao(rotas_best, score_best, tempos_best, pendentes_best, instancia, forca=0.3)
        
        # B. Tenta reconstruir e melhorar com o RVND
        r_nova, s_nova, t_nova = rvnd(r_pert, s_pert, t_pert, p_pert, instancia)
        
        # C. Critério de Aceitação: Foi melhor que o meu ótimo histórico?
        if s_nova > score_best:
            score_best = s_nova
            rotas_best = copy.deepcopy(r_nova)
            tempos_best = list(t_nova)
            pendentes_best = list(p_pert)
            iteracoes_sem_melhoria = 0 # Reseta a contagem
        else:
            iteracoes_sem_melhoria += 1 # Conta que não melhorou
            
    return rotas_best, score_best, tempos_best

# =====================================================================
# EXECUÇÃO PRINCIPAL
# =====================================================================
if __name__ == "__main__":
    arquivos_instancias = ['instancias.json', 'instancia_5.json', 'instancia_6.json']
    instancias = carregar_instancias(arquivos_instancias)
    
    print("--- RESULTADOS FINAIS: ILS + RVND ---\n")
    
    for chave, instancia in instancias.items():
        print(f"[{chave}]")
        print(f"Viaturas: {instancia['num_viaturas']} | Turno: {instancia['turno_minutos']} min")
        
        inicio = time.perf_counter()
        
        # Chama direto o motor completo do ILS
        rotas, score_final, tempos = iteradas_local_search(instancia, iteracoes_max=250)
        
        fim = time.perf_counter()
        
        print(f"--> Score Máximo Encontrado: {score_final} pontos")
        print(f"--> Tempo Total: {(fim - inicio):.4f} segundos")
        
        for i, rota in enumerate(rotas):
            print(f"    Viatura {i+1}: Tempo {tempos[i]:.1f} min | Rota: {rota}")
        print("-" * 60)