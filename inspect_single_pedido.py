#!/usr/bin/env python3
"""
Acessa pedido individual para ver detalhes expandidos
"""

from bling_auth import bling_get
import json

def inspect_single_pedido():
    print("=" * 90)
    print("INSPECIONANDO PEDIDO INDIVIDUAL COM DETALHES EXPANDIDOS")
    print("=" * 90)
    
    # Primeiro pega um ID de pedido Correios
    print("\n1️⃣ Obtendo ID de pedido Correios...")
    try:
        response = bling_get("/pedidos/vendas", params={"logistica": 151483, "limit": 1})
        if response.get("data"):
            pedido_id = response["data"][0]["id"]
            print(f"✅ Pedido ID: {pedido_id}\n")
            
            # Teste 2: Acessa o pedido específico
            print(f"2️⃣ Consultando /pedidos/vendas/{pedido_id} para detalhes completos")
            try:
                detail_response = bling_get(f"/pedidos/vendas/{pedido_id}")
                print(f"✅ 200 OK!")
                print(f"\nChaves disponíveis: {list(detail_response.keys())}")
                
                print(f"\n📄 Resposta Completa:")
                print(json.dumps(detail_response, indent=2, ensure_ascii=False)[:2000])
                
                if "data" in detail_response:
                    data = detail_response["data"]
                    print(f"\nChaves em 'data': {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                    
                    # Procura por etiqueta/rastreamento
                    print(f"\n🔍 Campos relacionados a rastreamento:")
                    for key in data.keys() if isinstance(data, dict) else []:
                        if any(w in key.lower() for w in ["etiqueta", "raast", "postag", "objeto", "nf", "notafisc", "envio"]):
                            print(f"  {key}: {data[key]}")
                        
            except Exception as e:
                print(f"❌ {str(e)[:200]}\n")
            
            # Teste 3: Tenta /avisos (pode ter informações de rastreamento)
            print(f"\n3️⃣ Consultando /avisos/vendas/{pedido_id}")
            try:
                avisos = bling_get(f"/avisos/vendas/{pedido_id}")
                print(f"✅ 200 OK!")
                print(json.dumps(avisos, indent=2, ensure_ascii=False)[:1000])
            except Exception as e:
                print(f"❌ {str(e)[:200]}\n")
            
            # Teste 4: Tenta /avisos sem ID
            print(f"\n4️⃣ Consultando /avisos (todos)")
            try:
                avisos_all = bling_get("/avisos", params={"limit": 5})
                print(f"✅ 200 OK!")
                if avisos_all.get("data"):
                    print(f"Encontrados {len(avisos_all['data'])} avisos")
                    print(json.dumps(avisos_all, indent=2, ensure_ascii=False)[:1500])
            except Exception as e:
                print(f"❌ {str(e)[:200]}\n")
        else:
            print("❌ Nenhum pedido Correios encontrado")
    except Exception as e:
        print(f"❌ Erro: {str(e)[:200]}\n")

if __name__ == "__main__":
    inspect_single_pedido()
