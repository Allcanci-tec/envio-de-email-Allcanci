#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUSCA EM CONTATO - Procurar por vendedor/fornecedor no contato da escola
"""

import json
from bling_auth import bling_get

print("\n" + "=" * 80)
print("ANÁLISE DO CONTATO DA ESCOLA - PROCURANDO VENDEDOR/FORNECEDOR")
print("=" * 80 + "\n")

try:
    # ID do contato da escola: 17996162790
    contato_id = 17996162790
    
    print(f"Buscando dados do contato ID: {contato_id}\n")
    
    contato_data = bling_get(f'/contatos/{contato_id}')
    contato = contato_data.get('data', {})
    
    # Salvar estrutura completa
    with open('contato_israel_pinheiro_completo.json', 'w', encoding='utf-8') as f:
        json.dump(contato, f, indent=2, ensure_ascii=False)
    
    print("✅ Dados salvos em: contato_israel_pinheiro_completo.json\n")
    
    print("=" * 80)
    print("ESTRUTURA DO CONTATO:")
    print("=" * 80 + "\n")
    
    # Exibir informações básicas
    print(f"Tipo: {contato.get('tipoPessoa')}")
    print(f"Nome: {contato.get('nome')}")
    print(f"Documento: {contato.get('numeroDocumento')}")
    print(f"Email: {contato.get('email')}")
    print(f"Categoria: {contato.get('categoria')}\n")
    
    # Procurar por campos de vendedor
    print("=" * 80)
    print("CAMPOS RELACIONADOS A VENDEDOR/FORNECEDOR:")
    print("=" * 80 + "\n")
    
    # Verificar todos os campos
    for chave in sorted(contato.keys()):
        valor = contato[chave]
        
        # Procurar por palavras-chave
        if 'vend' in chave.lower() or 'forn' in chave.lower() or 'gerente' in chave.lower() or 'responsavel' in chave.lower():
            print(f"🔍 {chave}: {valor}")
        
        # Se for dict, exibir conteúdo
        if isinstance(valor, dict) and len(str(valor)) < 500:
            print(f"📋 {chave}:")
            for k, v in valor.items():
                if 'vend' in k.lower() or 'forn' in k.lower() or 'gerente' in k.lower():
                    print(f"   → {k}: {v}")
        
        # Se for array, verificar
        if isinstance(valor, list) and len(valor) > 0:
            print(f"📦 {chave}: ({len(valor)} itens)")
            for i, item in enumerate(valor):
                if isinstance(item, dict):
                    # Procurar em dicts dentro do array
                    for k, v in item.items():
                        if 'vend' in str(k).lower() or 'forn' in str(v).lower():
                            print(f"   Item {i}: {k} = {v}")
    
    print("\n" + "=" * 80)
    print("TODOS OS CAMPOS DO CONTATO:")
    print("=" * 80 + "\n")
    
    for chave in sorted(contato.keys()):
        valor = contato[chave]
        if isinstance(valor, dict):
            print(f"  ⚙️ {chave}: {json.dumps(valor, ensure_ascii=False)}")
        elif isinstance(valor, list):
            print(f"  📦 {chave}: {len(valor)} itens")
            if len(valor) > 0:
                print(f"      Exemplo: {json.dumps(valor[0], ensure_ascii=False)[:100]}...")
        else:
            print(f"  📄 {chave}: {valor}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
