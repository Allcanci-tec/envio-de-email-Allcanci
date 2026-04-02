#!/usr/bin/env python3
"""
Busca situação da etiqueta consultando detalhes de cada pedido
"""

from bling_auth import bling_get
import json
from datetime import datetime

etiqueta = "AD287897978BR"

print(f"\n📦 SITUAÇÃO DA ETIQUETA: {etiqueta}\n")

# Carrega contatos que já temos
with open("contatos_rastreamento.json", "r", encoding="utf-8") as f:
    contatos = json.load(f)

encontrado = None
for c in contatos:
    if c.get("etiqueta") == etiqueta:
        encontrado = c
        break

if not encontrado:
    print("❌ Etiqueta não existe em contatos_rastreamento.json")
    exit(1)

print(f"✅ Etiqueta encontrada: {encontrado['cliente']}")
print(f"   Pedido: {encontrado['numero']}")
print(f"   Buscando detalhes completos...\n")

# Busca o detalhe do pedido
resp_detalhe = bling_get(f"/pedidos/vendas", params={"logistica": 151483, "limit": 100})

dados_completos = None

for pedido_resumo in resp_detalhe.get("data", []):
    if pedido_resumo.get("numero") == encontrado["numero"]:
        
        # Pega detalhe completo do pedido
        pedido_detalhe = bling_get(f"/pedidos/vendas/{pedido_resumo['id']}")
        pedido = pedido_detalhe.get("data", {})
        
        volumes = pedido.get("transporte", {}).get("volumes", [])
        
        for vol in volumes:
            if vol.get("codigoRastreamento") == etiqueta:
                dados_completos = {
                    "numero_pedido": encontrado["numero"],
                    "cliente": encontrado["cliente"],
                    "email": encontrado["email"],
                    "telefone": encontrado["telefone_celular"],
                    "etiqueta": etiqueta,
                    "servico": vol.get("servico", "N/A"),
                    "volume_id": vol.get("id"),
                    "data_consulta": datetime.now().isoformat(),
                    "status_bling": "Ativo",
                    "url_rastreamento": f"https://www.correios.com.br/rastreamento?numero={etiqueta}",
                    "operadora": "Correios (AD)",
                    "pedido": {
                        "data": pedido.get("data"),
                        "valor_total": pedido.get("total"),
                        "situacao": pedido.get("situacao", {}).get("valor")
                    }
                }
                break

if dados_completos:
    print("\n" + "="*70)
    print("✅ SITUAÇÃO DA ETIQUETA")
    print("="*70 + "\n")
    print(json.dumps(dados_completos, indent=2, ensure_ascii=False))
    
    # Salva
    with open("situacao_etiqueta.json", "w", encoding="utf-8") as f:
        json.dump(dados_completos, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Salvo em: situacao_etiqueta.json\n")
else:
    print("❌ Não conseguiu recuperar detalhes completos do pedido")
