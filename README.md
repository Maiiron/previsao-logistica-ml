# Sistema de Previsão Logística v2.3

Este projeto utiliza Inteligência Artificial para prever o tempo de presença (em dias) de cargas logísticas. A solução conta com uma API robusta (FastAPI) e um script de automação para processamento em lote.

## 📂 Estrutura do Projeto

* `api.py`: Servidor principal que expõe os modelos de IA via HTTP.
* `processamento.py`: Lógica de limpeza e preparação dos dados do Excel.
* `enviar_dados.py`: Script de automação (Payload) para enviar arquivos para a API.
* `modelo_random_forest.joblib` & `modelo_xgboost.joblib`: Modelos treinados.
* `dados.xlsx`: Exemplo de tabela de entrada.
* `requirements.txt`: Lista de bibliotecas necessárias.

---

## ⚠️ Observação Importante: Endereço da API (Ngrok)

Como o sistema utiliza o **Ngrok** na versão gratuita, a URL de conexão (`https://...ngrok-free.dev`) é **temporária**.

1.  **Se o Servidor for reiniciado:** O Ngrok gerará um novo link.
2.  **Ação Necessária:** Sempre que iniciar o projeto, você deve copiar a nova URL gerada no terminal do Ngrok e colá-la na variável `URL_API` dentro do arquivo `enviar_dados.py`.
3.  **Para o Usuário Externo:** O script cliente só funcionará se o servidor (seu PC) estiver ligado e com o túnel do Ngrok ativo.

---
---

## 🛠️ Como Configurar o Ambiente

1. **Python 3.10+** instalado.
2. **Ambiente Virtual (VENV):**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate

3. pip install -r requirements.txt

## Como usar

1. no api.py rodar o comando "uvicorn api:app --host 0.0.0.0 --port 8000"
2. em um segundo terminal rodar "ngrok http 8000"
3. configurar o arquivo "enviar_dados.py"
    Na variável URL_API, cole o link que você copiou do Ngrok.

    Na variável ARQUIVO_ENTRADA, coloque o nome do seu Excel (ex: dados.xlsx).

    Na variável MODELO, escolha entre "xgboost" ou "random_forest".

para executar basta rodar "python enviar_dados.py" em outro terminal
