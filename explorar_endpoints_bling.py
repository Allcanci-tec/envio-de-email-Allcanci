import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Carregar tokens
with open('tokens.json', 'r') as f:
    tokens = json.load(f)
    
ACCESS_TOKEN = tokens['access_token']
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# Tentar 1: Listar sem filtro de logistca para ver campos completos
print("=" * 80)
print("TENTATIVA 1: Listar pedidos SEM filtro de logística")
print("=" * 80)
response1 = requests.get(
    "https://api.bling.com.br/v3/pedidos/vendas?limite=2",
    headers=headers
)

if response1.status_code == 200:
    dados = response1.json()
    if 'data' in dados and len(dados['data']) > 0:
        print("✅ Chaves disponíveis:")
        print(list(dados['data'][0].keys()))
        print("\nPrimeiro pedido (preview):")
        print(json.dumps(dados['data'][0], indent=2, ensure_ascii=False)[:1000])

# Tentar 2: Acessar pedido direto com ID correto
print("\n\n" + "=" * 80)
print("TENTATIVA 2: Acessar pedido específico por ID")
print("=" * 80)
response2 = requests.get(
    "https://api.bling.com.br/v3/pedidos/vendas/25457174379",
    headers=headers
)

if response2.status_code == 200:
    pedido = response2.json()
    with open('pedido_detalhado.json', 'w', encoding='utf-8') as f:
        json.dump(pedido, f, indent=2, ensure_ascii=False)
    print("✅ Pedido encontrado!")
    print("Chaves:", list(pedido.keys()))
    print("\nConteúdo completo:")
    print(json.dumps(pedido, indent=2, ensure_ascii=False))
else:
    print(f"❌ Erro {response2.status_code}: {response2.text}")

# Tentar 3: Buscar endpoint de objetos/postagem
print("\n\n" + "=" * 80)
print("TENTATIVA 3: Endpoint de objetos de postagem")
print("=" * 80)
response3 = requests.get(
    "https://api.bling.com.br/v3/objetos",
    headers=headers
)
print(f"Status: {response3.status_code}")
if response3.status_code == 200:
    print("✅ Objetos encontrados:")
    print(json.dumps(response3.json(), indent=2, ensure_ascii=False)[:1000])
else:
    print(f"Resposta: {response3.text[:500]}")
