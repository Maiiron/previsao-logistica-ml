# uvicorn api:app --reload
# uvicorn api:app --host 0.0.0.0 --port 8000
# ngrok http 8000
#versão 3.2 - incluso Modelo 1 (previsao inicial) e Modelo 2 (Lat e Long)

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum
from typing import List, Dict
import joblib
import pandas as pd
import io
import os
import pickle
from xgboost import XGBRegressor  
from processamento import preparar_excel_para_modelo
import sys
import xgboost as xgb
from processamento_geo import preparar_dados_para_shipment # Importe a nova função

sys.modules['XGBRegressor'] = xgb.XGBRegressor

class OpcoesModelo(str, Enum):
    rf = "random_forest"
    xgb = "xgboost"

app = FastAPI(title="Sistema Logístico v3.2 - JSON & Excel Integrados")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carregamento seguro dos modelos
# MODELO. 1 Previsão Base()
modelos = {}
try:
    modelos["random_forest"] = joblib.load('modelo_random_forest.joblib')
    modelos["xgboost"] = joblib.load('modelo_xgboost.joblib')
except Exception as e:
    print(f"Erro ao carregar arquivos de modelo: {e}")

# BLOCO 2: Modelo de Rastreio GEO (Pickle)
# 2. Carregamento do Modelo Geográfico ()
try:
    # TENTATIVA: Carregamento via Joblib 
    raw_model = joblib.load('shipment_predictor_v1.pkl')
    modelos["shipment_geo"] = raw_model
    print("✅ Modelo Geográfico carregado com sucesso!")
except AttributeError as e:
    if "dtype" in str(e):
        print("⚠️ Erro de versão detectado. Tentando modo de compatibilidade...")
        # Se falhar o objeto inteiro, tentamos carregar apenas a 'inteligência'
        try:
            with open('shipment_predictor_v1.pkl', 'rb') as f:
                # O XGBoost tem uma função interna para tentar ler binários de pickle
                modelos["shipment_geo"] = pickle.load(f)
            print("✅ Modelo Geográfico carregado (via Pickle fallback)!")
        except:
            print("❌ Não foi possível carregar o modelo GEO devido a incompatibilidade de versão.")
except Exception as e:
    print(f"❌ Erro persistente no modelo GEO: {e}")

# ============================================================
# ROTAS JSON (SISTEMAS EXTERNOS)
# ============================================================

@app.post("/prever_lote_json", tags=["JSON"])
async def prever_lote_json(dados: List[Dict], modelo_escolhido: OpcoesModelo = OpcoesModelo.xgb):
    """Recebe uma lista de objetos JSON e processa o lote inteiro"""
    try:
        # 1. Converte JSON para DataFrame 'cru'
        df_entrada = pd.DataFrame(dados)
        
        # 2. Salva temporariamente (o processamento.py vai ler e limpar as datas)
        temp_name = "temp_lote_processo.xlsx"
        df_entrada.to_excel(temp_name, index=False)
        
        # 3. Chama função de processamento 
        X_processado = preparar_excel_para_modelo(temp_name)
        
        # 4. Predição
        modelo = modelos[modelo_escolhido.value]
        previsoes = modelo.predict(X_processado)
        
        if os.path.exists(temp_name):
            os.remove(temp_name)

        return {
            "status": "Sucesso",
            "modelo_utilizado": modelo_escolhido.value,
            "previsoes": [int(round(p)) for p in previsoes]
        }
    except Exception as e:
        print(f"Erro Interno JSON Lote: {e}")
        return JSONResponse(status_code=500, content={"erro": str(e)})

@app.post("/prever_situacao_json", tags=["JSON"])
async def prever_situacao_json(dados: Dict, modelo_escolhido: OpcoesModelo = OpcoesModelo.xgb):
    """Recebe um único objeto JSON para uma previsão rápida"""
    try:
        # Transforma um único dicionário em uma lista de um item para o DataFrame
        df_entrada = pd.DataFrame([dados])
        
        temp_name = "temp_unica_processo.xlsx"
        df_entrada.to_excel(temp_name, index=False)
        
        X_processado = preparar_excel_para_modelo(temp_name)
        modelo = modelos[modelo_escolhido.value]
        pred = modelo.predict(X_processado)
        
        if os.path.exists(temp_name):
            os.remove(temp_name)

        return {
            "status": "Sucesso",
            "previsao_dias": int(round(pred[0]))
        }
    except Exception as e:
        print(f"Erro Interno JSON Único: {e}")
        return JSONResponse(status_code=500, content={"erro": str(e)})

# ============================================================
# ROTAS EXCEL (MANTIDAS PARA COMPATIBILIDADE)
# ============================================================

@app.post("/prever_lote", tags=["Excel"])
async def prever_lote(file: UploadFile = File(...), modelo_escolhido: OpcoesModelo = Form(OpcoesModelo.rf)):
    conteudo = await file.read()
    with open("temp_api_excel.xlsx", "wb") as f:
        f.write(conteudo)
    
    X_processado = preparar_excel_para_modelo("temp_api_excel.xlsx")
    modelo = modelos[modelo_escolhido.value]
    previsoes = modelo.predict(X_processado)
    
    return {
        "status": "Sucesso",
        "previsoes": [int(round(p)) for p in previsoes]
    }

@app.post("/prever_por_linha", tags=["Excel"])
async def prever_por_linha(
    file: UploadFile = File(...),
    linha: int = Form(...),
    modelo_escolhido: OpcoesModelo = Form(OpcoesModelo.rf)
):
    """
    Mantém a funcionalidade original de prever uma linha específica 
    de um arquivo Excel enviado.
    """
    try:
        conteudo = await file.read()
        df_completo = pd.read_excel(io.BytesIO(conteudo))

        # Validação de segurança para o índice da linha
        if linha < 0 or linha >= len(df_completo):
            return JSONResponse(
                status_code=400, 
                content={"erro": f"Linha {linha} inválida. O arquivo vai de 0 a {len(df_completo)-1}"}
            )

        # Seleciona a linha específica
        df_linha = df_completo.iloc[[linha]].copy()
        
        # Nome temporário para processamento
        temp_name = f"temp_linha_excel_{linha}.xlsx"
        df_linha.to_excel(temp_name, index=False)
        
        # O seu processamento.py agora tratará as datas automaticamente se necessário
        X_un = preparar_excel_para_modelo(temp_name)
        
        if os.path.exists(temp_name):
            os.remove(temp_name)

        modelo = modelos[modelo_escolhido.value]
        pred = modelo.predict(X_un)
        
        return {
            "status": "Sucesso",
            "linha_analisada": linha,
            "previsao_dias": int(round(pred[0])),
            "detalhes_da_carga": df_linha.fillna("").to_dict(orient='records')[0]
        }
    except Exception as e:
        print(f"ERRO ROTA EXCEL INDIVIDUAL: {e}")
        return JSONResponse(status_code=500, content={"erro": str(e)})
    
# ============================================================
# ROTAS Geo (MANTIDAS PARA COMPATIBILIDADE)
# ============================================================
    
@app.post("/prever_rastreio_geo", tags=["Logística Avançada - GEO"])
async def prever_rastreio_geo(dados: Dict):
    try:
        conteudo_pkl = modelos["shipment_geo"]
        
        # 1. Extração correta baseada no seu DEBUG
        # O modelo real está guardado na chave 'classifier'
        modelo_real = conteudo_pkl['classifier']
        
        # 2. Processamento dos dados (via sua função no outro arquivo)
        df_processado = preparar_dados_para_shipment(dados)
        
        # 3. Predição
        predicao = modelo_real.predict(df_processado)
        
        return {
            "status": "Sucesso",
            "previsao": float(predicao[0])
        }
    except Exception as e:
        print(f"Erro na predição GEO: {e}")
        return JSONResponse(status_code=500, content={"erro": str(e)})