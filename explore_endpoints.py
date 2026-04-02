#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para explorar endpoints disponíveis na API do Bling.
"""

import requests
from bling_auth import get_token

def test_endpoint(endpoint: str, method: str = "GET", params=None):
    """Testa um endpoint da API."""
    base_url = "https://api.bling.com.br/Api/v3"
    token = get_token()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    
    try:
        if method == "GET":
            r = requests.get(f"{base_url}{endpoint}", headers=headers, params=params, timeout=10)
        else:
            r = requests.post(f"{base_url}{endpoint}", headers=headers, timeout=10)
        
        status = "✅" if r.status_code < 400 else "❌"
        return f"{status} {r.status_code} - {endpoint}"
    except Exception as e:
        return f"❌ ERRO - {endpoint} ({str(e)[:50]})"

def main():
    print("\n" + "="*80)
    print("  🔍 TESTE DE ENDPOINTS - API BLING")
    print("="*80 + "\n")
    
    endpoints_to_test = [
        # Logística
        "/logisticas",
        "/logisticas/objetos",
        "/logisticas/objetos/search",
        "/logisticas/rastreamentos",
        
        # Pedidos
        "/pedidos/vendas",
        
        # Contatos
        "/contatos",
        
        # Produtos
        "/produtos",
        
        # Notas Fiscais
        "/nfes/vendas",
        
        # Webhooks
        "/webhooks",
    ]
    
    print("Testando endpoints:\n")
    for endpoint in endpoints_to_test:
        result = test_endpoint(endpoint)
        print(f"  {result}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
