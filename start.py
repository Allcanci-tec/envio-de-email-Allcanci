#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime

print("\n" + "="*70)
print("🚀 INICIALIZADOR SISTEMA AUTOMÁTICO DE RASTREAMENTO")
print("="*70 + "\n")

# Validar .env
if not os.path.exists('.env'):
    print("❌ Arquivo .env não encontrado!")
    print("   Crie com:")
    print("   EMAIL_USUARIO=suporte1@allcanci.com.br")
    print("   EMAIL_SENHA=sua_senha")
    print("   ACCESS_TOKEN=seu_token_bling")
    exit(1)

print("✅ .env encontrado")

# Validar tokens.json
if not os.path.exists('tokens.json'):
    print("❌ tokens.json não encontrado!")
    exit(1)

print("✅ tokens.json encontrado")

# Validar contatos_rastreamento.json
if not os.path.exists('contatos_rastreamento.json'):
    print("❌ contatos_rastreamento.json não encontrado!")
    exit(1)

with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
    contatos = json.load(f)

print(f"✅ Carregados {len(contatos)} clientes")

# Contar com email
com_email = sum(1 for c in contatos if c.get('email'))
print(f"   📧 Com email: {com_email}")
print(f"   ⚠️  Sem email: {len(contatos) - com_email}")

# Inicializar histórico
if not os.path.exists('historico_producao.json'):
    with open('historico_producao.json', 'w', encoding='utf-8') as f:
        json.dump({}, f)
    print("✅ Histórico inicializado")
else:
    print("✅ Histórico já existe")

print("\n" + "="*70)
print("✨ SISTEMA PRONTO PARA INICIAR!")
print("="*70)
print("\nPara iniciar, execute:")
print("   python automatico_producao.py")
print("\nO sistema vai:")
print("   ✓ Monitorar TODOS os 14 clientes")
print("   ✓ Verificar a cada 5 minutos")
print("   ✓ Enviar email APENAS se status mudar")
print("   ✓ Evitar emails para quem já recebeu")
print("   ✓ Ignorar pedidos entregues")
print("   ✓ Gerar log completo em rastreamento.log")
print("\n" + "="*70 + "\n")
