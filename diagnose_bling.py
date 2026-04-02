#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para a integração com Bling.
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("BLING_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLING_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("BLING_REFRESH_TOKEN")
ACCESS_TOKEN = os.getenv("BLING_ACCESS_TOKEN")
TOKEN_URL = "https://www.bling.com.br/Api/v3/oauth/token"

print("\n" + "="*60)
print("  🔍 DIAGNÓSTICO - INTEGRAÇÃO BLING")
print("="*60 + "\n")

# 1. Verificar variáveis de ambiente
print("1️⃣  VERIFICAÇÃO DE VARIÁVEIS DE AMBIENTE")
print("-" * 60)

vars_check = {
    "BLING_CLIENT_ID": CLIENT_ID,
    "BLING_CLIENT_SECRET": CLIENT_SECRET,
    "BLING_ACCESS_TOKEN": ACCESS_TOKEN,
    "BLING_REFRESH_TOKEN": REFRESH_TOKEN,
}

all_vars_ok = True
for var_name, var_value in vars_check.items():
    if var_value:
        status = "✅"
        display = f"{var_value[:20]}..." if len(var_value) > 20 else var_value
    else:
        status = "❌"
        display = "NÃO CONFIGURADA"
        all_vars_ok = False
    print(f"  {status} {var_name:25} = {display}")

if not all_vars_ok:
    print("\n⚠️  Algumas variáveis de ambiente estão faltando!")
    print("    Verifique o arquivo .env\n")
    sys.exit(1)

print("\n✅ Todas as variáveis de ambiente estão configuradas!\n")

# 2. Tentar renovar o token
print("2️⃣  TENTATIVA DE RENOVAÇÃO DE TOKEN")
print("-" * 60)

print(f"  📤 POST para: {TOKEN_URL}")
print(f"  🔐 Client ID: {CLIENT_ID[:20]}...")
print(f"  🔄 Refresh Token: {REFRESH_TOKEN[:20]}...\n")

try:
    response = requests.post(
        TOKEN_URL,
        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers={"Accept": "application/json"},
        timeout=30,
    )
    
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {response.text}\n")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Token renovado com sucesso!")
        print(f"  📊 Novo Access Token: {data.get('access_token', 'N/A')[:20]}...")
        print(f"  ⏱️  Expira em: {data.get('expires_in', 'N/A')} segundos\n")
    else:
        print(f"  ❌ Erro ao renovar token (HTTP {response.status_code})")
        print(f"  Possíveis causas:")
        print(f"    - Refresh token expirou")
        print(f"    - Client ID/Secret inválidos")
        print(f"    - Token foi revogado")
        print(f"    - Credenciais incorretas\n")
        
except Exception as e:
    print(f"  ❌ Erro de conexão: {e}\n")

# 3. Tentar usar o access_token atual
print("3️⃣  TESTE COM ACCESS_TOKEN ATUAL")
print("-" * 60)

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept": "application/json",
}

print(f"  📤 GET para: https://api.bling.com.br/Api/v3/contatos")
print(f"  🔐 Access Token: {ACCESS_TOKEN[:20]}...\n")

try:
    response = requests.get(
        "https://api.bling.com.br/Api/v3/contatos",
        headers=headers,
        timeout=10,
    )
    
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Access token ainda é válido!")
        print(f"  📊 Resposta: {str(data)[:200]}...\n")
    elif response.status_code == 401:
        print(f"  ❌ Access token expirado ou inválido (401 Unauthorized)\n")
    else:
        print(f"  ⚠️  Status inesperado: {response.text}\n")
        
except Exception as e:
    print(f"  ❌ Erro ao conectar: {e}\n")

# 4. Resumo
print("4️⃣  RESUMO DO DIAGNÓSTICO")
print("-" * 60)

print("""
  📋 Para resolver o problema:

  1. Se o refresh_token está expirado:
     - Vá para: https://bling.com.br/b/oauth/autorizar
     - Autorize a aplicação novamente
     - Copie o novo token e atualize o .env

  2. Verifique se o CLIENT_ID e CLIENT_SECRET estão corretos
     - Eles devem vir da sua conta Bling

  3. Se o access_token ainda é válido:
     - O projeto deve funcionar normalmente
     - O refresh automático pode não estar funcionando

  ✨ Próximo passo: Verifique a autorização da app no Bling
""")
