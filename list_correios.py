#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para listar todas as etiquetas de postagem - APENAS CORREIOS.
"""

import sys
import json
from datetime import datetime
from bling_auth import bling_get, get_token_info

def main():
    print("\n" + "="*100)
    print("  ETIQUETAS DE POSTAGEM - CORREIOS")
    print("="*100 + "\n")
    
    # ID de Correios
    CORREIOS_ID = 151483
    
    # 1. Verificar status do token
    print("1. STATUS DO TOKEN")
    print("-" * 100)
    info = get_token_info()
    print(f"  Status: {info['status']} | Expira em {info['expires_in_minutes']} minutos\n")
    
    # 2. Buscar pedidos da Correios
    print("2. BUSCANDO PEDIDOS CORREIOS")
    print("-" * 100)
    
    try:
        print(f"  GET /pedidos/vendas?logistica={CORREIOS_ID}&limite=100\n")
        response = bling_get("/pedidos/vendas", params={"logistica": CORREIOS_ID, "limite": 100})
        
        pedidos = response.get("data", [])
        
        if not pedidos:
            print("  Nenhum pedido de Correios encontrado!\n")
            return 1
        
        print(f"  Total de pedidos Correios: {len(pedidos)}\n")
        
        # 3. Extrair dados de cada pedido
        print("3. DETALHES DOS PEDIDOS")
        print("="*100 + "\n")
        
        dados_extraidos = []
        
        for idx, pedido in enumerate(pedidos, 1):
            pedido_id = pedido.get("id")
            pedido_num = pedido.get("numero")
            contato = pedido.get("contato", {})
            data = pedido.get("data", "N/A")
            data_saida = pedido.get("dataSaida", "N/A")
            situacao = pedido.get("situacao", {})
            
            print(f"PEDIDO #{idx}")
            print(f"  ID Pedido:      {pedido_id}")
            print(f"  Numero:         {pedido_num}")
            print(f"  Cliente:        {contato.get('nome', 'N/A')}")
            print(f"  Data Pedido:    {data}")
            print(f"  Data Saida:     {data_saida}")
            print(f"  Situacao:       {situacao}")
            print()
            
            dados_extraidos.append({
                "numero_pedido": pedido_num,
                "id_pedido": pedido_id,
                "cliente": contato.get("nome"),
                "data_pedido": data,
                "data_saida": data_saida,
                "situacao_id": situacao.get("id"),
                "total": pedido.get("total"),
            })
        
        # 4. Exportar dados
        print("="*100)
        print("4. EXPORTANDO DADOS")
        print("-" * 100)
        
        output_file = "pedidos_correios.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "transportadora": "Correios",
                "logistica_id": CORREIOS_ID,
                "total_pedidos": len(dados_extraidos),
                "pedidos": dados_extraidos
            }, f, indent=2, ensure_ascii=False)
        
        print(f"  Arquivo exportado: {output_file}\n")
        
        print("="*100 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"  Erro: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
