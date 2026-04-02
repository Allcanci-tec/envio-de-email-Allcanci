#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para explorar os endpoints da API SiteRastreio
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('SITERASTREIO_API_KEY')
DOMAIN = os.getenv('SITERASTREIO_DOMAIN')
API_URL = os.getenv('SITERASTREIO_API_URL', 'https://api.siterastreio.com.br')
TRACKING_CODE = 'AD292694916BR'

print("🔍 Explorando endpoints da API SiteRastreio...\n")

headers_list = [
    {
        'name': 'Com Bearer Token',
        'headers': {
            'Authorization': f'Bearer {API_KEY}',
            'X-Domain': DOMAIN
        }
    },
    {
        'name': 'Com API Key como parâmetro',
        'headers': {
            'X-API-Key': API_KEY,
            'X-Domain': DOMAIN
        }
    },
    {
        'name': 'Com API Key simples',
        'headers': {
            'Authorization': API_KEY,
            'X-Domain': DOMAIN
        }
    },
]

endpoints = [
    '/',
    '/api',
    '/api/',
    '/docs',
    '/swagger',
    '/swagger.json',
    '/openapi.json',
    '/api/tracking',
    '/api/tracking/' + TRACKING_CODE,
    '/api/track',
    '/api/track/' + TRACKING_CODE,
    '/track',
    '/tracking',
    '/rastreio',
    '/rastreio/' + TRACKING_CODE,
]

for endpoint in endpoints:
    url = f"{API_URL}{endpoint}"
    
    for header_set in headers_list:
        try:
            response = requests.get(url, headers=header_set['headers'], timeout=5)
            
            if response.status_code != 404:
                print(f"✅ {endpoint} [{header_set['name']}]")
                print(f"   Status: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                
                if response.status_code == 200:
                    try:
                        print(f"   Data: {response.json()}")
                    except:
                        print(f"   Body: {response.text[:200]}")
                print()
        except Exception as e:
            pass

# Tentar com query parameters
print("\n\n🔗 Testando com query parameters...\n")

params_list = [
    {'code': TRACKING_CODE},
    {'tracking_code': TRACKING_CODE},
    {'numero': TRACKING_CODE},
    {'api_key': API_KEY, 'code': TRACKING_CODE},
]

endpoints2 = ['/', '/track', '/tracking', '/rastreio', '/api/track', '/api/tracking']

for endpoint in endpoints2:
    for params in params_list:
        url = f"{API_URL}{endpoint}"
        
        try:
            response = requests.get(
                url,
                params=params,
                headers={'X-Domain': DOMAIN},
                timeout=5
            )
            
            if response.status_code != 404:
                print(f"✅ {endpoint} - Params: {params}")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:300]}")
                print()
        except:
            pass

# Se ainda não conseguiu, tentar POST
print("\n\n📤 Testando com POST...\n")

post_endpoints = ['/track', '/tracking', '/rastreio', '/api/track', '/api/tracking', '/']

payload = {
    'codigo': TRACKING_CODE,
    'code': TRACKING_CODE,
    'tracking_code': TRACKING_CODE,
}

for endpoint in post_endpoints:
    url = f"{API_URL}{endpoint}"
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                'Authorization': f'Bearer {API_KEY}',
                'X-Domain': DOMAIN,
                'Content-Type': 'application/json'
            },
            timeout=5
        )
        
        if response.status_code != 404:
            print(f"✅ POST {endpoint}")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            print()
    except:
        pass
