#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHECKLIST DE PRODUCAO - Verificação rápida
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

print("\n" + "="*80)
print("PRE-CHECKLIST DE PRODUCAO")
print("="*80 + "\n")

print("1. Arquivos Essenciais:")
files_ok = True
for f in ['automatico_producao.py', 'enviar_emails_rastreamento.py', 
          'whatsapp_service.py', 'contatos_rastreamento.json', '.env']:
    if Path(f).exists():
        print(f"   OK: {f}")
    else:
        print(f"   FALHA: {f}")
        files_ok = False

print("\n2. Configuracao .env:")
load_dotenv()
env_ok = True
for var, desc in [('EMAIL_REMETENTE', 'Email'), 
                  ('EMAIL_SENHA', 'Senha Email'),
                  ('BLING_ACCESS_TOKEN', 'Token Bling')]:
    if os.getenv(var):
        print(f"   OK: {desc}")
    else:
        print(f"   FALHA: {desc}")
        env_ok = False

print("\n3. Base de Clientes:")
try:
    with open('contatos_rastreamento.json', 'r', encoding='utf-8') as f:
        clientes = json.load(f)
    print(f"   OK: {len(clientes)} clientes")
except:
    print("   FALHA: Erro ao carregar")

print("\n" + "="*80)
if files_ok and env_ok:
    print("STATUS: TUDO OK - PRONTO PARA PRODUCAO!")
    print("="*80)
    print("\nPROXIMO PASSO:")
    print("  python automatico_producao.py")
    print("\nO sistema rodara continuamente a cada 5 minutos.")
else:
    print("STATUS: FALHAS ENCONTRADAS")
    print("="*80)

print()
