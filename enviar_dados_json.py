import requests
import json

# 1. URL CORRIGIDA: Incluindo o parâmetro de consulta exigido pela API (modelo_escolhido=xgboost)
URL_API = "http://127.0.0.1:8000/prever_situacao_json?modelo_escolhido=xgboost"

HEADERS_SEGURANCA = {
    "X-API-Key": "Cometrix123"  # <-- Substitua pela senha que você definiu na API
}

# 2. Payload exato copiado do sucesso do seu Swagger
json_bruto_sucesso = """
{
    "Ano":2023,
        "Processo":3430,
        "Modal":"AEREO",
        "safra_semana":null,
        "Safra_mes":null,
        "Data Cria\u00e7ao":1681171200000,
        "Origem":"SINGAPORE",
        "Destino":"GUARULHOS",
        "Data Embarque":1681257600000,
        "Agente de Carga":"AIR FRANCE",
        "Data Chegada":1681862400000,
        "Data DI":1682294400000,
        "Data CI":1682294400000,
        "Data Desembara\u00e7o":1682353020000,
        "EntregaPrevista":1681862400000,
        "DataEntrega":1682380800000,
        "Prioridade":1682338620000,
        "Chegada":1681862400000,
        "Data Presen\u00e7a Carga":null,
        "Data Libera\u00e7\u00e3o":1682294400000,
        "Canal":"Verde"
}
"""

# Converte o bloco de texto JSON em um dicionário Python estruturado corretamente
dados_logistica = json.loads(json_bruto_sucesso)

def enviar_teste_logistica_json():
    try:
        print(f"🚀 Enviando dados JSON oficiais para o MODELO 1...")
        response = requests.post(URL_API, json=dados_logistica, headers=HEADERS_SEGURANCA)

        if response.status_code == 200:
            resultado = response.json()
            print("\n================ RESPOSTA DA API (MODELO 1) ================")
            print("✅ Sucesso!")
            print(f"📋 Status do Retorno: {resultado.get('status')}")
            # Ajustado para ler a chave real identificada na imagem: 'previsao_dias'
            print(f"⏱️ Previsão calculada pelo XGBoost: {resultado.get('previsao_days', resultado.get('previsao_dias'))} dias")
            print("============================================================")
        else:
            print(f"\n❌ Erro na API (Status {response.status_code})")
            print(f"Detalhe do erro: {response.text}")

    except Exception as e:
        print(f"\n❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    enviar_teste_logistica_json()