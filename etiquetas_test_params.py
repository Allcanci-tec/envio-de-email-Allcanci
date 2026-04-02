#!/usr/bin/env python3
"""
Testa diferentes parâmetros para /logisticas/etiquetas
"""

from bling_auth import bling_get, get_token_info
import json

def test_etiquetas():
    print("=" * 90)
    print("TESTANDO PARÂMETROS PARA /logisticas/etiquetas")
    print("=" * 90)
    
    # Mostrar token
    info = get_token_info()
    print(f"✅ Token: {info['status']}, expira em {info['expires_in_minutes']} min\n")
    
    # Teste 1: Com limite
    print("1️⃣ Teste: /logisticas/etiquetas?limit=5")
    try:
        response = bling_get("/logisticas/etiquetas", params={"limit": 5})
        print(f"✅ 200 OK!")
        print(json.dumps(response, indent=2)[:500])
    except Exception as e:
        print(f"❌ {e}\n")
    
    # Teste 2: Com offset
    print("\n2️⃣ Teste: /logisticas/etiquetas?offset=0&limit=10")
    try:
        response = bling_get("/logisticas/etiquetas", params={"offset": 0, "limit": 10})
        print(f"✅ 200 OK!")
        print(json.dumps(response, indent=2)[:500])
    except Exception as e:
        print(f"❌ {e}\n")
    
    # Teste 3: Com filtro de status
    print("\n3️⃣ Teste: /logisticas/etiquetas?situacao=1")
    try:
        response = bling_get("/logisticas/etiquetas", params={"situacao": 1})
        print(f"✅ 200 OK!")
        print(json.dumps(response, indent=2)[:500])
    except Exception as e:
        print(f"❌ {e}\n")
    
    # Teste 4: Ver se precisa de IDs de pedido específicos
    # Primeiro, pega um pedido Correios conhecida
    print("\n4️⃣ Teste: Buscando IDs de pedidos Correios...")
    try:
        response = bling_get("/pedidos/vendas", params={"logistica": 151483, "limit": 1})
        if "data" in response and len(response["data"]) > 0:
            pedido_id = response["data"][0]["id"]
            print(f"   Obtido pedido ID: {pedido_id}")
            
            print(f"   Tentando /logisticas/etiquetas?idPedidoVenda={pedido_id}")
            try:
                etiquetas_response = bling_get("/logisticas/etiquetas", params={"idPedidoVenda": pedido_id})
                print(f"   ✅ 200 OK!")
                print(f"   {json.dumps(etiquetas_response, indent=2)[:600]}")
            except Exception as e2:
                print(f"   ❌ {e2}")
        else:
            print("   ❌ Nenhum pedido encontrado")
    except Exception as e:
        print(f"❌ Erro ao buscar pedidos: {e}\n")
    
    # Teste 5: Consultar endpoint via GET direto
    print("\n5️⃣ Teste: GET /logisticas/etiquetas?page=1")
    try:
        response = bling_get("/logisticas/etiquetas", params={"page": 1})
        print(f"✅ 200 OK!")
        print(json.dumps(response, indent=2)[:500])
    except Exception as e:
        print(f"❌ {e}\n")

if __name__ == "__main__":
    test_etiquetas()
