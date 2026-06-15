# Documentação da API de Previsão Logística e Rastreamento

---

##  Arquitetura do Sistema e Modelos

A API gerencia e centraliza a execução de dois pipelines de Machine Learning:

### 1. Modelo de Desembaraço/Situação (Modelo 1)
* **Objetivo:** Prever o tempo de resolução/status do processo logístico com base no fluxo alfandegário.
* **Algoritmo:** XGBoost Classifier/Regressor.
* **Regra de Negócio:** Calcula o target através da relação temporal entre a **Data Criação** e a **Data Presença Carga**.
* **Tipo de Entrada:** JSON estruturado com dados de auditoria e datas em formato timestamp (Unix).

### 2. Modelo de Rastreio Geográfico V2 (Modelo 2)
* **Objetivo:** Prever o tempo restante de viagem (em horas) de um navio até o porto de destino.
* **Algoritmo:** XGBoost treinado via Google Colab.
* **Engenharia de Recursos Integrada:**
  * Cálculo matemático de distância física via **Fórmula de Haversine** vetorizada em tempo de execução.
  * Mapeamento dinâmico de variáveis categóricas de texto para numéricas usando dicionário de `LabelEncoders` (`le_dict`) persistido.

---

##  Estrutura de Arquivos de Teste (`/projeto_previsao`)

Para validar a integridade dos endpoints locais ou remotos, o projeto conta com 4 scripts de automação de requisições utilizando a biblioteca `requests`:

| Script de Teste | Endpoint Alvo | Formato do Payload | Objetivo do Teste |
| :--- | :--- | :--- | :--- |
| `enviar_dados_json.py` | `/prever_situacao_json` | JSON (`dict`) | Valida a predição individual do **Modelo 1** usando parâmetros de consulta (`?modelo_escolhido=xgboost`). |
| `enviar_dados_geo.py` | `/prever_rastreio_geo` | JSON (`dict`) | Valida o pipeline completo do **Modelo 2** (Haversine + Encoders + Predição de horas). |
| `enviar_dados_excel.py` | Rota de Lote / Excel | `.xlsx` / `.csv` | Valida o processamento em lote de múltiplas linhas de dados logísticos de uma vez só. |
| `enviar_dados.py` | Rota Padrão / Legada | JSON genérico | Script auxiliar para testes rápidos de conectividade e sanidade da API. |

---

##  Documentação dos Endpoints Principais

### 1. Previsão de Situação (JSON)
Retorna a estimativa de dias para o fluxo do processo logístico/alfandegário.

* **Método:** `POST`
* **Rota:** `/prever_situacao_json`
* **Query Parameters:** `modelo_escolhido=xgboost`
* **Payload Exemplo (`body`):**
```json
{
    "Ano": 2023,
    "Processo": 2701,
    "Modal": "AEREO",
    "safra_semana": null,
    "Safra_mes": 1677628800000,
    "Data Cria\\u00e7ao": 1679356800000,
    "Origem": "BANGALORE",
    "Destino": "GUARULHOS",
    "Data Embarque": 1678406400000,
    "Agente de Carga": "QATAR AIRWAYS(Q.C.S.C)",
    "Data Chegada": 1681603200000,
    "Data DI": 1681948800000,
    "Data CI": 1681948800000,
    "Data Desembara\\u00e7o": 1681948800000,
    "EntregaPrevista": 1681603200000,
    "DataEntrega": 1681948800000,
    "Prioridade": 1681989720000,
    "Chegada": 1681603200000,
    "Data Presen\\u00e7a Carga": null,
    "Data Libera\\u00e7\\u00e3o": 1681948800000,
    "Canal": "Verde"
}

```
### 2. Previsão de Situação (JSON)
Retorna a estimativa de dias para o fluxo do processo logístico/alfandegário.

* **Método:** `POST`
* **Rota:** `/prever_rastreio_geo`
* **Query Parameters:** `modelo_escolhido=xgboost`
* **Payload Exemplo (`body`):**
```json

{
    "sealine": "Evergreen",
    "size_type": "20' Dry Standard",
    "timestamp_utc": "2025-05-26T16:00:00+00:00",
    "event_desc": "Empty pick-up by merchant haulage",
    "port_name": "Kaohsiung",
    "current_lat": 22.61626,
    "current_lon": 120.31333,
    "dest_lat": -26.90778,
    "dest_lon": -48.66194
}
```
##  Como Executar e Testar

### 1. Iniciar o Servidor da API
Certifique-se de estar com o ambiente virtual ativado (`venv`) e execute o Uvicorn apontando para o seu arquivo de entrada:
```bash
uvicorn api:app --reload
python enviar_dados_json.py
python enviar_dados_geo.py