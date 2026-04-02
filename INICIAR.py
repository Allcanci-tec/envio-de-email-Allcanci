#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 INICIAR SISTEMA AUTOMÁTICO DE RASTREAMENTO
Production Ready - Validação Completa
"""

import os
import json
import sys
from datetime import datetime

print('\n' + '='*80)
print('🚀 SISTEMA AUTOMÁTICO DE RASTREAMENTO - INICIALIZAÇÃO')
print('='*80 + '\n')

# 1. Validar .env
print('📋 Validando configurações...\n')

required_env_vars = {
    'EMAIL_USUARIO': 'Email para envio (suporte1@allcanci.com.br)',
    'EMAIL_SENHA': 'Senha do email',
    'EMAIL_SMTP': 'Servidor SMTP (smtp.hostinger.com)',
    'EMAIL_PORTA': 'Porta SMTP (465)',
    'BLING_ACCESS_TOKEN': 'Token de acesso Bling',
}

if not os.path.exists('.env'):
    print('❌ Arquivo .env não encontrado!')
    print('\nCrie um arquivo .env com:')
    for var, descricao in required_env_vars.items():
        print(f'   {var}={descricao}')
    sys.exit(1)

print('✅ .env encontrado')

# 2. Validar tokens.json
if not os.path.exists('tokens.json'):
    print('❌ tokens.json não encontrado!')
    print('Execute primeiro: python bling_auth.py')
    sys.exit(1)

try:
    with open('tokens.json', 'r') as f:
        tokens = json.load(f)
    print('✅ tokens.json válido')
except:
    print('❌ tokens.json inválido!')
    sys.exit(1)

# 3. Validar contatos
if not os.path.exists('contatos_rastreamento.json'):
    print('❌ contatos_rastreamento.json não encontrado!')
    sys.exit(1)

try:
    with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
        contatos = json.load(f)
    print(f'✅ {len(contatos)} clientes carregados')
except:
    print('❌ contatos_rastreamento.json inválido!')
    sys.exit(1)

# 4. Validar config
if not os.path.exists('config_producao.json'):
    print('❌ config_producao.json não encontrado!')
    sys.exit(1)

try:
    with open('config_producao.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    print('✅ config_producao.json válido')
except:
    print('❌ config_producao.json inválido!')
    sys.exit(1)

# 5. Validar histórico
if not os.path.exists('historico_producao.json'):
    with open('historico_producao.json', 'w', encoding='utf-8') as f:
        json.dump({}, f)
    print('✅ historico_producao.json criado')
else:
    print('✅ historico_producao.json pronto')

print('\n' + '='*80)
print('✨ TODAS AS VALIDAÇÕES PASSARAM!')
print('='*80 + '\n')

print('📊 STATUS:')
print(f'   • Clientes: {len(contatos)}')
print(f'   • Com email: {sum(1 for c in contatos if c.get("email"))}')
print(f'   • Sem email: {sum(1 for c in contatos if not c.get("email"))}')
print(f'   • Ciclo: A cada 5 minutos')

print('\n' + '='*80)
print('🎯 INICIANDO SISTEMA...')
print('='*80 + '\n')

# Importar e rodar
try:
    from automatico_producao import main
    main()
except KeyboardInterrupt:
    print('\n\n❌ Sistema parado pelo usuário')
    print('='*80)
except Exception as e:
    print(f'\n❌ Erro ao iniciar: {str(e)}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
