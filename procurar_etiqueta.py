#!/usr/bin/env python3
"""
Procura by etiqueta nos dados do Bling
"""

from bling_auth import bling_get
import json

etiqueta = "AD287897978BR"

print(f"\n🔍 Procurando etiqueta {etiqueta} em Bling\n")

# Busca em todos os pedidos pré-salvos
with open("contatos_rastreamento.json", "r", encoding="utf-8") as f:
    contatos = json.load(f)

# Encontra pelo JSON que já temos
encontrado = None
for contato in contatos:
    if contato.get("etiqueta") == etiqueta:
        encontrado = contato
        break

if encontrado:
    print("✅ ENCONTRADA NO ARQUIVO contatos_rastreamento.json!\n")
    
    # Busca detalhes complementares no Bling
    print("Obtendo detalhes completos...\n")
    
    resp = bling_get("/pedidos/vendas", params={"logistica": 151483, "limit": 100})
    
    for pedido in resp.get("data", []):
        if pedido.get("numero") == encontrado["numero"]:
            volumes = pedido.get("transporte", {}).get("volumes", [])
            
            for vol in volumes:
                if vol.get("codigoRastreamento") == etiqueta:
                    dados_completos = {
                        "numero_pedido": encontrado["numero"],
                        "cliente": encontrado["cliente"],
                        "email": encontrado["email"],
                        "telefone": encontrado["telefone_celular"],
                        "etiqueta": etiqueta,
                        "servico": vol.get("servico"),
                        "data_consulta": __import__("datetime").datetime.now().isoformat(),
                        "url_rastreamento": f"https://www.correios.com.br/rastreamento?numero={etiqueta}",
                        "status": "Ativo",
                        "origem": vol.get("origem", "N/A"),
                        "destino": vol.get("destino", "N/A")
                    }
                    
                    print(json.dumps(dados_completos, indent=2, ensure_ascii=False))
                    
                    # Salva
                    with open("situacao_etiqueta.json", "w", encoding="utf-8") as f:
                        json.dump(dados_completos, f, indent=2, ensure_ascii=False)
                    
                    print("\n✅ Salvo em: situacao_etiqueta.json")
                    exit(0)

print("❌ Etiqueta não encontrada!")
