import pandas as pd
import joblib
import os

# Carregar as colunas que o modelo espera (manual de instruções)
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_colunas = os.path.join(diretorio_atual, 'colunas_modelo.joblib')
features_treino = joblib.load(caminho_colunas)

def preparar_excel_para_modelo(caminho_excel):
    # 1. Ler o arquivo
    df = pd.read_excel(caminho_excel)
    
    # --- 2. CÁLCULOS DE DATAS ( CTRL+C / CTRL+V DO COLAB) ---
    # Convertendo para datetime para poder subtrair
    df['Data Criaçao'] = pd.to_datetime(df['Data Criaçao'])
    df['Data Chegada'] = pd.to_datetime(df['Data Chegada'])
    df['Data DI'] = pd.to_datetime(df['Data DI'])
    df['Data CI'] = pd.to_datetime(df['Data CI'])
    df['Data Desembaraço'] = pd.to_datetime(df['Data Desembaraço'])
    df['Data Embarque'] = pd.to_datetime(df['Data Embarque'])

    # Criando as mesmas colunas que você tinha no treino
    df['Tempo_entre_criacao_DI'] = (df['Data DI'] - df['Data Criaçao']).dt.days
    df['Tempo_entre_criacao_CI'] = (df['Data CI'] - df['Data Criaçao']).dt.days
    df['Tempo_entre_CI_DI'] = (df['Data CI'] - df['Data DI']).dt.days
    df['Tempo_entre_Criacao_desembaraco'] = (df['Data Desembaraço'] - df['Data Criaçao']).dt.days
    df['Tempo_entre_desembaraco_CI'] = (df['Data CI'] - df['Data Desembaraço']).dt.days
    df['Tempo_transito'] = (df['Data Embarque'] - df['Data Chegada']).dt.days
    df['Tempo_Criacao_Embarque'] = (df['Data Criaçao'] - df['Data Embarque']).dt.days

    # 3. Sazonalidade
    df['X_Mes_Chegada'] = df['Data Chegada'].dt.month.astype(str)
    df['X_Dia_Semana_Chegada'] = df['Data Chegada'].dt.dayofweek.astype(str)

    # 4. One-Hot Encoding (Transformar texto em colunas 0 e 1)
    colunas_categoricas = ['Modal', 'Origem', 'Destino', 'Agente de Carga', 'Canal', 'X_Dia_Semana_Chegada']
    df_processado = pd.get_dummies(df, columns=colunas_categoricas)

    # --- 5. O SEGREDO: REINDEXAR ---
    # Isso garante que o DF final tenha as 174 colunas, nem mais, nem menos
    for col in features_treino:
        if col not in df_processado.columns:
            df_processado[col] = 0
            
    # Ordena as colunas exatamente como o modelo espera
    X_final = df_processado[features_treino]
    
    return X_final