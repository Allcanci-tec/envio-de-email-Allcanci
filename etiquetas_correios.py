#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script CORRETO V2: Usar /logisticas/etiquetas
Esta rota deve retornar as etiquetas das vendas diretamente.
"""

import sys
import json
from bling_auth import bling_get

def main():
    print("\n" + "="*110)
    print("  OBJETOS DE POSTAGEM - ETIQUETAS CORREIOS")
    print("="*110 + "\n")
    
    try:
        print("Consultando: GET /logisticas/etiquetas\n")
        response = bling_get("/logisticas/etiquetas")
        
        etiquetas = response.get("data", [])
        
        if not etiquetas:
            print("Nenhuma etiqueta encontrada.\n")
            return 1
        
        print(f"Total de etiquetas retornadas: {len(etiquetas)}\n")
        
        # Exibir tabela
        print("-" * 110)
        print(f"{'ID do Pedido':<20} {'Etiqueta (Código)':<25} {'Situação':<35} {'Origem':<15} {'Destino':<15}")
        print("-" * 110)
        
        etiquetas_extraidas = []
        
        for etiqueta in etiquetas:
            # Extrair dados
            pedido_id = etiqueta.get("pedidoVenda", {}).get("id") or etiqueta.get("notaFiscal", {}).get("id", "N/A")
            rastreamento = etiqueta.get("rastreamento", {})
            codigo = rastreamento.get("codigo", "N/A")
            descricao = rastreamento.get("descricao", "N/A")
            origem = rastreamento.get("origem", "N/A")
            destino = rastreamento.get("destino", "N/A")
            
            print(f"{str(pedido_id):<20} {codigo:<25} {descricao:<35} {origem[:14]:<15} {destino[:14]:<15}")
            
            etiquetas_extraidas.append({
                "id_pedido": pedido_id,
                "etiqueta": codigo,
                "situacao": descricao,
                "origem": origem,
                "destino": destino
            })
        
        print("-" * 110 + "\n")
        
        # Exportar JSON
        output_file = "objetos_etiquetas_correios.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "total": len(etiquetas_extraidas),
                "objetos": etiquetas_extraidas
            }, f, indent=2, ensure_ascii=False)
        
        print(f"Dados exportados em: {output_file}\n")
        
        return 0
        
    except Exception as e:
        print(f"Erro: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
