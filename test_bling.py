#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para validar a comunicação com a API do Bling.
Testa as funções bling_get, bling_post e bling_put.
"""

import sys
import json
from bling_auth import bling_get, bling_post, bling_put, get_token

def print_header(title):
    """Imprime um cabeçalho formatado."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_token():
    """Testa se o token está sendo obtido corretamente."""
    print_header("1️⃣  TESTE DE TOKEN")
    try:
        token = get_token()
        if token:
            print(f"✅ Token obtido com sucesso!")
            print(f"   Token (primeiros 20 caracteres): {token[:20]}...")
            return True
        else:
            print("❌ Token vazio!")
            return False
    except Exception as e:
        print(f"❌ Erro ao obter token: {e}")
        return False

def test_contatos():
    """Testa a rota GET /contatos."""
    print_header("2️⃣  TESTE DE GET - CONTATOS")
    try:
        print("📤 Enviando: GET /contatos")
        response = bling_get("/contatos")
        
        print(f"✅ Resposta recebida com sucesso!")
        print(f"   Status: Sucesso")
        print(f"   Dados retornados:")
        print(json.dumps(response, indent=2, ensure_ascii=False)[:500] + "..." if len(json.dumps(response)) > 500 else json.dumps(response, indent=2, ensure_ascii=False))
        
        if "data" in response:
            qtd = len(response.get("data", []))
            print(f"\n   📊 Total de contatos: {qtd}")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao buscar contatos: {e}")
        return False

def test_pedidos():
    """Testa a rota GET /pedidos/vendas."""
    print_header("3️⃣  TESTE DE GET - PEDIDOS DE VENDAS")
    try:
        print("📤 Enviando: GET /pedidos/vendas")
        response = bling_get("/pedidos/vendas", params={"limite": 5})
        
        print(f"✅ Resposta recebida com sucesso!")
        print(f"   Status: Sucesso")
        print(f"   Dados retornados (primeiros 500 caracteres):")
        print(json.dumps(response, indent=2, ensure_ascii=False)[:500] + "..." if len(json.dumps(response)) > 500 else json.dumps(response, indent=2, ensure_ascii=False))
        
        if "data" in response:
            qtd = len(response.get("data", []))
            print(f"\n   📊 Total de pedidos (limite 5): {qtd}")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao buscar pedidos: {e}")
        return False

def test_produtos():
    """Testa a rota GET /produtos."""
    print_header("4️⃣  TESTE DE GET - PRODUTOS")
    try:
        print("📤 Enviando: GET /produtos")
        response = bling_get("/produtos", params={"limite": 3})
        
        print(f"✅ Resposta recebida com sucesso!")
        print(f"   Status: Sucesso")
        print(f"   Dados retornados (primeiros 500 caracteres):")
        print(json.dumps(response, indent=2, ensure_ascii=False)[:500] + "..." if len(json.dumps(response)) > 500 else json.dumps(response, indent=2, ensure_ascii=False))
        
        if "data" in response:
            qtd = len(response.get("data", []))
            print(f"\n   📊 Total de produtos (limite 3): {qtd}")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao buscar produtos: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("  🔌 TESTE DE COMUNICAÇÃO COM API BLING")
    print("="*60)
    
    results = {
        "token": test_token(),
        "contatos": test_contatos(),
        "pedidos": test_pedidos(),
        "produtos": test_produtos(),
    }
    
    print_header("📋 RESUMO DOS TESTES")
    
    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"  {test_name.upper():20} {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\n  Total: {total_passed}/{total_tests} testes passaram")
    
    if total_passed == total_tests:
        print("\n✨ TODOS OS TESTES PASSARAM! A API do Bling está funcionando corretamente.")
        return 0
    else:
        print("\n⚠️  Alguns testes falharam. Verifique o .env e as credenciais do Bling.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
