# -*- coding: utf-8 -*-
"""
Código melhorado para alocação de aviões em estacionamentos de aeroporto,
incorporando as restrições e objetivo do notebook Final_Aula_5.ipynb.

Instruções:
1. Certifique-se de ter a biblioteca OR-Tools instalada:
   pip install ortools==9.7.2996 pandas==2.1.0
2. Execute este script Python.
"""

try:
    from ortools.sat.python import cp_model
except ModuleNotFoundError:
    print("Erro: A biblioteca 'ortools' não está instalada.")
    print("Execute 'pip install ortools==9.7.2996 pandas==2.1.0' no seu terminal ou ambiente.")
    # Decide whether to exit or let it fail later
    # exit() # Uncomment to exit immediately if ortools is missing

import pandas as pd # Embora pandas não seja usado diretamente no modelo, pode ser útil para entrada/saída

# --- Função para exibir a solução (adaptada do notebook) ---
# Nota: O uso de 'global' não é ideal em produção, mas mantido para consistência com o notebook.
variaveis_a_logar = []
def loga(variavel):
  global variaveis_a_logar
  variaveis_a_logar.append(variavel)

# Atualizando a função resolve para corresponder mais de perto ao notebook
# e incluir a variável Y e custos na impressão
def resolve(solucionador, modelo, X, Y, custos, total_avioes, total_estacionamentos, total_tempo):
  """Resolve o modelo e imprime a solução."""
  print("\nIniciando a resolução do modelo...")
  status = solucionador.Solve(modelo)
  status_name = cp_model.CpSolverStatus.Name(status)
  print(f"Status: {status} ({status_name})")

  # No notebook original, ele imprimia mesmo se não fosse ótimo, desde que fosse viável.
  # O código do notebook usava apenas cp_model.OPTIMAL, mas FEASIBLE também é uma solução válida.
  if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(f"Custo total objetivo: {solucionador.ObjectiveValue()}")
    print("\nAlocações encontradas (X):")
    alocacoes_encontradas = False
    for i in range(total_avioes):
      for j in range(total_estacionamentos):
        for k in range(total_tempo):
          try:
              if solucionador.Value(X[i][j][k]) == 1:
                print(f'  Avião {i} no estacionamento {j} no tempo {k}')
                alocacoes_encontradas = True
          except Exception as e:
              # Pode ocorrer erro se a variável não for usada ou o status for inválido
              # print(f"Erro ao obter valor para X[{i}][{j}][{k}]: {e}")
              pass
    if not alocacoes_encontradas:
        print("  Nenhuma alocação X encontrada na solução.")

    # Imprimir quais estacionamentos foram usados (variáveis Y)
    print("\nUso de Estacionamentos (Y):")
    uso_estacionamento_encontrado = False
    for i in range(total_avioes):
        for j in range(total_estacionamentos):
             try:
                 if solucionador.Value(Y[i][j]) == 1:
                     print(f'  Avião {i} usou o estacionamento {j} (Custo associado: {custos[i][j]})')
                     uso_estacionamento_encontrado = True
             except Exception as e:
                 # print(f"Erro ao obter valor para Y[{i}][{j}]: {e}")
                 pass
    if not uso_estacionamento_encontrado:
        print("  Nenhum uso de estacionamento Y encontrado na solução.")

    # Descomente para ver as variáveis de log (pode ser muita informação)
    # print("\nVariáveis de Log:")
    # for variavel in variaveis_a_logar:
    #   try:
    #     valor = solucionador.Value(variavel)
    #     print(f'  Variável {variavel.Name()} = {valor}')
    #   except Exception as e:
    #      print(f'  Não foi possível obter valor para {variavel.Name()}: {e}')

  else:
    print("Solução ótima ou viável não encontrada.")
  print("-" * 30)


# --- Parâmetros do Problema (Exemplo do Notebook com 3 Estacionamentos) ---
# Ajuste estes valores para o cenário 12x5x24 se necessário
total_avioes = 3
total_estacionamentos = 3 # Alterado para 3 para corresponder ao último exemplo do notebook
total_tempo = 5
momento_de_chegada = [1, 2, 0] # Primeiro tempo k que o avião i PODE chegar
tempo_duracao = [3, 3, 2]      # Número EXATO de tempos k que o avião i deve ficar estacionado
custos = [                     # Custo de usar o estacionamento j para o avião i
    [1000, 500, 500],          # Custos para Avião 0 nos Estacionamentos 0, 1, 2
    [1000, 500, 500],          # Custos para Avião 1 nos Estacionamentos 0, 1, 2
    [100,  500, 500]           # Custos para Avião 2 nos Estacionamentos 0, 1, 2 (Estac. 0 mais barato)
]

# Verificação de consistência básica
print("Verificando consistência dos parâmetros...")
# Adicionando verificação para garantir que cp_model foi importado antes de usar
if 'cp_model' not in globals():
    print("Erro crítico: Módulo cp_model não carregado. Verifique a instalação do ortools.")
    exit()

if len(momento_de_chegada) != total_avioes or len(tempo_duracao) != total_avioes or len(custos) != total_avioes:
    raise ValueError("Listas de chegada, duração ou custos não correspondem ao total de aviões.")
for i in range(total_avioes):
    if len(custos[i]) != total_estacionamentos:
        raise ValueError(f"Lista de custos para avião {i} não corresponde ao total de estacionamentos.")
    if tempo_duracao[i] < 0:
         raise ValueError(f"Duração para avião {i} ({tempo_duracao[i]}) não pode ser negativa.")
    if tempo_duracao[i] > total_tempo:
         raise ValueError(f"Duração para avião {i} ({tempo_duracao[i]}) excede o tempo total ({total_tempo}).")
    if momento_de_chegada[i] < 0:
         raise ValueError(f"Momento de chegada para avião {i} ({momento_de_chegada[i]}) não pode ser negativo.")
    # Ajuste na verificação: Se a duração é positiva, a chegada + duração deve caber.
    if tempo_duracao[i] > 0 and momento_de_chegada[i] + tempo_duracao[i] > total_tempo:
         print(f"Aviso: Avião {i} pode não conseguir completar sua duração ({tempo_duracao[i]}) se chegar no tempo {momento_de_chegada[i]} dentro do tempo total {total_tempo}.")


# --- Inicialização do Modelo ---
print("Inicializando o modelo CP-SAT...")
modelo = cp_model.CpModel()
solucionador = cp_model.CpSolver()
variaveis_a_logar = [] # Reseta a lista de log

# --- Variáveis de Decisão ---
print("Criando variáveis de decisão X e Y...")
# X[i][j][k] = 1 se avião i está no estacionamento j no tempo k, 0 caso contrário
X = [[[modelo.NewBoolVar(f'X_av{i}_est{j}_t{k}')
      for k in range(total_tempo)]
      for j in range(total_estacionamentos)]
      for i in range(total_avioes)]

# Y[i][j] = 1 se avião i USA o estacionamento j em ALGUM momento, 0 caso contrário
# (Variável auxiliar para custo e restrição de não-troca)
# No notebook, Y era criado dentro do loop de restrição, aqui criamos antes.
Y = [[modelo.NewBoolVar(f'Y_av{i}_usa_est{j}')
      for j in range(total_estacionamentos)]
      for i in range(total_avioes)]


# --- Restrições ---

# 1. Ocupação Máxima do Estacionamento: No máximo 1 avião por estacionamento por tempo.
print("Adicionando restrição: Ocupação Máxima do Estacionamento...")
for j in range(total_estacionamentos):
  for k in range(total_tempo):
    avioes_nesse_momento = [X[i][j][k] for i in range(total_avioes)]
    modelo.Add(sum(avioes_nesse_momento) <= 1)

# 2. Duração Exata da Estadia: Cada avião deve ficar estacionado EXATAMENTE pelo tempo definido.
print("Adicionando restrição: Duração Exata da Estadia...")
for i in range(total_avioes):
  tudo_do_aviao = [X[i][j][k] for j in range(total_estacionamentos) for k in range(total_tempo)]
  modelo.Add(sum(tudo_do_aviao) == tempo_duracao[i])
  # A restrição ">= 1" do notebook é redundante se a duração for > 0.
  # Se duração for 0, esta restrição já força a soma a ser 0.

# 3. Não Trocar de Estacionamento: Se um avião usa um estacionamento (Y[i][j]=1), ele só usa aquele.
print("Adicionando restrição: Não Trocar de Estacionamento...")
for i in range(total_avioes):
  # Garante que no máximo um Y[i][j] seja verdadeiro por avião
  # Se tempo_duracao[i] > 0, será exatamente 1 pela restrição de duração. Se tempo_duracao[i] == 0, será 0.
  modelo.Add(sum(Y[i]) <= 1)

  for j in range(total_estacionamentos):
    # Liga Y[i][j] a X[i][j][k]: (Usando a lógica do notebook)
    # Se o avião i usou o estacionamento j (Y[i][j]=1), então a soma de X[i][j][k] > 0
    # Se o avião i NÃO usou o estacionamento j (Y[i][j]=0), então a soma de X[i][j][k] == 0
    variaveis_aviao_neste_estacionamento = [X[i][j][k] for k in range(total_tempo)]
    modelo.Add(sum(variaveis_aviao_neste_estacionamento) > 0).OnlyEnforceIf(Y[i][j])
    modelo.Add(sum(variaveis_aviao_neste_estacionamento) == 0).OnlyEnforceIf(Y[i][j].Not())

    # Lógica adicional do notebook para garantir exclusividade (já coberta por sum(Y[i]) <= 1, mas mantida para fidelidade)
    # aviao_i_em_outro_sem_ser_j = modelo.NewBoolVar(f'aviao_{i}_em_outro_sem_ser_{j}')
    # variaveis_outros_estacionamentos = [X[i][outro_estacionamento][k] for k in range(total_tempo) for outro_estacionamento in range(total_estacionamentos) if outro_estacionamento != j]
    # modelo.Add(sum(variaveis_outros_estacionamentos) > 0).OnlyEnforceIf(aviao_i_em_outro_sem_ser_j)
    # modelo.Add(sum(variaveis_outros_estacionamentos) == 0).OnlyEnforceIf(aviao_i_em_outro_sem_ser_j.Not())
    # modelo.AddImplication(Y[i][j], aviao_i_em_outro_sem_ser_j.Not())


# 4. Continuidade e Não Retorno (Lógica de Decolagem): Se avião sai do estac. j, não volta para j.
print("Adicionando restrição: Continuidade (Não Retorno após Decolagem)...")
for i in range(total_avioes):
  for j in range(total_estacionamentos):
    for k in range(1, total_tempo): # Começa de k=1 para poder olhar k-1
      # Variável auxiliar: avião i decolou do estac j entre k-1 e k?
      se_aviao_decolou = modelo.NewBoolVar(f'av{i}_est{j}_t{k}_decolou')
      # loga(se_aviao_decolou) # Descomente se quiser logar

      # Define se_aviao_decolou: X[i][j][k-1] == 1 AND X[i][j][k] == 0
      # Usando a forma do notebook: sum([X[i][j][k-1], X[i][j][k].Not()]) == 2
      modelo.Add(X[i][j][k-1] + (1 - X[i][j][k]) == 2).OnlyEnforceIf(se_aviao_decolou)
      modelo.Add(X[i][j][k-1] + (1 - X[i][j][k]) != 2).OnlyEnforceIf(se_aviao_decolou.Not())

      # Se decolou é verdadeiro, então X[i][j][futuro] deve ser 0 para todo futuro >= k
      # O notebook usava k+1, mas para garantir não retorno *neste* estacionamento, deve incluir k.
      # No entanto, para garantir *continuidade* (não poder sair e voltar no mesmo k), k+1 está correto.
      # Vamos manter k+1 como no notebook original.
      for futuro in range(k + 1, total_tempo):
        modelo.AddImplication(se_aviao_decolou, X[i][j][futuro].Not())

# 5. Horário Mínimo de Chegada: Avião não pode estar estacionado ANTES do seu momento_de_chegada.
print("Adicionando restrição: Horário Mínimo de Chegada...")
for i in range(total_avioes):
  momento_de_chegada_dele = momento_de_chegada[i]
  if momento_de_chegada_dele > 0: # Só precisa adicionar se não for 0
    for j in range(total_estacionamentos):
      for k in range(momento_de_chegada_dele):
        modelo.Add(X[i][j][k] == 0)

# 6. Chegada Exata (se duração > 0): O avião DEVE estar em UM estacionamento EXATAMENTE no seu momento_de_chegada.
print("Adicionando restrição: Chegada Exata...")
for i in range(total_avioes):
  if tempo_duracao[i] > 0: # Só se aplica se o avião realmente for ficar estacionado
    momento_de_chegada_dele = momento_de_chegada[i]
    if momento_de_chegada_dele < total_tempo: # Garante que o tempo de chegada está dentro do horizonte
        avioes_no_momento_chegada = [X[i][j][momento_de_chegada_dele] for j in range(total_estacionamentos)]
        modelo.Add(sum(avioes_no_momento_chegada) == 1)
    else:
        # Se o momento de chegada for >= total_tempo e a duração > 0, é inviável.
        print(f"Erro nos parâmetros: Avião {i} tem duração {tempo_duracao[i]} mas chega em {momento_de_chegada_dele}, que é >= tempo total {total_tempo}.")
        # Forçar inviabilidade explicitamente (opcional, o solver já faria)
        modelo.Add(1==0) # Adiciona uma contradição


# --- Função Objetivo ---
# Minimizar o custo total, baseado em qual estacionamento (Y[i][j]) cada avião utilizou.
print("Definindo Função Objetivo: Minimizar Custo Total...")
custo_total_expr = []
for i in range(total_avioes):
    for j in range(total_estacionamentos):
        custo_total_expr.append(custos[i][j] * Y[i][j])

modelo.Minimize(sum(custo_total_expr))

# --- Resolução ---
# A chamada para resolve agora precisa dos custos também
resolve(solucionador, modelo, X, Y, custos, total_avioes, total_estacionamentos, total_tempo)

# --- Exemplo de como rodar com os parâmetros 12x5x24 ---
# Você precisaria definir:
# total_avioes = 12
# total_estacionamentos = 5
# total_tempo = 24
# momento_de_chegada = [ ... ] # Lista com 12 tempos de chegada
# tempo_duracao = [ ... ]    # Lista com 12 durações
# custos = [ [ ... ], [ ... ], ... ] # Lista de 12 listas, cada uma com 5 custos
# E então rodar o script novamente (após garantir que 'ortools' está instalado).

print("\nExecução do script concluída.")
