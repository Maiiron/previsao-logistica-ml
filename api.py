# uvicorn api:app --reload
# uvicorn api:app --host 0.0.0.0 --port 8000
# ngrok http 8000

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from enum import Enum
import joblib
import pandas as pd
import io
import os
import xgboost as xgb
from processamento import preparar_excel_para_modelo

class OpcoesModelo(str, Enum):
    rf = "random_forest"
    xgb = "xgboost"

app = FastAPI(title="Sistema Logístico v2.3")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que qualquer script acesse
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carregamento seguro
modelos = {}
try:
    modelos["random_forest"] = joblib.load('modelo_random_forest.joblib')
    modelos["xgboost"] = joblib.load('modelo_xgboost.joblib')
except Exception as e:
    print(f"Erro ao carregar arquivos: {e}")

#mudança aqui
@app.post("/prever_lote", tags=["Previsão em Massa"])
async def prever_lote(
    file: UploadFile = File(...), 
    modelo_escolhido: OpcoesModelo = Form(OpcoesModelo.rf) # Adicionamos o Form() aqui!
):
    # 1. LOG DE SEGURANÇA (Para você ver no terminal se mudou mesmo)
    print(f"DEBUG: Recebido pedido com o modelo: {modelo_escolhido.value}")

    # 1. Leitura e Processamento
    conteudo = await file.read()
    df_original = pd.read_excel(io.BytesIO(conteudo))
    
    with open("temp_api.xlsx", "wb") as f:
        f.write(conteudo)
    
    X_processado = preparar_excel_para_modelo("temp_api.xlsx")
    
    # Busca o modelo no dicionário
    modelo = modelos[modelo_escolhido.value]
    previsoes = modelo.predict(X_processado)
    
    # 2. Preparar a lista de dias
    resultados_dias = [int(round(p)) for p in previsoes]
    
    # 3. Gerar e SALVAR o Excel
    df_original['Previsao_Dias_Presenca'] = resultados_dias
    nome_arquivo_saida = f"previsoes_{modelo_escolhido.value}.xlsx"
    df_original.to_excel(nome_arquivo_saida, index=False)

    return {
        "status": "Sucesso",
        "modelo_utilizado": modelo_escolhido.value,
        "arquivo_gerado": nome_arquivo_saida,
        "previsoes": resultados_dias
    }

@app.post("/prever_por_linha")
async def prever_por_linha(
    file: UploadFile = File(...),
    linha: int = Form(...),
    modelo_escolhido: OpcoesModelo = OpcoesModelo.rf
):
    try:
        conteudo = await file.read()
        df_completo = pd.read_excel(io.BytesIO(conteudo))

        # Ajuste de segurança: verifica se o índice existe
        if linha < 0 or linha >= len(df_completo):
            return JSONResponse(status_code=400, content={"erro": f"Linha {linha} inválida. O arquivo vai de 0 a {len(df_completo)-1}"})

        # Seleciona a linha e força a criação de um DataFrame
        df_linha = df_completo.iloc[[linha]].copy()
        
        # Nome temporário único para evitar erro de acesso simultâneo
        temp_name = f"temp_linha_{linha}.xlsx"
        df_linha.to_excel(temp_name, index=False)
        
        X_un = preparar_excel_para_modelo(temp_name)
        
        # Remove o arquivo temporário após processar
        if os.path.exists(temp_name):
            os.remove(temp_name)

        modelo = modelos[modelo_escolhido.value]
        pred = modelo.predict(X_un)
        
        return {
            "status": "Sucesso",
            "linha_analisada": linha,
            "previsao_dias": int(round(pred[0])),
            "detalhes_carga": df_linha.fillna("").to_dict(orient='records')[0]
        }
    except Exception as e:
        # Se der erro, ele vai printar o motivo real no seu terminal do VS Code
        print(f"ERRO INTERNO: {e}")
        return JSONResponse(status_code=500, content={"erro": "Erro no processamento", "detalhe": str(e)})