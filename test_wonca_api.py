#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para API Wonca Labs (SiteRastreio)
Testa com código de rastreio: AD292694916BR
"""

import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Variáveis de ambiente
API_KEY = os.getenv('WONCA_API_KEY')
API_URL = os.getenv('WONCA_API_URL', 'https://api-labs.wonca.com.br')
SERVICE_PATH = os.getenv('WONCA_SERVICE_PATH', 'wonca.labs.v1.LabsService/Track')

# Código de rastreio para teste
TRACKING_CODE = 'AD292694916BR'

print("=" * 70)
print("🔍 TESTE DE INTEGRAÇÃO - WONCA LABS API (SiteRastreio)")
print("=" * 70)
print(f"\n📋 Configuração:")
print(f"  ✓ API URL: {API_URL}")
print(f"  ✓ Service: {SERVICE_PATH}")
print(f"  ✓ API Key: {API_KEY[:20]}...***")
print(f"  ✓ Código de Rastreio: {TRACKING_CODE}")
print("\n" + "=" * 70)

def tracking_wonca(tracking_code):
    """Busca rastreamento na API Wonca Labs"""
    
    url = f"{API_URL}/{SERVICE_PATH}"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Apikey {API_KEY}'
    }
    
    payload = {
        "code": tracking_code
    }
    
    print(f"\n📤 Enviando requisição POST")
    print(f"   URL: {url}")
    print(f"   Headers: {{'Content-Type': 'application/json', 'Authorization': 'Apikey ***'}}")
    print(f"   Payload: {json.dumps(payload, indent=4)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        print(f"\n✅ Resposta recebida:")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code in [200, 201]:
            try:
                data = response.json()
                print(f"\n📦 DADOS DO RASTREAMENTO:")
                print(json.dumps(data, indent=4, ensure_ascii=False))
                
                # Salva resultado
                resultado = {
                    'timestamp': datetime.now().isoformat(),
                    'codigo': tracking_code,
                    'status_http': response.status_code,
                    'dados': data
                }
                
                with open('resultado_rastreio_wonca.json', 'w', encoding='utf-8') as f:
                    json.dump(resultado, f, indent=4, ensure_ascii=False)
                
                print(f"\n✅ Resultado salvo em: resultado_rastreio_wonca.json")
                return True
                
            except json.JSONDecodeError as e:
                print(f"   ⚠️  Response não é JSON válido")
                print(f"   Body: {response.text[:500]}")
        else:
            print(f"\n⚠️  Erro HTTP {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout na requisição (15s)")
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Erro de conexão: {str(e)}")
    except Exception as e:
        print(f"   ❌ Erro inesperado: {str(e)}")
    
    return False

def test_connection():
    """Testa a conexão básica com a API"""
    print("\n\n" + "=" * 70)
    print("🔗 TESTE DE CONECTIVIDADE")
    print("=" * 70)
    
    url = f"{API_URL}/"
    headers = {
        'Authorization': f'Apikey {API_KEY}'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"\n✅ API acessível!")
        print(f"   Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"\n⚠️  Erro ao conectar: {str(e)}")
        return False

# Executar testes
if __name__ == "__main__":
    if not API_KEY:
        print("❌ ERRO: WONCA_API_KEY não configurada no .env")
        exit(1)
    
    # Teste de conexão
    test_connection()
    
    # Teste de rastreamento
    print("\n\n" + "=" * 70)
    print("📦 TESTE DE RASTREAMENTO COM API WONCA")
    print("=" * 70)
    
    success = tracking_wonca(TRACKING_CODE)
    
    if not success:
        print("\n\n⚠️  Falha na requisição")
        print("Possíveis causas:")
        print("  1. API Key inválida ou expirada")
        print("  2. Código de rastreio inválido")
        print("  3. Problema com conectividade")
        print("  4. API fora do ar")
