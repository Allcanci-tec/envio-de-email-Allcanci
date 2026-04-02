#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIMPAR SESSAO WHATSAPP
Execute este script para deletar a sessao salva e comeca do zero
Util quando a sessao expirou ou o QR Code foi lido incorretamente
"""

import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent
WHATSAPP_SESSION_DIR = BASE_DIR / 'whatsapp_session'

print()
print("="*70)
print("LIMPADOR DE SESSAO WHATSAPP")
print("="*70)
print()

if WHATSAPP_SESSION_DIR.exists():
    print(f"Deletando: {WHATSAPP_SESSION_DIR}")
    try:
        shutil.rmtree(WHATSAPP_SESSION_DIR)
        print("✓ Sessao deletada com sucesso!")
        print()
        print("PROXIMOS PASSOS:")
        print("  1. Execute: python whatsapp_service.py")
        print("  2. O navegador vai abrir")
        print("  3. Escaneie o QR Code com seu celular")
        print("  4. Aguarde ate a mensagem ser enviada")
        print()
    except Exception as e:
        print(f"✗ Erro ao deletar: {e}")
else:
    print(f"Pasta nao encontrada: {WHATSAPP_SESSION_DIR}")
    print("Nada para limpar.")
    print()

print("="*70)
print()
