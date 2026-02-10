# ativacao: uvicorn api:app --reload
# /docs

from fastapi import FastAPI, UploadFile, File
import joblib
import pandas as pd
import io
from processamento import preparar_excel_para_modelo

app = FastAPI(title="API de Previsão de Carga")

# Carregamos o modelo uma única vez quando a API sobe
modelo = joblib.load('modelo_random_forest.joblib')

@app.get("/")
def home():
    return {"status": "API Online", "modelo": "Random Forest Regressor"}

@app.post("/prever")
async def prever_excel(file: UploadFile = File(...)):
    # 1. Ler o arquivo enviado via API
    conteudo = await file.read()
    
    # 2. Salvar temporariamente para o processador ler
    with open("temp_api.xlsx", "wb") as f:
        f.write(conteudo)
    
    # 3. Usar sua função que já testamos
    X_processado = preparar_excel_para_modelo("temp_api.xlsx")
    
    # 4. Fazer a previsão
    previsoes = modelo.predict(X_processado)
    
    # 5. Retornar os resultados como JSON
    return {
        "quantidade_linhas": len(previsoes),
        "previsoes": previsoes.tolist()
    }