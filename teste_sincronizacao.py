#!/usr/bin/env python3
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def carregar_token():
    if not os.path.exists('tokens.json'):
        raise FileNotFoundError('tokens.json não encontrado')
    with open('tokens.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    return dados.get('access_token')

def headers_bling():
    token = carregar_token()
    return {'Authorization': f'Bearer {token}'}

print('TESTE DE SINCRONIZAÇÃO')
print('=' * 60)

print('\n1. Verificando tokens...')
try:
    token = carregar_token()
    print(f'   ✅ Token carregado: {token[:20]}...')
except Exception as e:
    print(f'   ❌ ERRO: {e}')
    exit(1)

print('\n2. Montando headers...')
try:
    headers = headers_bling()
    print(f'   ✅ Headers: {headers}')
except Exception as e:
    print(f'   ❌ ERRO: {e}')
    exit(1)

print('\n3. Testando requisição inicial ao Bling...')
try:
    print('   Enviando GET /pedidos/vendas (página 1)...')
    resp = requests.get(
        'https://api.bling.com.br/v3/pedidos/vendas',
        headers=headers,
        params={
            'pagina': 1,
            'limite': 10,
            'idLogistica': 151483,
        },
        timeout=15,
    )
    print(f'   ✅ Status: {resp.status_code}')
    print(f'   ✅ Response length: {len(resp.text)} chars')
    
    data = resp.json()
    pedidos = data.get('data', [])
    print(f'   ✅ Pedidos retornados: {len(pedidos)}')
    
    if pedidos:
        primeiro = pedidos[0]
        print(f'\n   Primeiro pedido:')
        print(f'     - Número: {primeiro.get("numero")}')
        print(f'     - ID: {primeiro.get("id")}')
        
except requests.Timeout:
    print(f'   ❌ TIMEOUT - requisição demorou mais de 15 segundos')
except requests.ConnectionError as e:
    print(f'   ❌ ERRO DE CONEXÃO: {e}')
except Exception as e:
    print(f'   ❌ ERRO: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '=' * 60)
print('Teste concluído')
