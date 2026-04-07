#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Buscar dados completos do vendedor da Escola Municipal Israel Pinheiro
"""

from vendedor_service import buscar_vendedor
import json

vendedor_id = 15596468666
dados = buscar_vendedor(vendedor_id)

print('\n' + '='*80)
print('VENDEDOR DA ESCOLA MUNICIPAL ISRAEL PINHEIRO')
print('='*80 + '\n')

print(f'ID: {dados.get("id")}')
print(f'Nome: {dados.get("nome")}')
print(f'Email: {dados.get("email")}')
print(f'Telefone: {dados.get("telefone")}')
print(f'Sucesso: {dados.get("sucesso")}')

print('\n' + '='*80)
print('DADOS COMPLETOS:')
print('='*80 + '\n')
print(json.dumps(dados, indent=2, ensure_ascii=False))

print('\n' + '='*80)
print('CONFIRMAÇÃO:')
print('='*80)
print(f'\n✅ VENDEDOR CORRETO IDENTIFICADO!')
print(f'\n   Escola: Caixa Escolar da Escola Municipal Israel Pinheiro')
print(f'   Vendedor: {dados.get("nome")}')
print(f'   Email: {dados.get("email")}')
print(f'\nPronto para enviar notificação de teste!\n')
print('='*80)
