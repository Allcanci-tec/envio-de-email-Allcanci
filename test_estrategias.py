#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tentar /logisticas/objetos com diferentes estratégias.
"""

import requests
from bling_auth import get_token

token = get_token()
base_url = "https://api.bling.com.br/Api/v3"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

estrategias = [
    ("GET", "/logisticas/objetos", None),
    ("GET", "/logisticas/objetos", {"transportadora": 151483}),  # Correios
    ("GET", "/logisticas/objetos", {"filtro": "correios"}),
    ("POST", "/logisticas/objetos", {"filtro": "correios"}),
    ("GET", "/logistica/objetos", None),
    ("GET", "/logisticas/objeto", None),
]

print("\n" + "="*100)
print("  TESTANDO /logisticas/objetos COM DIFERENTES ESTRATEGIAS")
print("="*100 + "\n")

for metodo, rota, dados in estrategias:
    try:
        url = f"{base_url}{rota}"
        
        if metodo == "GET":
            r = requests.get(url, headers=headers, params=dados, timeout=10)
            status_msg = f"GET {rota}"
            if dados:
                status_msg += f" com params {dados}"
        else:
            r = requests.post(url, headers=headers, json=dados, timeout=10)
            status_msg = f"POST {rota}"
            if dados:
                status_msg += f" com body {dados}"
        
        print(f"  {metodo} {rota:<30}", end=" → ")
        
        if r.status_code == 200:
            try:
                json_data = r.json()
                qtd = len(json_data.get("data", []))
                print(f"✅ 200 ({qtd} items)")
                
                # Se funcionou, mostrar primeiro item
                if qtd > 0:
                    primeiro = json_data["data"][0]
                    print(f"       Primeiro item chaves: {list(primeiro.keys())[:5]}")
            except:
                print(f"✅ 200 (resposta inválida)")
        else:
            print(f"❌ {r.status_code}")
    
    except Exception as e:
        print(f"  {metodo} {rota:<30} → ❌ ERRO: {str(e)[:30]}")

print("\n" + "="*100 + "\n")
