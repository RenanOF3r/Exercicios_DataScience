# Instalar bibliotecas necessárias
try:
    from ortools.sat.python import cp_model
except ModuleNotFoundError:
    print("Instale com: pip install ortools==9.7.2996 pandas==2.1.0")

def alocar_avioes(total_avioes, total_estacionamentos, total_tempo,
                  momento_de_chegada, tempo_duracao, custos):
    modelo = cp_model.CpModel()
    solucionador = cp_model.CpSolver()

    X = [[[modelo.NewBoolVar(f'X_av{i}_est{j}_t{k}')
          for k in range(total_tempo)]
          for j in range(total_estacionamentos)]
          for i in range(total_avioes)]

    Y = [[modelo.NewBoolVar(f'Y_av{i}_usa_est{j}')
          for j in range(total_estacionamentos)]
          for i in range(total_avioes)]

    for j in range(total_estacionamentos):
        for k in range(total_tempo):
            modelo.Add(sum(X[i][j][k] for i in range(total_avioes)) <= 1)

    for i in range(total_avioes):
        modelo.Add(sum(X[i][j][k] for j in range(total_estacionamentos)
                                  for k in range(total_tempo)) == tempo_duracao[i])
        modelo.Add(sum(Y[i]) <= 1)
        for j in range(total_estacionamentos):
            uso = [X[i][j][k] for k in range(total_tempo)]
            modelo.Add(sum(uso) > 0).OnlyEnforceIf(Y[i][j])
            modelo.Add(sum(uso) == 0).OnlyEnforceIf(Y[i][j].Not())
            for k in range(1, total_tempo):
                decolou = modelo.NewBoolVar(f'decolou_{i}_{j}_{k}')
                modelo.Add(X[i][j][k-1] + (1 - X[i][j][k]) == 2).OnlyEnforceIf(decolou)
                modelo.Add(X[i][j][k-1] + (1 - X[i][j][k]) != 2).OnlyEnforceIf(decolou.Not())
                for futuro in range(k+1, total_tempo):
                    modelo.AddImplication(decolou, X[i][j][futuro].Not())

    for i in range(total_avioes):
        for j in range(total_estacionamentos):
            for k in range(momento_de_chegada[i]):
                modelo.Add(X[i][j][k] == 0)
        if tempo_duracao[i] > 0 and momento_de_chegada[i] < total_tempo:
            modelo.Add(sum(X[i][j][momento_de_chegada[i]]
                           for j in range(total_estacionamentos)) == 1)

    modelo.Minimize(sum(custos[i][j] * Y[i][j]
                        for i in range(total_avioes)
                        for j in range(total_estacionamentos)))

    status = solucionador.Solve(modelo)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(f"Custo total: {solucionador.ObjectiveValue()}")
        for i in range(total_avioes):
            for j in range(total_estacionamentos):
                for k in range(total_tempo):
                    if solucionador.Value(X[i][j][k]) == 1:
                        print(f"Avião {i} no estac. {j} no tempo {k}")
    else:
        print("Nenhuma solução encontrada.")

# Exemplo pequeno (3 aviões, 3 estacs, 5 tempos)
print("Exemplo pequeno")
alocar_avioes(
    3,
    3,
    5,
    [1, 2, 0],
    [3, 3, 2],
    [
        [1000, 500, 500],
        [1000, 500, 500],
        [100,  500, 500]
    ]
)

# Exemplo grande (12 aviões, 5 estacs, 24 tempos)
print("\nExemplo grande")
alocar_avioes(
    12,
    5,
    24,
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    [3, 4, 5, 2, 3, 4, 2, 3, 2, 4, 3, 3],
    [[(i+j+1)*100 for j in range(5)] for i in range(12)]
)