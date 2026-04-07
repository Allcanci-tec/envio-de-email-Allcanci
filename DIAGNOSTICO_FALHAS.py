#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO: Por que está falhando ao consultar Bling?
"""

import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("DIAGNÓSTICO: FALHAS AO CONSULTAR BLING")
print("="*80 + "\n")

# 1. Verificar tokens.json
print("1. VERIFICANDO TOKEN:")
if os.path.exists('tokens.json'):
    try:
        with open('tokens.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        token = dados.get('access_token')
        if token:
            print(f"   ✓ Token encontrado: {token[:20]}...")
            print(f"   ✓ Comprimento: {len(token)} caracteres")
            
            # Verificar se token é válido (Bearer format)
            if len(token) > 30 and not ' ' in token:
                print(f"   ✓ Formato válido (sem espaços)")
            else:
                print(f"   ✗ AVISO: Token parece inválido")
        else:
            print(f"   ✗ Token NÃO encontrado em tokens.json")
    except Exception as e:
        print(f"   ✗ ERRO ao ler tokens.json: {e}")
else:
    print(f"   ✗ ERRO: tokens.json não existe!")

# 2. Verificar contatos
print("\n2. VERIFICANDO CONTATOS:")
if os.path.exists('contatos_rastreamento.json'):
    with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
        contatos = json.load(f)
    
    print(f"   ✓ {len(contatos)} clientes carregados")
    
    # Contadores
    com_volume = sum(1 for c in contatos if c.get('volume_id'))
    sem_volume = len(contatos) - com_volume
    
    print(f"   ✓ Com volume_id: {com_volume}")
    print(f"   ✗ Sem volume_id: {sem_volume}")
    
    # Mostrar primeiros 3 com volume_id
    if com_volume > 0:
        print(f"\n   Primeiros 3 com volume_id:")
        count = 0
        for c in contatos:
            if c.get('volume_id') and count < 3:
                print(f"     • Pedido {c['numero']}: volume_id = {c['volume_id']}")
                count += 1
else:
    print(f"   ✗ contatos_rastreamento.json não existe!")
    exit(1)

# 3. Testar conexão com Bling
print("\n3. TESTANDO CONEXÃO COM BLING:")

BLING_API = 'https://api.bling.com.br/v3'

try:
    with open('tokens.json', 'r', encoding='utf-8') as f:
        token = json.load(f)['access_token']
    
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"   • Testando com Bearer token...")
    
    # Tentar requisição simples
    resp = requests.get(
        f'{BLING_API}/pedidos/vendas?pagina=1&limite=1',
        headers=headers,
        timeout=10
    )
    
    print(f"   ✓ Status: {resp.status_code}")
    
    if resp.status_code == 200:
        print(f"   ✓ CONEXÃO OK - API respondendo")
        dados = resp.json()
        if 'data' in dados:
            print(f"   ✓ Estrutura JSON correta")
    elif resp.status_code == 401:
        print(f"   ✗ ERRO 401: Token inválido ou expirado!")
    elif resp.status_code == 403:
        print(f"   ✗ ERRO 403: Sem permissão")
    else:
        print(f"   ✗ Erro HTTP {resp.status_code}")
    
    print(f"   Resposta: {resp.text[:200]}")
    
except Exception as e:
    print(f"   ✗ ERRO: {type(e).__name__}: {e}")

# 4. Testar rastreamento específico
print("\n4. TESTANDO RASTREAMENTO (se houver volume_id):")

com_volume = [c for c in contatos if c.get('volume_id')]
if com_volume:
    teste = com_volume[0]
    volume_id = teste['volume_id']
    
    print(f"   Testando: Pedido {teste['numero']}, volume_id = {volume_id}")
    
    try:
        resp = requests.get(
            f'{BLING_API}/logisticas/objetos/{volume_id}',
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code == 200:
            dados = resp.json().get('data', {})
            rastreamento = dados.get('rastreamento', {})
            
            if rastreamento:
                print(f"   ✓ Rastreamento encontrado!")
                print(f"     • Descrição: {rastreamento.get('descricao', 'N/A')}")
                print(f"     • Última alteração: {rastreamento.get('ultimaAlteracao', 'N/A')}")
            else:
                print(f"   ✗ Sem dados de rastreamento para este volume")
        else:
            print(f"   ✗ Status {resp.status_code}")
            print(f"   Resposta: {resp.text[:200]}")
    
    except Exception as e:
        print(f"   ✗ ERRO: {type(e).__name__}: {e}")
else:
    print(f"   ⚠️  Sem clientes com volume_id para testar")

# 5. Resumo
print("\n" + "="*80)
print("RESUMO DO DIAGNÓSTICO:")
print("="*80 + "\n")

diagnóstico = {
    'Token': 'OK' if os.path.exists('tokens.json') else 'FALHA',
    'Contatos': f'{len(contatos)} carregados' if os.path.exists('contatos_rastreamento.json') else 'FALHA',
    'Conexão Bling': 'OK' if resp and resp.status_code in [200, 401] else 'FALHA',
}

for chave, valor in diagnóstico.items():
    status = '✓' if 'OK' in valor or 'carregado' in valor else '✗'
    print(f"{status} {chave}: {valor}")

print()
