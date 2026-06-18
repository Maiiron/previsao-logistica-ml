import requests
import json

# 1. URL CORRIGIDA: Apontando para a rota geográfica da sua API
URL_API = "http://127.0.0.1:8000/prever_rastreio_geo"

# ====== ADICIONADO: CABEÇALHO DE SEGURANÇA ======
HEADERS_SEGURANCA = {
    "X-API-Key": "Cometrix123"  # <-- Mesma senha definida na API
}
# ================================================

# 2. Payload geográfico (Exemplo de coordenadas/rastreio do seu Swagger)
json_geo_sucesso = """
{
  "sealine": "Maersk",
  "size_type": "40' High Cube Dry",
  "timestamp_utc": "2025-08-19T00:56:00+00:00",
  "event_desc": "Vessel departure",
  "port_name": "Pecem",
  "current_lat": -3.54806,
  "current_lon": -38.82972,
  "dest_lat": -3.10194,
  "dest_lon": -60.025
}
"""
# Converte o bloco de texto JSON em um dicionário Python estruturado corretamente
dados_geo = json.loads(json_geo_sucesso)

def enviar_teste_logistica_geo():
    try:
        print(f"🚀 Enviando dados GEOGRÁFICOS oficiais para o MODELO 2...")
        
        # ====== ALTERAÇÃO: Incluído o parâmetro headers=HEADERS_SEGURANCA ======
        response = requests.post(URL_API, json=dados_geo, headers=HEADERS_SEGURANCA)
        # =======================================================================

        if response.status_code == 200:
            resultado = response.json()
            print("\n================ RESPOSTA DA API (MODELO 2 - GEO) ================")
            print("✅ Sucesso!")
            print(f"📋 Status do Retorno: {resultado.get('status', 'Sucesso')}")
            # Adapte as chaves abaixo caso o retorno do seu modelo geo use nomes diferentes
            print(f"⏱️ Previsão calculada via Geo/Haversine: {resultado.get('previsao_dias')} dias")
            print("==================================================================")
            # Para isso (mostra tudo que a API devolveu):
            print("DADOS BRUTOS DA API:", resultado)
            
        else:
            print(f"\n❌ Erro na API (Status {response.status_code})")
            print(f"Detalhe do erro: {response.text}")

    except Exception as e:
        print(f"\n❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    enviar_teste_logistica_geo()