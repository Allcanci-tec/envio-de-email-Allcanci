#!/usr/bin/env python3
"""
MVP: Extrai de 30 pedidos com rastreamento - Número | Cliente | Etiqueta
"""

from bling_auth import bling_get
import json

print("\n📦 MVP - Extraindo 100+ pedidos Correios\n")

dados = []

# Primeira page
resp = bling_get("/pedidos/vendas", params={"logistica": 151483, "limit": 100})

print(f"Processando {min(100, len(resp.get('data', [])))} pedidos...\n")

for p in resp.get("data", [])[:100]:
    numero = p.get("numero")
    cliente = p.get("contato", {}).get("nome", "")
    pedido_id = p["id"]
    
    # Fetch individual
    detail = bling_get(f"/pedidos/vendas/{pedido_id}")
    vols = detail.get("data", {}).get("transporte", {}).get("volumes", [])
    
    for v in vols:
        etiq = v.get("codigoRastreamento", "")
        if etiq:
            dados.append({
                "numero": numero,
                "cliente": cliente,
                "etiqueta": etiq
            })
            print(f"  {numero:<10} | {cliente:<50} | {etiq}")

# Export
with open("mvp.json", "w", encoding="utf-8") as f:
    json.dump(dados, f, indent=2, ensure_ascii=False)

print(f"\n✅ Total: {len(dados)} etiquetas found")
print(f"✅ File: mvp.json\n")
