#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste do novo sistema de refresh automático.
"""

import sys
import json
from bling_auth import bling_get, get_token_info, get_token

def main():
    print("\n" + "="*60)
    print("  ✅ TESTE DO SISTEMA DE REFRESH AUTOMÁTICO")
    print("="*60 + "\n")
    
    # 1. Verificar status do token
    print("1️⃣  STATUS DO TOKEN ATUAL")
    print("-" * 60)
    info = get_token_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    print()
    
    # 2. Testar GET /contatos
    print("2️⃣  TESTE DE API - GET /contatos")
    print("-" * 60)
    try:
        contatos = bling_get("/contatos")
        print("✅ Requisição bem-sucedida!\n")
        print("📋 Resposta (primeiros 500 caracteres):")
        print(json.dumps(contatos, indent=2, ensure_ascii=False)[:500])
        
        if "data" in contatos:
            print(f"\n📊 Total de contatos: {len(contatos['data'])}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
