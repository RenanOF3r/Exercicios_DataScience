# Análise: Imigração do Brasil para o Canadá (1980+)

Este repositório contém um notebook e materiais de apoio para analisar a evolução da imigração do **Brasil → Canadá** usando um dataset anual (1980 em diante).

## Conteúdo
- `analise_imigracao_brasil_canada.ipynb` — notebook com código e gráficos (matplotlib).
- `brasil_imigracao_canada_serie_1980+.csv` — série do Brasil em formato *tidy*.
- `brazil_canada_insights.txt` — resumo com números-chave.
- `brasil_*.png` — gráficos exportados (4 figuras).
- `imigrantes_canada.csv` — **(opcional)** dataset bruto por país (1980+). Inclua apenas se tiver direito de redistribuição.

## Requisitos
Veja `requirements.txt`. Recomendado usar um virtualenv:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Como rodar localmente
1. (Opcional) Coloque `imigrantes_canada.csv` na raiz do projeto.
2. Abra o Jupyter:
```bash
jupyter notebook
```
3. Execute as células do notebook.
4. Os gráficos e a série limpa serão gerados/atualizados na pasta raiz.

## Como publicar no GitHub (rápido)
**Via interface web (mais simples):**
1. Crie um repositório em https://github.com/new (nome sugerido: `imigracao-brasil-canada`).
2. No repositório, clique em **Add file → Upload files** e **arraste** os arquivos do projeto (notebook, CSV(s), PNGs, README, requirements, .gitignore).
3. Escreva uma mensagem de *commit* e clique em **Commit changes**.

**Via linha de comando (git):**
```bash
# dentro da pasta do projeto
git init
git add .
git commit -m "Análise: imigração Brasil → Canadá (1980+)"
git branch -M main

# crie o repositório no GitHub (via site) e copie a URL "origin" (HTTPS ou SSH)
git remote add origin https://github.com/SEU_USUARIO/imigracao-brasil-canada.git
git push -u origin main
```

> Dica: se usar HTTPS, o GitHub hoje pede Token de Acesso Pessoal (PAT). Em SSH, adicione sua chave pública à sua conta GitHub.

## Licença e dados
- Adicione uma licença (ex.: MIT) conforme a sua preferência.
- Verifique a permissão de **redistribuição** do dataset bruto antes de torná-lo público.
