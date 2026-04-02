#!/usr/bin/env python3
"""
Inspeciona campo 'transporte' de pedidos Correios
"""

from bling_auth import bling_get
import json

def inspect_transporte():
    print("=" * 90)
    print("INSPECIONANDO CAMPO 'TRANSPORTE' DE PEDIDOS CORREIOS")
    print("=" * 90)
    
    # Pega 10 pedidos Correios para inspecionar
    print("\n1️⃣ Obtendo 10 pedidos Correios...")
    try:
        response = bling_get("/pedidos/vendas", params={"logistica": 151483, "limit": 10})
        if response.get("data"):
            pedidos = response["data"]
            print(f"✅ Obtidos {len(pedidos)} pedidos\n")
            
            # Acessa detalhes de cada pedido para inspecionar 'transporte'
            for i, pedido_resumo in enumerate(pedidos[:5], 1):  # Primeiros 5
                pedido_id = pedido_resumo["id"]
                print(f"\n{'='*60}")
                print(f"PEDIDO {i} - ID: {pedido_id}, Número: {pedido_resumo.get('numero')}")
                print(f"{'='*60}")
                
                try:
                    detail = bling_get(f"/pedidos/vendas/{pedido_id}")
                    if detail.get("data"):
                        data = detail["data"]
                        
                        # Inspeciona transporte
                        transporte = data.get("transporte", {})
                        print(f"\n🚚 TRANSPORTE:")
                        print(json.dumps(transporte, indent=2, ensure_ascii=False))
                        
                        # Se houver etiqueta no transporte
                        if transporte:
                            print(f"\n   Chaves de 'transporte': {list(transporte.keys())}")
                            
                            # Procura por etiqueta/rastreamento em subníveis
                            for key, value in transporte.items():
                                if isinstance(value, dict):
                                    print(f"   {key} → {list(value.keys())}")
                        
                        # Também inspeciona notaFiscal
                        nf = data.get("notaFiscal", {})
                        if nf.get("id") and nf.get("id") != 0:
                            print(f"\n📄 NOTA FISCAL ID: {nf.get('id')}")
                            # Tenta pegar detalhes da NF
                            try:
                                nf_detail = bling_get(f"/notasfiscais/{nf.get('id')}")
                                if nf_detail.get("data"):
                                    print(json.dumps(nf_detail["data"], indent=2, ensure_ascii=False)[:800])
                            except:
                                pass
                
                except Exception as e:
                    print(f"❌ Erro ao obter pedido {pedido_id}: {str(e)[:100]}")
        else:
            print("❌ Nenhum pedido encontrado")
    except Exception as e:
        print(f"❌ Erro: {str(e)[:200]}")

if __name__ == "__main__":
    inspect_transporte()
