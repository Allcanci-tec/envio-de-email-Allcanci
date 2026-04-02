#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para encontrar a rota correta dos objetos de logística/rastreamento.
"""

import requests
from bling_auth import get_token

def test_endpoint(endpoint: str, method: str = "GET"):
    """Testa um endpoint e retorna status + resposta reduzida."""
    base_url = "https://api.bling.com.br/Api/v3"
    token = get_token()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    
    try:
        if method == "GET":
            r = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
        else:
            r = requests.post(f"{base_url}{endpoint}", headers=headers, timeout=10)
        
        status = "✅" if r.status_code < 400 else "❌"
        
        # Tentar extrair a quantidade de dados
        try:
            data = r.json()
            if isinstance(data, dict) and "data" in data:
                count = len(data["data"]) if isinstance(data["data"], list) else "dict"
                return f"{status} {r.status_code} - {endpoint} ({count} items)"
        except:
            pass
        
        return f"{status} {r.status_code} - {endpoint}"
    except Exception as e:
        return f"❌ ERRO - {endpoint}"

def main():
    print("\n" + "="*80)
    print("  🔍 EXPLORAÇÃO DE ENDPOINTS DE LOGÍSTICA")
    print("="*80 + "\n")
    
    endpoints = [
        # Possíveis rotas para objetos/rastreamentos
        "/logisticas/542471",  # Allcanci ID
        "/logisticas/542471/objetos",
        "/objetos",
        "/rastreamentos",
        "/postagens",
        "/pedidos/vendas",  # Talvez rastreamento esteja aqui
    ]
    
    print("Testando endpoints:\n")
    for endpoint in endpoints:
        result = test_endpoint(endpoint)
        print(f"  {result}")
    
    print("\n")
    
    # Explorar estrutura de /pedidos/vendas
    print("="*80)
    print("  📋 INSPECIONANDO ESTRUTURA DE /pedidos/vendas")
    print("="*80 + "\n")
    
    import json
    from bling_auth import bling_get
    
    try:
        response = bling_get("/pedidos/vendas", params={"limite": 1})
        if response.get("data"):
            print("Primeiro pedido:")
            print(json.dumps(response["data"][0], indent=2, ensure_ascii=False)[:1000])
            print("...\n")
    except Exception as e:
        print(f"Erro: {e}\n")

if __name__ == "__main__":
    main()
