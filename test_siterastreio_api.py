#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para integração com API SiteRastreio
Testa com código de rastreio: AD292694916BR
"""

import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Variáveis de ambiente
API_KEY = os.getenv('SITERASTREIO_API_KEY')
DOMAIN = os.getenv('SITERASTREIO_DOMAIN')
API_URL = os.getenv('SITERASTREIO_API_URL', 'https://api.siterastreio.com.br')

# Código de rastreio para teste
TRACKING_CODE = 'AD292694916BR'

print("=" * 70)
print("🔍 TESTE DE INTEGRAÇÃO COM API SITERASTREIO")
print("=" * 70)
print(f"\n📋 Configuração:")
print(f"  ✓ API URL: {API_URL}")
print(f"  ✓ Domínio: {DOMAIN}")
print(f"  ✓ API Key: {API_KEY[:20]}...***")
print(f"  ✓ Código de Rastreio: {TRACKING_CODE}")
print("\n" + "=" * 70)

def test_tracking(tracking_code):
    """Testa rastreamento de um código"""
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
        'X-Domain': DOMAIN
    }
    
    # Tenta diferentes endpoints possíveis
    endpoints = [
        f"/track/{tracking_code}",
        f"/tracking/{tracking_code}",
        f"/rastreamento/{tracking_code}",
        f"/v1/track/{tracking_code}",
    ]
    
    for endpoint in endpoints:
        url = f"{API_URL}{endpoint}"
        print(f"\n🔗 Testando: {url}")
        print(f"   Headers: Authorization, X-Domain={DOMAIN}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"\n   Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n   ✅ SUCESSO! Dados recebidos:")
                print(f"   {json.dumps(data, indent=4, ensure_ascii=False)}")
                
                # Salva resultado
                with open('resultado_rastreio.json', 'w', encoding='utf-8') as f:
                    json.dump({
                        'timestamp': datetime.now().isoformat(),
                        'codigo': tracking_code,
                        'dados': data
                    }, f, indent=4, ensure_ascii=False)
                
                return True
            else:
                print(f"   ⚠️  Erro: {response.status_code}")
                print(f"   Body: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erro na requisição: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"   ❌ Erro ao decodificar JSON: {str(e)}")
            print(f"   Body: {response.text[:200]}")
    
    return False

def test_api_health():
    """Testa a saúde da API"""
    print("\n\n" + "=" * 70)
    print("🏥 TESTE DE SAÚDE DA API")
    print("=" * 70)
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
        'X-Domain': DOMAIN
    }
    
    endpoints = [
        "/health",
        "/status",
        "/v1/health",
        "/ping",
    ]
    
    for endpoint in endpoints:
        url = f"{API_URL}{endpoint}"
        print(f"\n🔗 Testando: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 204]:
                print(f"   ✅ API está respondendo!")
                return True
        except Exception as e:
            print(f"   ⚠️  {str(e)[:50]}")
    
    return False

# Executar testes
if __name__ == "__main__":
    if not API_KEY or not DOMAIN:
        print("❌ ERRO: Variáveis de ambiente não configuradas!")
        print("   Verifique o arquivo .env")
        exit(1)
    
    # Teste de saúde
    test_api_health()
    
    # Teste de rastreamento
    print("\n\n" + "=" * 70)
    print("📦 TESTE DE RASTREAMENTO")
    print("=" * 70)
    
    success = test_tracking(TRACKING_CODE)
    
    if success:
        print("\n\n✅ INTEGRAÇÃO FUNCIONANDO!")
        print("Resultado salvo em: resultado_rastreio.json")
    else:
        print("\n\n⚠️  NENHUM ENDPOINT FUNCIONOU")
        print("Verificar:")
        print("  1. Se a API Key está correta")
        print("  2. Se o domínio está certo")
        print("  3. Se o código de rastreio é válido")
        print("  4. Se a API está acessível")
