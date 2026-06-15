# Cometrix Realtime Shipment ETA Predictor (XGBoost Model)
Este repositório contém a documentação de produção e especificação do modelo final de Machine Learning baseado no algoritmo **XGBoost Regressor**. O modelo foi projetado para prever, em tempo real, o tempo restante (em horas) para que um contêiner chegue ao seu destino final com base no seu evento logístico mais recente.
## 🧠 O Modelo Final
Após rodar testes comparativos, o **XGBoost** foi selecionado como o modelo oficial de produção devido à sua altíssima precisão e excelente capacidade de generalização para rotas de transbordo complexas.
### Métricas de Performance:
* **MAE (Erro Médio Absoluto):** 91.42 horas (~3.8 dias)
* **RMSE (Raiz do Erro Quadrático Médio):** 149.23 horas
* **R² Score:** 0.9958 (o modelo explica 99.58% da variabilidade do tempo de tráfego)
---
## 📥 Contrato da API: Payload de Entrada (Request)
O modelo espera receber um objeto JSON representando o último evento de tracking gerado pelo contêiner.
### Estrutura do JSON:
| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `sealine` | String | Nome do armador / linha marítima | `"Evergreen"` |
| `size_type` | String | Tamanho e tipo do contêiner | `"20' Dry Standard"` |
| `timestamp_utc` | String | Data/Hora do evento no formato ISO 8601 | `"2025-05-26T16:00:00+00:00"` |
| `event_desc` | String | Descrição exata do status/evento logístico | `"Empty pick-up by merchant haulage"` |
| `port_name` | String | Nome do porto onde o evento ocorreu | `"Kaohsiung"` |
| `current_lat` | Float | Latitude atual do contêiner / porto atual | `22.61626` |
| `current_lon` | Float | Longitude atual do contêiner / porto atual | `120.31333` |
| `dest_lat` | Float | Latitude do porto de destino final | `-26.90778` |
| `dest_lon` | Float | Longitude do porto de destino final | `-48.66194` |
### Exemplo Prático de Payload:
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
---
## 📤 Contrato da API: Retorno (Response)
O modelo retorna o tempo estimado restante em **horas estruturadas em ponto flutuante (Float)**. Cabe à aplicação que consome o modelo converter esse valor para dias ou para uma data estimada final (ETA).
### Exemplo de Resposta:
```json
{
  "estimated_time_to_destination_hours": 1547.22
}
```
> **Nota de Negócio:** À medida que o contêiner avança na viagem (muda de latitude/longitude e atualiza o `event_desc`), o payload deve ser reenviado para que o modelo atualize dinamicamente as horas restantes (fazendo a contagem regressiva inteligente).
---
## ⚙️ O que acontece "Under the Hood" (Pré-processamento)
Antes do XGBoost realizar o cálculo final, o código de inferência pega o seu payload e faz as seguintes transformações *on-the-fly*:
1.  **Feature Engineering Temporal:** Quebra o `timestamp_utc` em `hour`, `day_of_week` e `month`.
2.  **Cálculo de Distância:** Utiliza a fórmula matemática de Haversine para transformar as 4 coordenadas geográficas (`current_lat`, `current_lon`, `dest_lat`, `dest_lon`) em uma única variável numérica: `destine_dist` (distância em quilômetros).
3.  **Encoding Categórico:** Transforma os textos (`sealine`, `size_type`, `event_desc`, `port_name`) em números utilizando os mapeamentos salvos no arquivo `.pkl`.
---
## 🚀 Como carregar e rodar em produção
Certifique-se de ter o arquivo de artefatos `shipment_predictor_v2.pkl` no mesmo diretório.
```python
import joblib
import pandas as pd
import numpy as np
# Carrega os componentes do XGBoost
saved_data = joblib.load('shipment_predictor_v2.pkl')
model = saved_data['classifier']
encoders = saved_data['encoders']
feature_cols = saved_data['features']
def predict_eta(payload):
    # Converte para DataFrame interno
    df_input = pd.DataFrame([payload])
    df_input['timestamp_utc'] = pd.to_datetime(df_input['timestamp_utc'])
    # Feature Engineering
    df_input['hour'] = df_input['timestamp_utc'].dt.hour
    df_input['day_of_week'] = df_input['timestamp_utc'].dt.dayofweek
    df_input['month'] = df_input['timestamp_utc'].dt.month
    # Haversine (Distância)
    lat1, lon1, lat2, lon2 = map(np.radians, [df_input['current_lat'], df_input['current_lon'], df_input['dest_lat'], df_input['dest_lon']])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    df_input['destine_dist'] = 2 * np.arcsin(np.sqrt(a)) * 6371
    # Label Encoding
    for col, le in encoders.items():
        df_input[col] = le.transform(df_input[col].astype(str))
    # Predição final com o XGBoost
    return float(model.predict(df_input[feature_cols])[0])
# Executando a predição
resultado = predict_eta(seu_payload_json)
print(f"Horas restantes até o destino: {resultado:.2f}")
```
