#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Explorar variações de rota para encontrar objetos de postagem.
"""

import requests
from bling_auth import get_token

def test_endpoint(endpoint: str):
    """Testa um endpoint."""
    base_url = "https://api.bling.com.br/Api/v3"
    token = get_token()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    
    try:
        r = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
        status = "✅" if r.status_code < 400 else "❌"
        
        # Tentar ver quantidade de dados
        try:
            data = r.json()
            if isinstance(data, dict) and "data" in data:
                if isinstance(data["data"], list):
                    return f"{status} {r.status_code} - {endpoint} ({len(data['data'])} items)"
        except:
            pass
        
        return f"{status} {r.status_code} - {endpoint}"
    except Exception as e:
        return f"❌ ERRO - {endpoint}"

endpoints_para_testar = [
    "/objetos",
    "/logisticas/objetos",
    "/postagens",
    "/postagens/objetos",
    "/logisticas/151483/objetos",
    "/logisticas/542471/objetos",
    "/rastreamento",
    "/rastreamentos",
    "/envios",
    "/etiquetas",
]

print("\n" + "="*80)
print("  EXPLORANDO ROTAS DE OBJETOS DE POSTAGEM")
print("="*80 + "\n")

for endpoint in endpoints_para_testar:
    print(f"  {test_endpoint(endpoint)}")

print("\n" + "="*80 + "\n")
