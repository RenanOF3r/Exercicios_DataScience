# Imigração do Brasil para o Canadá — Análises e Estrutura

Este repositório reúne uma análise exploratória da imigração do **Brasil → Canadá** (1980+),
com foco em **tendência**, **dinâmica anual**, **relevância relativa** e **estrutura do fluxo**.

## 🎯 Objetivo
Responder, com visualizações claras e replicáveis, às perguntas:
- Como a imigração do Brasil evoluiu ao longo do tempo?
- Em que momentos houve aceleração ou queda?
- Qual a **participação** do Brasil dentro do total?
- Como o Brasil se posiciona **entre outros países**?
- O fluxo total está **concentrado** em poucos países ou **diversificado**?



## 📁 Estrutura do projeto
```
.
├── imigracao_brasil_canada.ipynb                        # Notebook com gráficos embutidos
├── exports/                                             # PNGs gerados
│   ├── 01_brasil_imigrantes_por_ano.png
│   ├── 02_brasil_yoy_abs.png
│   ├── 03_brasil_participacao.png
│   ├── 04_brasil_acumulado.png
│   ├── 05_brasil_indice_base100.png
│   ├── 06_comparacao_paises.png
│   ├── 07_top10_YYYY_gradiente.png
│   ├── 08_ranking_brasil.png
│   ├── 09_cagr5_brasil.png
│   └── 10_hhi_vs_share.png
├── requirements.txt
├── LICENSE
└── README.md
```

> **Dados**: o notebook espera um arquivo `imigrantes_canada.csv` na raiz **apenas se você quiser reprocessar**.
> Para **visualizar**, basta abrir o notebook no GitHub ou consultar os PNGs em `exports/`.

## 👀 Como visualizar
- Abra `imigracao_brasil_canada.ipynb` diretamente no GitHub para ver os gráficos embutidos; **ou**
- navegue pela pasta `exports/` para ver as figuras em PNG.

## 🧪 Organização do notebook (o que cada seção faz e por que importa)

1) **Série anual do Brasil + MM5**  
   - **O que é**: linha com os imigrantes/ano e uma **média móvel de 5 anos**.  
   - **Por que importa**: revela **tendência estrutural** e **pontos de inflexão**.  
   - **Saída**: `exports/01_brasil_imigrantes_por_ano.png`.

2) **Variação ano a ano (Δ)**  
   - **O que é**: diferença absoluta entre anos consecutivos.  
   - **Por que importa**: destaca **acelerações** e **quedas** de curto prazo.  
   - **Saída**: `exports/02_brasil_yoy_abs.png`.

3) **Participação do Brasil (%) no total**  
   - **O que é**: share do Brasil no total de imigrantes para o Canadá.  
   - **Por que importa**: separa **crescimento próprio** de **crescimento do mercado**.  
   - **Saída**: `exports/03_brasil_participacao.png`.

4) **Acumulado desde 1980**  
   - **O que é**: soma do fluxo ao longo do período.  
   - **Por que importa**: mostra a **contribuição total** do Brasil nas décadas.  
   - **Saída**: `exports/04_brasil_acumulado.png`.

5) **Índice (base ≈ 100 no primeiro valor)**  
   - **O que é**: normaliza a série para evidenciar **crescimento relativo**.  
   - **Por que importa**: remove o efeito do nível inicial; facilita comparação proporcional.  
   - **Saída**: `exports/05_brasil_indice_base100.png`.

6) **Comparação entre países (Brasil × Argentina × China × Índia)**  
   - **O que é**: séries dos países selecionados.  
   - **Por que importa**: traz **escala** e **dinâmica relativa** no contexto internacional.  
   - **Saída**: `exports/06_comparacao_paises.png`.

7) **Top 10 do ano mais recente (degradê amarelo → laranja)**  
   - **O que é**: ranking anual com coloração contínua do **menor** (amarelo) ao **maior** (laranja).  
   - **Por que importa**: evidencia **liderança** e **distâncias** no último ano da série.  
   - **Saída**: `exports/07_top10_YYYY_gradiente.png`.

8) **Ranking anual do Brasil (1 = maior fluxo)**  
   - **O que é**: posição do Brasil entre todos os países a cada ano (eixo invertido: 1 no topo).  
   - **Por que importa**: mede **competitividade relativa** e mudanças de patamar.  
   - **Saída**: `exports/08_ranking_brasil.png`.

9) **Crescimento composto móvel (CAGR 5 anos)**  
   - **O que é**: taxa composta de crescimento em janelas deslizantes de 5 anos.  
   - **Por que importa**: identifica **períodos sustentados** de expansão/contração.  
   - **Saída**: `exports/09_cagr5_brasil.png`.  
   - **Fórmula**: \( \text{CAGR}_{5Y}(t) = \left(\frac{X_t}{X_{t-5}}\right)^{1/5} - 1 \).

10) **Concentração (HHI) do total × Participação do Brasil**  
    - **O que é**: **HHI** (soma dos quadrados das participações por país, ano a ano) e a participação do Brasil na mesma escala.  
    - **Por que importa**: avalia se ganhos do Brasil ocorrem num **mercado concentrado** ou **disperso**.  
    - **Saída**: `exports/10_hhi_vs_share.png`.  
    - **Fórmula**: \( \text{HHI} = \sum_i s_i^2 \), onde \( s_i \) é o share do país *i* no ano.

## 🧠 Metodologia e cuidados
- Leitura robusta do CSV (encodings comuns).
- Detecção automática de coluna de país e colunas de anos.
- Exclusão de linhas agregadas (ex.: **Total/World**) em ranking e HHI.
- Uso de **MM5**, **CAGR 5Y** e **índice base** para leitura de tendência e crescimento relativo.
- Paleta consistente para melhorar contraste e leitura.

## 📄 Licença
Código sob **MIT** (veja `LICENSE`).  
Verifique a **licença dos dados** antes de publicar o CSV em repositório público.


## 🖼️ Pré-visualização rápida

<p align="center">
  <img src="exports/01_brasil_imigrantes_por_ano.png" alt="01 brasil imigrantes por ano" width="300" style="margin:6px;" />
  <img src="exports/02_brasil_yoy_abs.png" alt="02 brasil yoy abs" width="300" style="margin:6px;" />
  <img src="exports/03_brasil_participacao.png" alt="03 brasil participacao" width="300" style="margin:6px;" />
</p>

<p align="center">
  <img src="exports/04_brasil_acumulado.png" alt="04 brasil acumulado" width="300" style="margin:6px;" />
  <img src="exports/05_brasil_indice_base100.png" alt="05 brasil indice base100" width="300" style="margin:6px;" />
  <img src="exports/06_comparacao_paises.png" alt="06 comparacao paises" width="300" style="margin:6px;" />
</p>

<p align="center">
  <img src="exports/07_top10_2013_gradiente.png" alt="07 top10 2013 gradiente" width="300" style="margin:6px;" />
  <img src="exports/08_ranking_brasil.png" alt="08 ranking brasil" width="300" style="margin:6px;" />
  <img src="exports/09_cagr5_brasil.png" alt="09 cagr5 brasil" width="300" style="margin:6px;" />
</p>

<p align="center">
  <img src="exports/10_hhi_vs_share.png" alt="10 hhi vs share" width="300" style="margin:6px;" />
</p>

