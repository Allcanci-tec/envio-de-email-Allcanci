#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inspecionar um pedido específico com todos os detalhes.
"""

import json
from bling_auth import bling_get

def main():
    print("\n" + "="*80)
    print("  🔍 INSPECCIONANDO PEDIDO COMPLETO")
    print("="*80 + "\n")
    
    # Pegar primeiro pedido
    pedidos_response = bling_get("/pedidos/vendas", params={"limite": 1})
    
    if not pedidos_response.get("data"):
        print("Nenhum pedido encontrado!")
        return
    
    pedido_id = pedidos_response["data"][0]["id"]
    print(f"📋 Obtendo detalhes do pedido ID: {pedido_id}\n")
    
    # Tentar acessar detalhes do pedido
    try:
        pedido_detalhes = bling_get(f"/pedidos/vendas/{pedido_id}")
        print("Pedido completo (JSON):")
        print(json.dumps(pedido_detalhes, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erro ao acessar /pedidos/vendas/{pedido_id}: {e}\n")
        print("Estrutura do pedido da lista:")
        print(json.dumps(pedidos_response["data"][0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
