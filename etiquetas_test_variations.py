#!/usr/bin/env python3
"""
Testa mais variações de rota para acessar etiquetas
"""

from bling_auth import bling_get, bling_post, get_token_info
import json

def test_variations():
    print("=" * 90)
    print("TESTANDO VARIAÇÕES DE ROTA PARA ETIQUETAS")
    print("=" * 90)
    
    # Teste 1: Endpoint individual com ID de logistica (Correios = 151483)
    print("\n1️⃣ Teste: /logisticas/151483/etiquetas")
    try:
        response = bling_get("/logisticas/151483/etiquetas")
        print(f"✅ 200 OK!")
        if isinstance(response, dict):
            print(f"Response keys: {response.keys()}")
            print(json.dumps(response, indent=2)[:800])
        else:
            print(response[:800])
    except Exception as e:
        print(f"❌ {str(e)[:200]}\n")
    
    # Teste 2: POST sem body
    print("\n2️⃣ Teste: POST /logisticas/etiquetas sem body")
    try:
        response = bling_post("/logisticas/etiquetas", payload={})
        print(f"✅ 200 OK!")
        print(json.dumps(response, indent=2)[:800])
    except Exception as e:
        print(f"❌ {str(e)[:200]}\n")
    
    # Teste 3: POST com logistica
    print("\n3️⃣ Teste: POST /logisticas/etiquetas com filtro")
    try:
        response = bling_post("/logisticas/etiquetas", payload={"logistica": 151483})
        print(f"✅ 200 OK!")
        print(json.dumps(response, indent=2)[:800])
    except Exception as e:
        print(f"❌ {str(e)[:200]}\n")
    
    # Teste 4: Usando parâmetro em formato diferente
    print("\n4️⃣ Teste: GET /objetos com status")
    try:
        response = bling_get("/objetos", params={"status": "1"})
        print(f"✅ 200 OK!")
        print(json.dumps(response, indent=2)[:800])
    except Exception as e:
        print(f"❌ {str(e)[:200]}\n")
    
    # Teste 5: GET objetos simples
    print("\n5️⃣ Teste: GET /objetos")
    try:
        response = bling_get("/objetos")
        print(f"✅ 200 OK!")
        print(json.dumps(response, indent=2)[:800])
    except Exception as e:
        print(f"❌ {str(e)[:200]}\n")
    
    # Teste 6: Consultando endpoints já conhecidos
    print("\n6️⃣ Teste: Verificando endpoints conhecidos")
    
    endpoints = [
        "/contatos",
        "/logisticas",
        "/pedidos/vendas"
    ]
    
    for endpoint in endpoints:
        try:
            response = bling_get(endpoint, params={"limit": 1})
            print(f"✅ {endpoint} → 200 OK (chaves da resposta: {list(response.keys()) if isinstance(response, dict) else 'N/A'})")
        except Exception as e:
            print(f"❌ {endpoint} → {str(e)[:100]}")
    
    # Teste 7: Ver dados do primeiro pedido
    print("\n7️⃣ Teste: Inspecionando estrutura de /pedidos/vendas")
    try:
        response = bling_get("/pedidos/vendas", params={"limit": 1})
        if isinstance(response, dict) and "data" in response and response["data"]:
            pedido = response["data"][0]
            print(f"Pedido ID: {pedido.get('id')}")
            print(f"Chaves do pedido: {list(pedido.keys())[:15]}")  # Primeiras 15 chaves
            print(f"Logistica: {pedido.get('logistica')}")
            
            # Procurar por etiqueta/objeto/rastreamento no pedido
            for chave in pedido.keys():
                if any(palavra in chave.lower() for palavra in ["etiqueta", "objeto", "rastreamento", "postag", "nfse"]):
                    print(f"  {chave}: {pedido[chave]}")
    except Exception as e:
        print(f"❌ {str(e)[:200]}\n")

if __name__ == "__main__":
    test_variations()
