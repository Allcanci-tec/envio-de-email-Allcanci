#!/usr/bin/env python3
"""
Debug: Verifica o que vem em /pedidos/vendas
"""

from bling_auth import bling_get
import json

resp = bling_get("/pedidos/vendas", params={"logistica": 151483, "limit": 5})

print("Chaves da resposta:", resp.keys())
print("\nPrimeiro pedido:")
if resp.get("data"):
    p = resp["data"][0]
    print(json.dumps(p, indent=2, ensure_ascii=False)[:1000])
    
    # Verifica transporte
    print("\n\nTransporte:")
    print(json.dumps(p.get("transporte", {}), indent=2, ensure_ascii=False)[:800])
