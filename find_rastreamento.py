#!/usr/bin/env python3
"""
Procura por pedidos com codigoRastreamento preenchido e testa endpoints de volumes
"""

from bling_auth import bling_get
import json

def find_rastreamento():
    print("=" * 90)
    print("PROCURANDO PEDIDOS COM CÓDIGO DE RASTREAMENTO PREENCHIDO")
    print("=" * 90)
    
    # Teste 1: Procura em mais pedidos
    print("\n1️⃣ Escaneando 50 pedidos Correios para encontrar codigoRastreamento...")
    
    found_count = 0
    checked_count = 0
    
    try:
        # Pega primeiros 50 (limite da query faz isso em batches)
        response = bling_get("/pedidos/vendas", params={"logistica": 151483, "limit": 50})
        
        if response.get("data"):
            for pedido_resumo in response["data"][:50]:
                pedido_id = pedido_resumo["id"]
                checked_count += 1
                
                try:
                    detail = bling_get(f"/pedidos/vendas/{pedido_id}")
                    if detail.get("data"):
                        volumes = detail["data"].get("transporte", {}).get("volumes", [])
                        
                        for volume in volumes:
                            if volume.get("codigoRastreamento"):
                                found_count += 1
                                print(f"\n✅ ENCONTRADO - Pedido {pedido_resumo.get('numero')} (ID: {pedido_id})")
                                print(f"   Volume ID: {volume.get('id')}")
                                print(f"   Serviço: {volume.get('servico')}")
                                print(f"   Código Rastreamento: {volume.get('codigoRastreamento')}")
                except:
                    pass
        
        print(f"\n📊 Resultado: {found_count} volumes com rastreamento em {checked_count} pedidos verificados")
    except Exception as e:
        print(f"❌ Erro: {str(e)[:200]}")
    
    # Teste 2: Tenta endpoints de volumes
    print("\n\n2️⃣ Testando endpoints para volumes/rastreamento")
    
    endpoints = [
        "/volumes",
        "/volumes/rastreamento",
        "/rastreamento/volumes",
        "/objetos",
        "/etiquetas",
        "/logisticas/volumes",
        "/logisticas/rastreamento"
    ]
    
    for endpoint in endpoints:
        try:
            response = bling_get(endpoint, params={"limit": 1})
            print(f"✅ {endpoint} → 200 OK")
            if isinstance(response, dict) and "data" in response:
                print(f"   Sample: {json.dumps(response['data'][:1], indent=2, ensure_ascii=False)[:400]}")
        except Exception as e:
            status = "404" if "404" in str(e) else ("403" if "403" in str(e) else "Erro")
            print(f"❌ {endpoint} → {status}")
    
    # Teste 3: Tenta acessar um volume específico
    print("\n\n3️⃣ Tentando acessar volume específico")
    try:
        response = bling_get("/pedidos/vendas", params={"logistica": 151483, "limit": 1})
        if response.get("data"):
            pedido = response["data"][0]
            detail = bling_get(f"/pedidos/vendas/{pedido['id']}")
            
            volumes = detail.get("data", {}).get("transporte", {}).get("volumes", [])
            if volumes:
                volume_id = volumes[0]["id"]
                print(f"Tentando /volumes/{volume_id}")
                try:
                    vol_detail = bling_get(f"/volumes/{volume_id}")
                    print(f"✅ 200 OK!")
                    print(json.dumps(vol_detail, indent=2, ensure_ascii=False)[:1000])
                except Exception as e2:
                    print(f"❌ {str(e2)[:200]}")
    except:
        pass

if __name__ == "__main__":
    find_rastreamento()
