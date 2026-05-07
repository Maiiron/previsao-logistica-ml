#esse gera um novo excel com os resultados

import requests
import pandas as pd

# --- CONFIGURAÇÕES ---
URL_API = "https://awilda-unfrayed-obliviously.ngrok-free.dev/" # link da pagina API
ARQUIVO_ENTRADA = "teste_micro_1.xlsx"
ARQUIVO_SAIDA = "previsoes_finais.xlsx"

def solicitar_previsao():
    print(f"🚀 Lendo arquivo: {ARQUIVO_ENTRADA}")
    
    try:
        # 1. Carregar o arquivo original para conferir as linhas
        df_original = pd.read_excel(ARQUIVO_ENTRADA)
        
        # 2. Enviar para a API
        with open(ARQUIVO_ENTRADA, "rb") as f:
            arquivos = {"file": (ARQUIVO_ENTRADA, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            dados = {"modelo_escolhido": "xgboost"}
            
            response = requests.post(f"{URL_API}/prever_lote", files=arquivos, data=dados)
        
        if response.status_code == 200:
            previsoes = response.json()["previsoes"]
            
            # 3. Criar uma nova coluna com as previsões
            df_original['Previsao_Data'] = previsoes
            
            # 4. Salvar um novo Excel com a resposta
            df_original.to_excel(ARQUIVO_SAIDA, index=False)
            
            print(f"✅ Sucesso! Gerado arquivo: {ARQUIVO_SAIDA}")
            print(f"📊 Foram processadas {len(previsoes)} linha(s).")
        else:
            print(f"❌ Erro na API: {response.text}")
            
    except Exception as e:
        print(f"❌ Falha: {e}")

if __name__ == "__main__":
    solicitar_previsao()