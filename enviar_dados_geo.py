import requests
import json

# URL da sua API local
url = "http://127.0.0.1:8000/prever_rastreio_geo"

# Dados de exemplo do Conjunto 2 (Idênticos ao sucesso do teste local)
dados_navio = {
    "sealine": "Evergreen",
    "size_type": "20' Dry Standard",
    "timestamp_utc": "2025-05-26T16:00:00+00:00",
    "event_desc": "Empty pick-up by merchant haulage",
    "port_name": "Kaohsiung",
    "current_lat": 22.61626,
    "current_lon": 120.31333,
    "dest_lat": -26.90778,
    "dest_lon": -48.66194
}

try:
    print("🚀 Enviando dados para a API...")
    response = requests.post(url, json=dados_navio)
    
    if response.status_code == 200:
        resultado = response.json()
        print("\n================ RESPOSTA DA API ================")
        print("✅ Sucesso!")
        print(f"🤖 Versão utilizada: {resultado.get('modelo_versao')}")
        # Ajustado para ler a nova chave do api.py
        print(f"⏱️ Tempo restante estimado: {resultado['previsao_horas_restantes']:.2f} horas")
        print("=================================================")
    else:
        print(f"\n❌ Erro na API: {response.status_code}")
        print(response.json())
        
except Exception as e:
    print(f"\n❌ Falha ao conectar na API: {e}")