#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inspecionar a estrutura da resposta de /logisticas.
"""

import json
from bling_auth import bling_get

def main():
    print("\n" + "="*80)
    print("  🔍 INSPECCIONANDO ESTRUTURA DE /logisticas")
    print("="*80 + "\n")
    
    response = bling_get("/logisticas", params={"limite": 100})
    
    print("📋 Resposta JSON completa:")
    print(json.dumps(response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
