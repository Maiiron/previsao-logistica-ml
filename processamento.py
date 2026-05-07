import pandas as pd
import joblib
import os

# Carregar as colunas que o modelo espera (manual de instruções)
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_colunas = os.path.join(diretorio_atual, 'colunas_modelo.joblib')
features_treino = joblib.load(caminho_colunas)

def tratar_datas_flexivel(df):
    """
    Tenta converter colunas para datetime, tratando tanto o formato Excel 
    quanto os milissegundos (timestamps) que vêm do JSON.
    """
    colunas_data = [
        'Data Criaçao', 'Data Chegada', 'Data DI', 'Data CI', 
        'Data Desembaraço', 'Data Embarque'
    ]
    
    for col in colunas_data:
        if col in df.columns:
            # Se a coluna for numérica (como o 1679356800000 do seu JSON)
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = pd.to_datetime(df[col], unit='ms', errors='coerce')
            else:
                # Se for string (formato DD/MM/AAAA do Excel)
                df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

def preparar_excel_para_modelo(caminho_excel):
    # 1. Ler o arquivo
    df = pd.read_excel(caminho_excel)
    
    # --- 2. TRATAMENTO FLEXÍVEL DE DATAS ---
    # Resolve o problema dos milissegundos antes de fazer as contas
    df = tratar_datas_flexivel(df)
    
    # --- 3. CÁLCULOS DE DATAS ---
    # Criando as mesmas colunas que você tinha no treino
    df['Tempo_entre_criacao_DI'] = (df['Data DI'] - df['Data Criaçao']).dt.days
    df['Tempo_entre_criacao_CI'] = (df['Data CI'] - df['Data Criaçao']).dt.days
    df['Tempo_entre_CI_DI'] = (df['Data CI'] - df['Data DI']).dt.days
    df['Tempo_entre_Criacao_desembaraco'] = (df['Data Desembaraço'] - df['Data Criaçao']).dt.days
    df['Tempo_entre_desembaraco_CI'] = (df['Data CI'] - df['Data Desembaraço']).dt.days
    df['Tempo_transito'] = (df['Data Embarque'] - df['Data Chegada']).dt.days
    df['Tempo_Criacao_Embarque'] = (df['Data Criaçao'] - df['Data Embarque']).dt.days

    # 4. Sazonalidade
    df['X_Mes_Chegada'] = df['Data Chegada'].dt.month.astype(str)
    df['X_Dia_Semana_Chegada'] = df['Data Chegada'].dt.dayofweek.astype(str)

    # 5. One-Hot Encoding
    colunas_categoricas = ['Modal', 'Origem', 'Destino', 'Agente de Carga', 'Canal', 'X_Dia_Semana_Chegada']
    df_processado = pd.get_dummies(df, columns=colunas_categoricas)

    # --- 6. O SEGREDO: REINDEXAR ---
    for col in features_treino:
        if col not in df_processado.columns:
            df_processado[col] = 0
            
    # Ordena as colunas exatamente como o modelo espera
    X_final = df_processado[features_treino]
    
    return X_final