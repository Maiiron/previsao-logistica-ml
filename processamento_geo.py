import joblib
import pandas as pd
import numpy as np

# 1. CARREGAR OS ARTEFATOS DO NOVO MODELO V2
# Carrega o dicionário estruturado no Colab que contém o modelo, os encoders e as features
ARQUIVO_MODELO = 'shipment_predictor_v2.pkl'

try:
    model_data = joblib.load(ARQUIVO_MODELO)
    modelo_xgb = model_data['classifier']
    le_dict = model_data['encoders']
    features_ordem = model_data['features']
    print("✅ [processamento_geo] Modelo V2 e LabelEncoders carregados com sucesso!")
except FileNotFoundError:
    print(f"❌ [processamento_geo] Erro: Arquivo '{ARQUIVO_MODELO}' não encontrado. Verifique a pasta.")
    modelo_xgb, le_dict, features_ordem = None, None, None


# 2. FÓRMULA DE HAVERSINE VETORIZADA (Substituindo o antigo Geopy)
def haversine_vectorized(lat1, lon1, lat2, lon2):
    """
    Calcula a distância em quilômetros entre duas coordenadas geográficas
    utilizando a fórmula matemática de Haversine (idêntica ao treino no Colab).
    """
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # Raio da Terra em km
    return c * r


# 3. FUNÇÃO PRINCIPAL QUE A API VAI CHAMAR
def preparar_dados_para_shipment(dados_json):
    """
    Transforma o JSON recebido pela API no DataFrame numérico exato
    que o novo modelo treinado no Colab espera receber.
    """
    if modelo_xgb is None:
        raise RuntimeError("O modelo V2 não foi carregado corretamente na inicialização.")

    # Converte o dicionário (JSON) recebido em um DataFrame de 1 linha
    df = pd.DataFrame([dados_json])
    
    # 3.1. Engenharia de Recursos Temporais
    ts = pd.to_datetime(df['timestamp_utc'])
    df['hour'] = ts.dt.hour
    df['day_of_week'] = ts.dt.dayofweek
    df['month'] = ts.dt.month
    
    # 3.2. Cálculo da Distância Física via Haversine
    df['destine_dist'] = haversine_vectorized(
        df['current_lat'], df['current_lon'], 
        df['dest_lat'], df['dest_lon']
    )
    
    # 3.3. Aplicação dos LabelEncoders salvos (Mapeamento de Texto para Número)
    categorical_cols = ['sealine', 'size_type', 'event_desc', 'port_name']
    for col in categorical_cols:
        le = le_dict[col]
        
        # Tratamento de segurança: se a API receber um texto desconhecido que não estava 
        # no treino do Colab, mapeia temporariamente para a primeira classe conhecida 
        # para evitar que o transform quebre a execução.
        df[col] = df[col].map(lambda s: s if s in le.classes_ else le.classes_[0])
        
        # Aplica a transformação numérica do LabelEncoder
        df[col] = le.transform(df[col].astype(str))
        
    # 3.4. Filtragem e Ordenação das colunas com base no arquivo do Colab
    X_input = df[features_ordem]
    
    return X_input, modelo_xgb