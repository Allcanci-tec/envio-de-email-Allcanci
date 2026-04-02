#!/usr/bin/env python3
"""
Examina estrutura completa de pedidos Correios
"""

from bling_auth import bling_get
import json

def inspect_correios():
    print("=" * 90)
    print("INSPECIONANDO PEDIDOS CORREIOS - ESTRUTURA COMPLETA")
    print("=" * 90)
    
    # Teste 1: Pega pedidos Correios (logistica=151483)
    print("\n1️⃣ Buscando 5 pedidos Correios com logistica=151483")
    try:
        response = bling_get("/pedidos/vendas", params={"logistica": 151483, "limit": 5})
        if isinstance(response, dict) and "data" in response:
            print(f"✅ Encontrados {len(response['data'])} pedidos\n")
            
            for i, pedido in enumerate(response['data'][:3], 1):
                print(f"\n--- PEDIDO {i} ---")
                print(f"ID: {pedido.get('id')}")
                print(f"Número: {pedido.get('numero')}")
                print(f"Data: {pedido.get('data')}")
                print(f"Total: R$ {pedido.get('total')}")
                print(f"Situacao: {pedido.get('situacao')}")
                
                # Procura por qualquer coisa relacionada a etiqueta/rastreamento
                print(f"\nTodas as chaves: {list(pedido.keys())}")
                
                # Print completo em JSON para inspeção
                print(f"\n📄 JSON Completo do Pedido {i}:")
                print(json.dumps(pedido, indent=2, ensure_ascii=False)[:1500])
    except Exception as e:
        print(f"❌ {str(e)[:200]}\n")
    
    # Teste 2: Tenta /notasfiscais para ver se etiquetas estão lá
    print("\n\n2️⃣ Testando /notasfiscais (pode ter etiqueta/rastreamento)")
    try:
        response = bling_get("/notasfiscais", params={"limit": 3})
        if isinstance(response, dict) and "data" in response and response["data"]:
            print(f"✅ Encontrados {len(response['data'])} NFs")
            
            nf = response['data'][0]
            print(f"Chaves da NF: {list(nf.keys())}\n")
            
            # Procura por rastreamento/etiqueta
            for chave in nf.keys():
                if any(palavra in chave.lower() for palavra in ["etiqueta", "rastreamento", "postag", "objeto", "nfe"]):
                    print(f"  {chave}: {nf.get(chave)}")
    except Exception as e:
        print(f"❌ {str(e)[:200]}\n")
    
    # Teste 3: Buscar todos endpoints disponíveit
    print("\n\n3️⃣ Testando outros endpoints potenciais")
    
    endpoints_to_test = [
        "/etiquetas",
        "/rastreamento",
        "/postagens",
        "/logisticas/transporte",
        "/vendas",
        "/vendas/etiquetas",
        "/envios",
        "/avisos"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = bling_get(endpoint, params={"limit": 1})
            print(f"✅ {endpoint} → 200 OK")
        except Exception as e:
            status = "404" if "404" in str(e) else "Erro"
            print(f"❌ {endpoint} → {status}")

if __name__ == "__main__":
    inspect_correios()
