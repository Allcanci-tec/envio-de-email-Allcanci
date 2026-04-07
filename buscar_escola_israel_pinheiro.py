#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUSCA ESPECÍFICA - Encontrar vendedor de "Escola Municipal Israel Pinheiro"
"""

import json
import requests
from bling_auth import get_token
from vendedor_service import buscar_vendedor

BLING_API = 'https://api.bling.com.br/v3'

def headers_bling_local():
    """Retorna headers com token"""
    token = get_token()
    return {'Authorization': f'Bearer {token}'}

print("\n" + "=" * 80)
print("BUSCANDO: Escola Municipal Israel Pinheiro")
print("=" * 80 + "\n")

# Buscar todos os pedidos Correios
for pagina in range(1, 20):
    try:
        resp = requests.get(
            f'{BLING_API}/pedidos/vendas',
            headers=headers_bling_local(),
            params={
                'pagina': pagina,
                'limite': 100,
                'idLogistica': 151483,  # Correios
            },
            timeout=15,
        )
        
        if resp.status_code != 200:
            break
        
        dados = resp.json().get('data', [])
        if not dados:
            break
        
        print(f"Verificando página {pagina}...\n")
        
        for pedido_resumido in dados:
            numero = pedido_resumido.get('numero')
            pedido_id = pedido_resumido.get('id')
            
            # Buscar detalhe do pedido
            try:
                r2 = requests.get(
                    f'{BLING_API}/pedidos/vendas/{pedido_id}',
                    headers=headers_bling_local(),
                    timeout=10,
                )
                
                if r2.status_code == 200:
                    pedido = r2.json().get('data', {})
                    cliente = pedido.get('contato', {}).get('nome', '').upper()
                    
                    # Procurar pela escola
                    if 'ISRAEL PINHEIRO' in cliente:
                        print(f"✅ ENCONTRADO!")
                        print(f"   Pedido: {numero}")
                        print(f"   Cliente: {cliente}")
                        
                        vendedor_id = pedido.get('vendedor', {}).get('id')
                        print(f"   Vendor ID: {vendedor_id}")
                        
                        if vendedor_id and vendedor_id != 0:
                            # Buscar dados do vendedor
                            dados_vend = buscar_vendedor(vendedor_id)
                            print(f"\n   📋 VENDEDOR ENCONTRADO:")
                            print(f"   - ID: {vendedor_id}")
                            print(f"   - Nome: {dados_vend.get('nome')}")
                            print(f"   - Email: {dados_vend.get('email')}")
                            print(f"   - Sucesso: {dados_vend.get('sucesso')}")
                        else:
                            print(f"   ⚠️ SEM VENDEDOR ASSOCIADO!")
                        
                        print()
            except Exception as e:
                pass
    
    except Exception as e:
        print(f"Erro na página {pagina}: {e}")
        break

print("\n" + "=" * 80)
print("Busca concluída")
print("=" * 80)
