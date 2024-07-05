from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

app = FastAPI()

def ler_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"carrinhos": {}}
    except json.JSONDecodeError:
        return {"carrinhos": {}}

def escrever_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

class ItensCarrinho(BaseModel):
    id_carrinho: str
    id_produto: int

@app.get("/")
def read_root():
    return {"message": "Olá"}

@app.post("/adicionar")
def adicionar_ao_carrinho(item: ItensCarrinho):
    carrinhos = ler_json('carrinhos.json')
    if item.id_carrinho not in carrinhos['carrinhos']:
        carrinhos['carrinhos'][item.id_carrinho] = []

    carrinhos['carrinhos'][item.id_carrinho].append(str(item.id_produto))    
    escrever_json('carrinhos.json', carrinhos)
    return {"message": "Produto adicionado ao carrinho"}

from fastapi import HTTPException

from fastapi import HTTPException

@app.get("/carrinho/{id_carrinho}")
def mostrar_carrinho(id_carrinho: str):
    carrinhos = ler_json('carrinhos.json')
    produtos = ler_json('produtos.json')
    
    if id_carrinho not in carrinhos['carrinhos']:
        raise HTTPException(status_code=404, detail="Carrinho não encontrado")

    itens_carrinho = carrinhos['carrinhos'][id_carrinho]
    
    contador_itens = {}
    for id_produto in itens_carrinho:
        if id_produto in contador_itens:
            contador_itens[id_produto] += 1
        else:
            contador_itens[id_produto] = 1
    
    detalhe_itens = []
    valor_total = 0.0
    for id_produto in contador_itens:
        produto_encontrado = next((produto for produto in produtos if produto['ID'] == id_produto), None)
        if produto_encontrado:
            valor_produto = float(produto_encontrado['VALOR'].replace('R$', '').replace('.', '').replace(',', '.'))
            quantidade = contador_itens[id_produto]
            valor_total += valor_produto * quantidade
            
            for _ in range(quantidade):
                detalhe_itens.append({
                    "ID": produto_encontrado['ID'],
                    "PRODUTO": produto_encontrado['PRODUTO'],
                    "VALOR": produto_encontrado['VALOR'],
                    "IMAGEM_PRODUTO": produto_encontrado['IMAGEM_PRODUTO'],
                    "CATEGORIA": produto_encontrado['CATEGORIA'],
                    "DESCRICAO": produto_encontrado['DESCRICAO']
                })
    
    valor_total_formatado = f"R$ {valor_total:.2f}"
    
    resposta = {"items": detalhe_itens, "valor_total": valor_total_formatado}
    
    return resposta

from fastapi import HTTPException

@app.delete("/carrinho/{id_carrinho}/{id_produto}")
def remover_do_carrinho(id_carrinho: str, id_produto: str):
    carrinhos = ler_json('carrinhos.json')
    
    if id_carrinho not in carrinhos['carrinhos']:
        raise HTTPException(status_code=404, detail="Carrinho não encontrado")
    
    if id_produto in carrinhos['carrinhos'][id_carrinho]:
        carrinhos['carrinhos'][id_carrinho].remove(id_produto)
        
        escrever_json('carrinhos.json', carrinhos)
        
        return {"message": "Produto removido do carrinho"}
    else:
        raise HTTPException(status_code=404, detail=f"Produto {id_produto} não encontrado no carrinho {id_carrinho}")

@app.delete("/carrinho/{id_carrinho}")
def remover_carrinho(id_carrinho: str):
    carrinhos = ler_json('carrinhos.json')
    
    if id_carrinho not in carrinhos['carrinhos']:
        raise HTTPException(status_code=404, detail="Carrinho não encontrado")

    else:
        del carrinhos['carrinhos'][id_carrinho]  
        escrever_json('carrinhos.json', carrinhos) 

        return {
            "message": "Carrinho esvaziado"
        }