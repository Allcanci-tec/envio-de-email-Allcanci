#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug: Testar variações de rota para objetos de postagem
"""

import requests
from bling_auth import get_token

token = get_token()
base_url = "https://api.bling.com.br/Api/v3"

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
}

rotas = [
    "/logisticas/objetos",
    "/logisticas/objetos/",
    "/logsticas/objetos",  # typo?
    "/objeto",
    "/objetos",
    "/postagem/objetos",
    "/postagens/objetos",
]

print("\nTentando diferentes variações de rota:\n")

for rota in rotas:
    try:
        r = requests.get(f"{base_url}{rota}", headers=headers, timeout=10)
        
        if r.status_code == 200:
            try:
                data = r.json()
                qtd = len(data.get("data", []))
                print(f"✅ {rota:<30} → 200 OK ({qtd} items)")
            except:
                print(f"✅ {rota:<30} → 200 OK (resposta inválida)")
        else:
            print(f"❌ {rota:<30} → {r.status_code}")
    except Exception as e:
        print(f"❌ {rota:<30} → ERRO")

print()
