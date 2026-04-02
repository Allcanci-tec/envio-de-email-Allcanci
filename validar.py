#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import sys

print('\n' + '='*80)
print('SISTEMA AUTOMATICO DE RASTREAMENTO - INICIALIZACAO')
print('='*80 + '\n')

print('Validando configuracoes...\n')

# 1. Validar .env
if not os.path.exists('.env'):
    print('ERRO: .env nao encontrado!')
    sys.exit(1)

print('[OK] .env encontrado')

# 2. Validar tokens.json
if not os.path.exists('tokens.json'):
    print('[ERRO] tokens.json nao encontrado!')
    sys.exit(1)

with open('tokens.json', 'r') as f:
    tokens = json.load(f)

print('[OK] tokens.json valido')

# 3. Validar contatos
with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
    contatos = json.load(f)

print(f'[OK] {len(contatos)} clientes carregados')

# 4. Validar config
with open('config_producao.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

print('[OK] config_producao.json valido')

# 5. Validar histórico
if not os.path.exists('historico_producao.json'):
    with open('historico_producao.json', 'w', encoding='utf-8') as f:
        json.dump({}, f)
    print('[OK] historico_producao.json criado')
else:
    print('[OK] historico_producao.json pronto')

print('\n' + '='*80)
print('OK! TODAS AS VALIDACOES PASSARAM!')
print('='*80 + '\n')

print('STATUS:')
print(f'  Clientes: {len(contatos)}')
print(f'  Com email: {sum(1 for c in contatos if c.get("email"))}')
print(f'  Sem email: {sum(1 for c in contatos if not c.get("email"))}')
print(f'  Ciclo: A cada 5 minutos')

print('\n' + '='*80)
print('SISTEMA PRONTO PARA INICIAR')
print('='*80 + '\n')

print('Para iniciar de verdade, execute:')
print('  python automatico_producao.py\n')
