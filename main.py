from fastapi import FastAPI, HTTPException, Query, Depends, Header
from jose import JWTError, jwt
from datetime import datetime, timedelta
import requests

app = FastAPI()

# Configuração do JWT
SECRET_KEY = "sua_chave_secreta_12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def criar_token(dados: dict):
    """
    Gera um token JWT.
    """
    expira = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    dados.update({"exp": expira})
    return jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)

def validar_token(authorization: str = Header(...)):
    """
    Valida o token JWT.
    """
    try:
        # Obtendo o token diretamente do header Authorization
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")
    except IndexError:
        raise HTTPException(status_code=400, detail="Token não fornecido.")

# Endpoint para autenticação
@app.post("/login")
def login(username: str, password: str):
    if username == "admin" and password == "1234":
        token = criar_token({"sub": username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Usuário ou senha inválidos.")

# Endpoint de municípios (proteção com JWT)
@app.get("/municipios")
def listar_municipios(uf: str = Query(..., description="UF do estado (ex: SP, RJ)"), token: dict = Depends(validar_token)):
    """
    Lista os municípios de uma UF.
    """
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao buscar dados do IBGE.")

    dados = response.json()
    municipios = [{"id": item["id"], "nome": item["nome"]} for item in dados]
    return {"uf": uf.upper(), "municipios": municipios}

@app.get("/welcome")
async def welcome(name: str):
    return {"message": f"Bem-vindo(a), {name}!"}
