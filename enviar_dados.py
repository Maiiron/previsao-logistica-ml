import requests
import pandas as pd

# --- CONFIGURAÇÕES ---
# Toda vez que você ligar o ngrok, mude APENAS esta URL abaixo:
URL_API = "https://awilda-unfrayed-obliviously.ngrok-free.dev/" 
# colocar arquivo a ser lido
ARQUIVO_ENTRADA = "ExemploT1.xlsx"
MODELO =  "random_forest"     #"xgboost"  # ou "random_forest"

def solicitar_previsao():
    print(f"🚀 Conectando à API em: {URL_API}")
    
    try:
        # Abre o arquivo Excel para envio
        with open(ARQUIVO_ENTRADA, "rb") as f:
            arquivos = {"file": (ARQUIVO_ENTRADA, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            dados = {"modelo_escolhido": MODELO}
            
            # Envia para a rota
            response = requests.post(f"{URL_API}/prever_lote", files=arquivos, data=dados)
        
        if response.status_code == 200:
            previsoes = response.json()["previsoes"]
            print(f"✅ Previsão recebida com sucesso!")
            print(f"📊 Resultados: {previsoes}")
            
            # Opcional: Salvar os resultados num CSV ou TXT local
            with open("resultados_ia.txt", "w") as res_file:
                res_file.write(str(previsoes))
        else:
            print(f"❌ Erro na API: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Falha ao conectar: {e}")

if __name__ == "__main__":
    solicitar_previsao()