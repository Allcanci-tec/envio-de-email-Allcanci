#!/usr/bin/env python3
"""
MVP Super Simples: Retorna Número | Cliente | Etiqueta
"""

from bling_auth import bling_get
import json

print("\n📦 EXTRAINDO RASTREAMENTO...\n")

dados = []

# Faz request simples
resp = bling_get("/pedidos/vendas", params={"logistica": 151483, "limit": 50})

# Itera pela resposta
for p in resp.get("data", []):
    numero = p.get("numero")
    cliente = p.get("contato", {}).get("nome", "")
    
    # Pega volumes
    vols = p.get("transporte", {}).get("volumes", [])
    for v in vols:
        etiq = v.get("codigoRastreamento", "")
        if etiq:
            dados.append({
                "numero": numero,
                "cliente": cliente,
                "etiqueta": etiq
            })
            print(f"  {numero:<10} | {cliente:<50} | {etiq}")

# Exporta
with open("mvp.json", "w", encoding="utf-8") as f:
    json.dump(dados, f, indent=2, ensure_ascii=False)

print(f"\n✅ Total: {len(dados)} etiquetas")
print(f"✅ Arquivo: mvp.json")
