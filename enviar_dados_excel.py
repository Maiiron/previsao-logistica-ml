# esse gera um novo excel com os resultados

import requests
import pandas as pd

# --- CONFIGURAÇÕES ---
# Ajustado para localhost para o seu teste local atual
URL_API = "http://127.0.0.1:8000" 
ARQUIVO_ENTRADA = "teste_micro_1.xlsx"
ARQUIVO_SAIDA = "previsoes_finais.xlsx"

# ====== ADICIONADO: CABEÇALHO DE SEGURANÇA ======
HEADERS_SEGURANCA = {
    "X-API-Key": "Cometrix123"  # <-- Mesma senha definida na API
}
# ================================================

def solicitar_previsao():
    print(f"🚀 Lendo arquivo: {ARQUIVO_ENTRADA}")
    
    try:
        # 1. Carregar o arquivo original para conferir as linhas
        df_original = pd.read_excel(ARQUIVO_ENTRADA)
        
        # 2. Enviar para a API
        with open(ARQUIVO_ENTRADA, "rb") as f:
            arquivos = {"file": (ARQUIVO_ENTRADA, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            dados = {"modelo_escolhido": "xgboost"}
            
            # ====== ALTERAÇÃO: Incluído o parâmetro headers=HEADERS_SEGURANCA ======
            response = requests.post(
                f"{URL_API}/prever_lote", 
                files=arquivos, 
                data=dados, 
                headers=HEADERS_SEGURANCA
            )
            # =======================================================================
        
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