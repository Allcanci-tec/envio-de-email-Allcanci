#!/usr/bin/env python3
import json, requests
from dotenv import load_dotenv
load_dotenv()

with open('tokens.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)
token = dados['access_token']
headers = {'Authorization': f'Bearer {token}'}

BLING_API = 'https://api.bling.com.br/v3'

# Buscar os pedidos mais recentes
resp = requests.get(f'{BLING_API}/pedidos/vendas', headers=headers, params={'pagina': 1, 'limite': 5})
pedidos = resp.json().get('data', [])

for p in pedidos[:2]:
    pid = p.get('id')
    r2 = requests.get(f'{BLING_API}/pedidos/vendas/{pid}', headers=headers)
    pedido = r2.json().get('data', {})
    contato_id = pedido.get('contato', {}).get('id')
    if not contato_id:
        continue

    rc = requests.get(f'{BLING_API}/contatos/{contato_id}', headers=headers)
    c = rc.json().get('data', {})

    print(f"\n{'='*60}")
    print(f"CONTATO: {c.get('nome')}")
    print(f"{'='*60}")
    print(json.dumps(c, indent=2, ensure_ascii=False))
    print()
    break
