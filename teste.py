import joblib
import pandas as pd
import os
from processamento import preparar_excel_para_modelo

# 1. Configurar caminhos
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_modelo = os.path.join(diretorio_atual, 'modelo_random_forest.joblib')
caminho_excel = os.path.join(diretorio_atual, 'dados.xlsx') # Nome do seu arquivo

print(f"Procurando arquivo em: {caminho_excel}")

# 2. Carregar o modelo
if not os.path.exists(caminho_excel):
    print("ERRO: O arquivo 'dados.xlsx' não foi encontrado na pasta!")
else:
    try:
        modelo = joblib.load(caminho_modelo)
        
        # 3. Processar (Isso vai rodar sua função de datas e dummies)
        X_novo = preparar_excel_para_modelo(caminho_excel)
        
        # 4. Predição
        previsoes = modelo.predict(X_novo)
        
        print("\n--- TESTE CONCLUÍDO COM SUCESSO ---")
        print(f"Quantidade de previsões feitas: {len(previsoes)}")
        print("Primeiras 5 previsões:")
        print(previsoes[:5])
        
    except Exception as e:
        print(f"\nERRO DURANTE O PROCESSAMENTO: {e}")