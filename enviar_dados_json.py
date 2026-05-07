import requests
import json

# 1. Use o endereço LOCAL se estiver no VS Code com a API ligada
# Se for usar no Colab, troque para a URL do Ngrok
URL_API = "http://127.0.0.1:8000/prever_rastreio_geo"

# 2. enviar dados json
dados_navio = { #exemplo
    "sealine": "Maersk",
    "size_type": "40' High Cube Dry",
    "timestamp_utc": "2025-07-27T00:25:00+00:00",
    "event_desc": "Load",
    "port_name": "Santos",
    "current_lat": -23.96083,
    "current_lon": -46.33361,
    "dest_lat": -3.10194,
    "dest_lon": -60.025
}

def enviar_teste_geo():
    try:
        print(f"🚀 Enviando dados para o modelo GEO em: {URL_API}")
        
        # O segredo: passamos 'json=dados_navio' para que o requests
        # converta o dicionário no formato que a API entende.
        response = requests.post(URL_API, json=dados_navio)

        if response.status_code == 200:
            resultado = response.json()
            print("\n✅ Sucesso!")
            print(f"🔮 Resultado da Previsão: {resultado.get('previsao')}")
        else:
            print(f"\n❌ Erro na API (Status {response.status_code})")
            print(f"Detalhe do erro: {response.text}")

    except Exception as e:
        print(f"\n❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    enviar_teste_geo()