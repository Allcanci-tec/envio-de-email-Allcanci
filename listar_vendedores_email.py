#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bling_auth import bling_get

# Buscar todos os vendedores e seus emails
vendedores = bling_get('/vendedores', params={'limite': 100})

print('\n' + '='*80)
print('VENDEDORES COM CONTATOS E SEUS EMAILS')
print('='*80 + '\n')

count = 0
for v in vendedores.get('data', [])[:25]:
    v_id = v.get('id')
    contato_info = v.get('contato', {})
    nome = contato_info.get('nome', 'N/A')
    contato_id = contato_info.get('id')
    
    # Buscar email do contato
    email = ''
    if contato_id:
        try:
            contato = bling_get(f'/contatos/{contato_id}')
            email = contato.get('data', {}).get('email', '')
        except:
            pass
    
    print(f'ID: {v_id}')
    print(f'Nome: {nome}')
    print(f'Email: {email or "(sem email)"}')
    print('---')
    
    if email:
        count += 1

print(f'\nTotal com email: {count}')
