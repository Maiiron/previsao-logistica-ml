import requests
import json

# URL da sua API local (ou o link do ngrok se estiver testando remotamente)
url = "http://127.0.0.1:8000/prever_rastreio_geo"

# Dados de exemplo (passa json)
dados_navio = {
    "sealine": "Maersk",
    "size_type": "40' High Cube Dry",
    "timestamp_utc": "2025-07-27T00:25:00+00:00",
    "event_desc": "Load",
    "port_name": "Santos",
    "current_lat": -23.9608,
    "current_lon": -46.3336,
    "dest_lat": -3.1019,
    "dest_lon": -60.0250
}

try:
    response = requests.post(url, json=dados_navio)
    if response.status_code == 200:
        print("✅ Sucesso!")
        print(f"Previsão do Modelo: {response.json()['previsao']}")
    else:
        print(f"❌ Erro na API: {response.status_code}")
        print(response.json())
except Exception as e:
    print(f"❌ Falha ao conectar na API: {e}")