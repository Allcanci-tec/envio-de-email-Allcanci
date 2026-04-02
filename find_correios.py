#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para listar objetos de postagem APENAS de Correios.
"""

import sys
import json
from datetime import datetime
from bling_auth import bling_get, get_token_info

def main():
    print("\n" + "="*90)
    print("  LISTAGEM DE OBJETOS DE POSTAGEM - CORREIOS")
    print("="*90 + "\n")
    
    # 1. Pegar informações de token
    print("1. STATUS DO TOKEN")
    print("-" * 90)
    info = get_token_info()
    print(f"  Status: {info['status']} | Expira em {info['expires_in_minutes']} minutos\n")
    
    # 2. Buscar logísticas para encontrar Correios
    print("2. BUSCANDO TRANSPORTADORA CORREIOS")
    print("-" * 90)
    
    try:
        logisticas = bling_get("/logisticas")
        
        correios_id = None
        for log in logisticas.get("data", []):
            if log.get("descricao") == "Correios":
                correios_id = log.get("id")
                print(f"  Encontrado: Correios (ID: {correios_id})\n")
                break
        
        if not correios_id:
            print("  Erro: Transportadora Correios nao encontrada!\n")
            return 1
        
        # 3. Tentar buscar objetos de Correios
        print("3. BUSCANDO OBJETOS DE POSTAGEM - CORREIOS")
        print("-" * 90)
        
        # Tentar diferentes rotas
        rotas_teste = [
            f"/logisticas/{correios_id}",
            f"/logisticas/{correios_id}/objetos",
            f"/pedidos/vendas?logistica={correios_id}",
            "/pedidos/vendas",
        ]
        
        print(f"  Testando rotas para ID {correios_id}:\n")
        
        for rota in rotas_teste:
            try:
                response = bling_get(rota)
                print(f"  OK - {rota}")
                
                # Se funcionou, verificar estrutura
                if isinstance(response.get("data"), list) and response["data"]:
                    print(f"      Retornou {len(response['data'])} items")
                    
                    # Salvar primeiro item
                    primeiro = response["data"][0]
                    if isinstance(primeiro, dict):
                        print(f"      Chaves: {list(primeiro.keys())[:5]}...")
                
            except Exception as e:
                status_erro = "404" if "404" in str(e) else "ERRO"
                print(f"  {status_erro} - {rota}")
        
        return 0
        
    except Exception as e:
        print(f"  Erro: {e}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
