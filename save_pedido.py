#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inspecionar e salvar estrutura de um pedido.
"""

import json
from bling_auth import bling_get

def main():
    # Pegar primeiro pedido
    pedidos_response = bling_get("/pedidos/vendas", params={"limite": 1})
    
    if not pedidos_response.get("data"):
        print("Nenhum pedido encontrado!")
        return
    
    pedido_id = pedidos_response["data"][0]["id"]
    print(f"Obtendo detalhes do pedido ID: {pedido_id}")
    
    # Acessar detalhes do pedido
    pedido_detalhes = bling_get(f"/pedidos/vendas/{pedido_id}")
    
    # Salvar em arquivo
    with open("pedido_estrutura.json", "w", encoding="utf-8") as f:
        json.dump(pedido_detalhes, f, indent=2, ensure_ascii=False)
    
    print("Estrutura salva em pedido_estrutura.json")
    
    # Verificar chaves principais
    if "data" in pedido_detalhes:
        chaves = list(pedido_detalhes["data"].keys())
        print(f"\nChaves principais do pedido:")
        for chave in sorted(chaves):
            print(f"  - {chave}")

if __name__ == "__main__":
    main()
