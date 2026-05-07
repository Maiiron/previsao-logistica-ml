import pandas as pd
from geopy.distance import geodesic

def preparar_dados_para_shipment(dados_json):
    """
    Transforma o JSON bruto no DataFrame EXATO que o modelo 
    shipment_predictor_v1 espera (nomes em inglês e ordem específica).
    """
    df = pd.DataFrame([dados_json])
    
    # 1. Tratamento do Tempo (Usando os nomes que o modelo pediu no erro)
    ts = pd.to_datetime(df['timestamp_utc'])
    df['hour'] = ts.dt.hour
    df['day_of_week'] = ts.dt.dayofweek
    df['month'] = ts.dt.month
    
    # 2. Cálculo de Distância Geográfica (destine_dist)
    # O modelo espera essa coluna em vez das latitudes/longitudes soltas
    def calcular_distancia(row):
        ponto_atual = (row['current_lat'], row['current_lon'])
        ponto_destino = (row['dest_lat'], row['dest_lon'])
        return geodesic(ponto_atual, ponto_destino).km

    df['destine_dist'] = df.apply(calcular_distancia, axis=1)
    
    # 3. Conversão para Categoria (Para as colunas de texto)
    colunas_categoricas = ["sealine", "size_type", "event_desc", "port_name"]
    for col in colunas_categoricas:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # 4. ORDEM DAS COLUNAS (O SEGREDO FINAL)
    # O XGBoost exige que as colunas entrem na MESMA ordem do treino.
    # Baseado no erro do Swagger, a ordem deve ser esta:
    colunas_finais = [
        'hour', 'day_of_week', 'month', 'destine_dist', 
        'sealine', 'size_type', 'event_desc', 'port_name'
    ]
    
    # Filtramos apenas as colunas necessárias e na ordem certa
    return df[colunas_finais]