#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script CORRETO: Buscar APENAS em /logisticas/objetos
Extrair: ID do Pedido, Etiqueta (rastreamento) e Situação
Filtrar apenas objetos de Correios
"""

import sys
import json
from bling_auth import bling_get

def is_correios_tracking(codigo):
    """Verifica se o código é de rastreamento Correios (padrão: 2 letras + 9 números + BR)."""
    if not codigo or codigo == "N/A" or codigo == "":
        return False
    # Padrão Correios: começa com 2 letras, tem números, termina com BR
    # Ex: AD287897978BR
    if len(codigo) >= 13:
        if codigo[:2].isalpha() and codigo[-2:] == "BR" and codigo[2:-2].isdigit():
            return True
    return False

def main():
    print("\n" + "="*100)
    print("  OBJETOS DE POSTAGEM - CORREIOS")
    print("="*100 + "\n")
    
    try:
        print("Consultando: GET /logisticas/objetos\n")
        response = bling_get("/logisticas/objetos")
        
        objetos = response.get("data", [])
        
        if not objetos:
            print("Nenhum objeto encontrado.\n")
            return 1
        
        print(f"Total de objetos retornados: {len(objetos)}\n")
        
        # Filtrar apenas Correios
        objetos_correios = []
        for obj in objetos:
            rastreamento = obj.get("rastreamento", {}).get("codigo", "")
            if is_correios_tracking(rastreamento):
                objetos_correios.append(obj)
        
        print(f"Objetos de Correios: {len(objetos_correios)}\n")
        
        if not objetos_correios:
            print("Nenhum objeto de Correios encontrado.\n")
            return 0
        
        # Exibir tabela
        print("-" * 100)
        print(f"{'ID do Pedido/NF':<20} {'Etiqueta (Rastreamento)':<25} {'Situação':<50}")
        print("-" * 100)
        
        for obj in objetos_correios:
            # Extrair dados conforme mapeamento do usuário
            pedido_id = obj.get("pedido", {}).get("id") or obj.get("notaFiscal", {}).get("id", "N/A")
            etiqueta = obj.get("rastreamento", {}).get("codigo", "N/A")
            situacao = obj.get("situacao", {}).get("nome", "N/A")
            
            print(f"{str(pedido_id):<20} {etiqueta:<25} {situacao:<50}")
        
        print("-" * 100 + "\n")
        
        # Exportar JSON limpo
        dados_exportacao = []
        for obj in objetos_correios:
            pedido_id = obj.get("pedido", {}).get("id") or obj.get("notaFiscal", {}).get("id")
            etiqueta = obj.get("rastreamento", {}).get("codigo")
            situacao = obj.get("situacao", {}).get("nome")
            
            dados_exportacao.append({
                "id_pedido": pedido_id,
                "etiqueta": etiqueta,
                "situacao": situacao
            })
        
        output_file = "objetos_correios_limpo.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "total": len(dados_exportacao),
                "objetos": dados_exportacao
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
