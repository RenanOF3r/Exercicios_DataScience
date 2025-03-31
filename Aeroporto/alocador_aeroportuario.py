import subprocess
import sys
import platform # Para checar o sistema operacional

def instalar(pacote):
    """Instala um pacote Python usando pip."""
    print(f"Tentando instalar {pacote}...")
    try:
        # Tenta usar 'pip3' primeiro, comum em Linux/macOS
        comando = [sys.executable, "-m", "pip", "install", pacote]
        if platform.system() != "Windows":
             # Em alguns sistemas, 'pip' pode ser 'pip3'
             try:
                 subprocess.check_call(comando)
             except FileNotFoundError:
                 comando = ["pip3", "install", pacote] # Tenta 'pip3' diretamente
                 subprocess.check_call(comando)
        else:
            subprocess.check_call(comando) # Usa o comando padrão no Windows

        print(f"{pacote} instalado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Falha ao instalar {pacote}. Erro: {e}")
        print("Por favor, tente instalar manualmente usando 'pip install {pacote}' ou 'pip3 install {pacote}'.")
        sys.exit(1) # Sai se a instalação falhar, pois é uma dependência crítica
    except FileNotFoundError:
         print(f"Erro: Comando 'pip' ou '{sys.executable} -m pip' não encontrado.")
         print("Certifique-se de que o Python e o pip estão instalados e no PATH do sistema.")
         sys.exit(1)

# --- Verificação e Instalação de Dependências ---
try:
    import pandas as pd
except ImportError:
    instalar("pandas")
    import pandas as pd

try:
    # Especifica a versão que funcionou anteriormente, se necessário
    # Se houver problemas, pode tentar sem a versão específica: instalar("ortools")
    from ortools.sat.python import cp_model
except ImportError:
    instalar("ortools==9.7.2996")
    from ortools.sat.python import cp_model
except Exception as e:
     print(f"Ocorreu um erro inesperado ao importar ortools: {e}")
     # Verifica se o erro ainda é sobre pandas, apesar da tentativa de instalação
     if 'pandas' in str(e):
         print("A instalação do pandas pode não ter sido bem-sucedida ou o ambiente precisa ser reiniciado.")
     sys.exit(1)


try:
    import matplotlib.pyplot as plt
except ImportError:
    instalar("matplotlib")
    import matplotlib.pyplot as plt

# --- Função Principal de Alocação ---
def alocar_avioes(total_avioes, total_estacionamentos, total_tempo,
                  momento_de_chegada, tempo_duracao, custos,
                  mostrar_grafico=False):
    """
    Aloca aviões a estacionamentos usando OR-Tools CP-SAT para minimizar custos.
    """
    print(f"\nIniciando alocação para {total_avioes} aviões, {total_estacionamentos} estac., {total_tempo} unidades de tempo.")

    modelo = cp_model.CpModel()
    solucionador = cp_model.CpSolver()
    # Aumentar o tempo limite pode ajudar em problemas complexos, mas pode demorar
    # solucionador.parameters.max_time_in_seconds = 60.0

    # --- Variáveis de Decisão ---
    # X[i][j][k] = 1 se avião i está no estacionamento j no tempo k, 0 caso contrário
    X = [[[modelo.NewBoolVar(f'X_av{i}_est{j}_t{k}')
          for k in range(total_tempo)]
          for j in range(total_estacionamentos)]
          for i in range(total_avioes)]

    # Y[i][j] = 1 se avião i USA o estacionamento j, 0 caso contrário
    Y = [[modelo.NewBoolVar(f'Y_av{i}_usa_est{j}')
          for j in range(total_estacionamentos)]
          for i in range(total_avioes)]

    # --- Restrições ---

    # 1. Exclusividade do Estacionamento: No máximo um avião por estacionamento por tempo
    for j in range(total_estacionamentos):
        for k in range(total_tempo):
            modelo.Add(sum(X[i][j][k] for i in range(total_avioes)) <= 1)

    # 2. Restrições por Avião
    for i in range(total_avioes):
        # a) Duração Zero: Se duração é 0, não alocar.
        if tempo_duracao[i] == 0:
            modelo.Add(sum(Y[i][j] for j in range(total_estacionamentos)) == 0)
            for j in range(total_estacionamentos):
                for k in range(total_tempo):
                    modelo.Add(X[i][j][k] == 0)
            continue # Pula para o próximo avião

        # b) Alocação Única: Usar exatamente UM estacionamento se duração > 0.
        modelo.Add(sum(Y[i][j] for j in range(total_estacionamentos)) == 1)

        # c) Vinculação X e Y e Duração Correta:
        for j in range(total_estacionamentos):
            uso_estacionamento_j = [X[i][j][k] for k in range(total_tempo)]

            # Se Y[i][j]=1, a soma(X[i][j][k] para todo k) deve ser igual a tempo_duracao[i]
            modelo.Add(sum(uso_estacionamento_j) == tempo_duracao[i]).OnlyEnforceIf(Y[i][j])
            # Se Y[i][j]=0, a soma(X[i][j][k] para todo k) deve ser 0
            modelo.Add(sum(uso_estacionamento_j) == 0).OnlyEnforceIf(Y[i][j].Not())

        # d) Chegada: Não pode estar antes da chegada.
        for j in range(total_estacionamentos):
            for k in range(momento_de_chegada[i]):
                modelo.Add(X[i][j][k] == 0)

        # e) Ocupação na Chegada: Deve ocupar UM estacionamento no momento exato da chegada.
        #    (Só faz sentido se chegar dentro do horizonte de tempo)
        if momento_de_chegada[i] < total_tempo:
            vars_chegada = [X[i][j][momento_de_chegada[i]] for j in range(total_estacionamentos)]
            modelo.Add(sum(vars_chegada) == 1)
            # Esta restrição, combinada com Y=1 para um j* e X=0 para j!=j*,
            # força que X[i][j*][chegada[i]] == 1.

        # f) Contiguidade: Se um avião usa um estacionamento, deve ser por um bloco contínuo.
        #    Esta é uma restrição complexa e pode ser fonte de inviabilidade.
        #    Vamos garantir que, se X[k1]=1 e X[k2]=1 (k2 > k1), todos X entre eles são 1.
        #    Aplicamos isso apenas se Y[i][j] for verdadeiro.
        if tempo_duracao[i] > 1: # Só relevante se duração > 1
             for j in range(total_estacionamentos):
                 # Criamos variáveis booleanas intermediárias para clareza (opcional)
                 # b_Y = Y[i][j]

                 for k1 in range(total_tempo):
                     # b_X_k1 = modelo.NewBoolVar('') # Poderia usar reificação se necessário
                     # modelo.Add(X[i][j][k1] == 1).OnlyEnforceIf(b_X_k1)
                     # modelo.Add(X[i][j][k1] == 0).OnlyEnforceIf(b_X_k1.Not())

                     for k2 in range(k1 + 2, total_tempo): # k2 é pelo menos k1+2
                         # b_X_k2 = modelo.NewBoolVar('')
                         # modelo.Add(X[i][j][k2] == 1).OnlyEnforceIf(b_X_k2)
                         # modelo.Add(X[i][j][k2] == 0).OnlyEnforceIf(b_X_k2.Not())

                         for k_meio in range(k1 + 1, k2):
                             # b_X_meio = modelo.NewBoolVar('')
                             # modelo.Add(X[i][j][k_meio] == 1).OnlyEnforceIf(b_X_meio)
                             # modelo.Add(X[i][j][k_meio] == 0).OnlyEnforceIf(b_X_meio.Not())

                             # A implicação (X[k1] AND X[k2]) => X[k_meio]
                             # é equivalente a: X[k1] + X[k2] - 1 <= X[k_meio]
                             # Aplicamos esta restrição apenas se Y[i][j] for verdadeiro.
                             modelo.Add(X[i][j][k1] + X[i][j][k2] - 1 <= X[i][j][k_meio]).OnlyEnforceIf(Y[i][j])


    # --- Função Objetivo ---
    # Minimizar o custo total da alocação (custo associado ao estacionamento escolhido Y[i][j])
    custo_total = modelo.NewIntVar(0, sum(max(c) for c in custos) * total_avioes, 'custo_total')
    modelo.Add(custo_total == sum(custos[i][j] * Y[i][j]
                                  for i in range(total_avioes)
                                  for j in range(total_estacionamentos)))
    modelo.Minimize(custo_total)

    # --- Resolver o Modelo ---
    print("Resolvendo o modelo...")
    status = solucionador.Solve(modelo)

    # --- Apresentar Resultados ---
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(f"\nSolução encontrada (Status: {solucionador.StatusName(status)})")
        print(f"Custo total mínimo: {solucionador.ObjectiveValue()}")
        print("Alocações:")
        alocacoes_plot = [] # Dados para o gráfico
        for i in range(total_avioes):
            if tempo_duracao[i] == 0:
                print(f"  Avião {i}: Não necessita alocação (duração 0).")
                continue

            alocado = False
            for j in range(total_estacionamentos):
                 if solucionador.Value(Y[i][j]) > 0.5: # Verifica se Y[i][j] é verdadeiro
                    tempo_inicio = -1
                    tempo_fim = -1
                    tempos_ocupados = []
                    for k in range(total_tempo):
                        if solucionador.Value(X[i][j][k]) > 0.5:
                            tempos_ocupados.append(k)
                            if tempo_inicio == -1:
                                tempo_inicio = k # Primeiro tempo encontrado
                            tempo_fim = k # Último tempo encontrado

                    duracao_real = len(tempos_ocupados)
                    print(f"  Avião {i} -> Estac. {j} | Custo: {custos[i][j]:<5} | Tempo: {tempo_inicio} a {tempo_fim} (Duração esperada: {tempo_duracao[i]}, real: {duracao_real})")
                    if duracao_real != tempo_duracao[i]:
                         print(f"      * Aviso: Duração real ({duracao_real}) diferente da esperada ({tempo_duracao[i]})! Tempos: {tempos_ocupados}")
                    if tempo_inicio != momento_de_chegada[i]:
                         print(f"      * Aviso: Início ({tempo_inicio}) diferente da chegada ({momento_de_chegada[i]})!")

                    alocacoes_plot.append({
                        'aviao': i,
                        'estacionamento': j,
                        'inicio': tempo_inicio,
                        'duracao': duracao_real, # Usar duração real para plot
                        'cor_idx': i # Índice para cor
                    })
                    alocado = True
                    break # Já encontrou o estacionamento único para este avião

            if not alocado:
                 print(f"  Avião {i}: Não foi alocado (verifique se houve erro ou se é viável).")

        if mostrar_grafico and alocacoes_plot:
            plot_alocacoes_por_aviao(alocacoes_plot, total_avioes, total_estacionamentos, total_tempo)
        elif mostrar_grafico:
             print("Gráfico não gerado pois não há alocações válidas.")

    else:
        print(f"\nNenhuma solução viável encontrada. Status: {solucionador.StatusName(status)}")
        # Se for INFEASIBLE, pode ser útil analisar o conflito.
        # Isso requer ferramentas mais avançadas ou análise manual das restrições vs dados.
        # print("Verifique os dados de entrada e as restrições do modelo.")


# --- Função de Plotagem ---
def plot_alocacoes_por_aviao(alocacoes, total_avioes, total_estacionamentos, total_tempo):
    """Plota as alocações com um avião por linha e cores por estacionamento."""
    fig, ax = plt.subplots(figsize=(max(15, total_tempo * 0.6), max(6, total_avioes * 0.6)))
    # Usar um mapa de cores para os estacionamentos
    cores_estac = plt.cm.get_cmap('tab10', total_estacionamentos)

    for aloc in alocacoes:
        aviao_id = aloc['aviao']
        inicio = aloc['inicio']
        duracao = aloc['duracao']
        estacionamento_id = aloc['estacionamento']

        # Desenha a barra horizontal
        ax.broken_barh([(inicio, duracao)], # (início, duração)
                       (aviao_id * 10, 9),    # (posição_y, altura_barra)
                       facecolors=cores_estac(estacionamento_id % 10), # Cor baseada no estacionamento
                       edgecolor='black', linewidth=0.5)

        # Adiciona texto indicando o estacionamento dentro da barra
        texto_cor = 'white' if duracao > 0 else 'black' # Cor do texto (ajustar se necessário)
        ax.text(inicio + duracao / 2, aviao_id * 10 + 4.5, f'E{estacionamento_id}',
                ha='center', va='center', color=texto_cor, fontsize=9, fontweight='bold')

    ax.set_xlabel("Unidade de Tempo")
    ax.set_ylabel("Aviões")
    ax.set_yticks([i * 10 + 4.5 for i in range(total_avioes)])
    ax.set_yticklabels([f"Avião {i}" for i in range(total_avioes)])
    ax.set_xticks(range(0, total_tempo + 1, max(1, total_tempo // 20))) # Ajusta ticks do eixo X
    ax.set_xlim(-0.5, total_tempo + 0.5) # Limites do eixo X
    ax.set_ylim(-5, total_avioes * 10 + 5) # Limites do eixo Y
    ax.grid(True, axis='x', linestyle=':', alpha=0.7) # Grade vertical sutil
    plt.title(f"Alocação de Aviões ({len(alocacoes)}/{total_avioes}) nos Estacionamentos")
    plt.tight_layout()
    # Salvar figura (opcional)
    # plt.savefig("alocacao_avioes.png")
    plt.show()


# --- Dados dos Exemplos ---

# Exemplo Pequeno (Ajustado para ter mais chance de ser viável)
print("--- Exemplo Pequeno ---")
alocar_avioes(
    total_avioes=3,
    total_estacionamentos=2, # Menos estacionamentos
    total_tempo=10,          # Horizonte de tempo
    momento_de_chegada=[0, 2, 5], # Chegadas mais espaçadas
    tempo_duracao=[3, 4, 2],    # Duração no solo
    custos=[
        [10, 50],  # Custos Av 0 (Est 0, Est 1)
        [10, 60],  # Custos Av 1 (Est 0, Est 1)
        [40, 5]    # Custos Av 2 (Est 0, Est 1) -> Prefere Est 1
    ],
    mostrar_grafico=True
)

# Exemplo Grande
print("\n--- Exemplo Grande ---")
alocar_avioes(
    total_avioes=12,
    total_estacionamentos=5,
    total_tempo=24,
    momento_de_chegada=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], # Chegadas sequenciais
    tempo_duracao=     [3, 4, 5, 2, 3, 4, 2, 3, 2, 4, 3, 3], # Durações variadas
    # Custos: Custo crescente com índice do estacionamento, com pequena variação por avião
    custos=[[(j + 1) * 100 + i * 5 for j in range(5)] for i in range(12)],
    mostrar_grafico=True # Habilitar gráfico
)

print("\nExecução concluída.")
