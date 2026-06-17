# Metaheurísticas Aplicadas ao Team Orienteering Problem

Implementação e experimentos computacionais para o **Team Orienteering Problem (TOP)** aplicados a um cenário real de suporte técnico às escolas estaduais de Maceió-AL.

## 📌 Visão Geral

Este projeto investiga o uso de métodos exatos e metaheurísticas para resolver o **Team Orienteering Problem (TOP)**, considerando o roteamento de equipes de suporte de TI responsáveis pelo atendimento das escolas da rede estadual.

Cada escola é representada por um nó contendo:

* uma pontuação de prioridade (score);
* um tempo de atendimento;
* tempos de deslocamento entre os nós;
* uma restrição de duração máxima do turno.

O objetivo é maximizar a soma das prioridades atendidas sem ultrapassar o tempo disponível de cada viatura.

---

## 📚 Descrição do Problema

Dado:

* uma sede (SEDUC-AL);
* um conjunto de escolas;
* uma frota de viaturas;
* tempos de deslocamento entre os nós;
* tempos de atendimento em cada escola;
* níveis de prioridade para os chamados;

deseja-se determinar as rotas que maximizam a pontuação total obtida respeitando o limite de tempo de trabalho das equipes.

Esse problema corresponde ao clássico **Team Orienteering Problem (TOP)**, pertencente à classe dos problemas NP-difíceis.

---

## 🗺️ Estudo de Caso

O conjunto de dados utilizado é baseado na rede estadual de ensino de Maceió (AL):

* **104 escolas estaduais**;
* **1 depósito (SEDUC-AL)**;
* matrizes assimétricas de tempo e distância;
* tempos de atendimento associados à severidade dos incidentes de TI.

As matrizes de custos foram obtidas a partir de coordenadas geográficas reais utilizando serviços de roteamento.

---

## 📂 Estrutura do Repositório

```text
.
├── instances/
│   ├── instancias_top.json
│   ├── Instancia_1_Dia_Normal.dat
│   ├── Instancia_2_Dia_Caos.dat
│   ├── Instancia_3_Crise_Frota.dat
│   ├── Instancia_4_Escala_Completa.dat
│   └── Instancia_5_Grande.dat
│
├── cplex/
│   ├── top.mod
│   └── arquivos .dat
│
├── python/
│   ├── gerador_instancias.py
│   ├── json_to_dat.py
│   └── scripts auxiliares
│
├── mapas/
│   └── visualizações em Folium
│
└── README.md
```

---

## 🔢 Modelo Matemático

### Função Objetivo

<p align="center">

<img src="https://latex.codecogs.com/svg.image?\max\sum_{k\in K}\sum_{i\in V}S_i\,y_{ik}"/>

</p>

onde:

* (S_i): prioridade do chamado da escola (i);
* (y_{ik}): variável binária que indica se a escola (i) é atendida pela viatura (k).

---

### Restrição de Tempo

<p align="center">

<img src="https://latex.codecogs.com/svg.image?\sum_{i\in V}\sum_{j\in V}t_{ij}x_{ijk}+\sum_{i\in V}s_i\,y_{ik}\leq T_{max},\quad\forall k\in K"/>

</p>

em que:

* (t_{ij}): tempo de deslocamento entre os nós (i) e (j);
* (s_i): tempo de atendimento da escola (i);
* (T_{max}): duração máxima do turno de trabalho.

---

## ⚙️ Método Exato

O modelo matemático foi implementado utilizando:

* **IBM ILOG CPLEX Optimization Studio**

O CPLEX é utilizado como referência para comparação com as metaheurísticas.

---

## 📈 Resultados Computacionais

| Instância | Escolas | Viaturas | Resultado CPLEX |
| --------- | ------: | -------: | --------------- |
| 1         |      20 |        2 | Ótimo           |
| 2         |      20 |        2 | Ótimo           |
| 3         |      15 |        1 | Ótimo           |
| 4         |      30 |        3 | Gap = 3,53%     |
| 5         |      50 |        3 | Gap = 8,70%     |

As três primeiras instâncias foram resolvidas exatamente em poucos segundos. Para instâncias maiores, o crescimento do tempo computacional evidencia a dificuldade do problema e motiva o uso de metaheurísticas.

---

## 🚀 Trabalhos Futuros

Pretende-se implementar:

* ILS (Iterated Local Search);
* RVND (Random Variable Neighborhood Descent);
* ILS-RVND;
* GRASP;
* Algoritmos Genéticos;
* Team Orienteering Problem com Janelas de Tempo (TOPTW);
* Roteamento dinâmico utilizando informações de trânsito em tempo real.

---

## 📖 Referências

* CHAO, I. M.; GOLDEN, B. L.; WASIL, E. A. *The Team Orienteering Problem*. European Journal of Operational Research, v. 88, n. 3, p. 464–474, 1996.

* VANSTEENWEGEN, P.; SOUFFRIAU, W.; VAN OUDHEUSDEN, D. *The Orienteering Problem: A Survey*. European Journal of Operational Research, v. 209, n. 1, p. 1–10, 2011.

* LOURENÇO, H. R.; MARTIN, O. C.; STÜTZLE, T. *Iterated Local Search*. Handbook of Metaheuristics. Springer, 2003.

---

## 👨‍💻 Autores

* Leonardo Barros
* Eduardo Serpa
* José Herberty

**Universidade Federal de Alagoas (UFAL)**
Instituto de Computação (IC)
