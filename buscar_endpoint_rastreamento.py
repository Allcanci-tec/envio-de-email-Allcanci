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

# O volume tem ID: 16015289930
volume_id = 16015289930

print("🔍 PROCURANDO DADOS DE RASTREAMENTO NO BLING\n")

# Tentativa 1: Endpoint /objetos/{id}
print("=" * 80)
print("TENTATIVA 1: /objetos/{volume_id}")
print("=" * 80)
response = requests.get(
    f"https://api.bling.com.br/v3/objetos/{volume_id}",
    headers=headers
)
print(f"Status: {response.status_code}")
print(response.text[:1000] if len(response.text) > 0 else "Sem resposta")

# Tentativa 2: Procurar por cotação de postagem
print("\n" + "=" * 80)
print("TENTATIVA 2: /cotacoes")
print("=" * 80)
response = requests.get(
    "https://api.bling.com.br/v3/cotacoes",
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(json.dumps(response.json(), indent=2, ensure_ascii=False)[:1500])
else:
    print(response.text[:500])

# Tentativa 3: Procurar por rastreamento
print("\n" + "=" * 80)
print("TENTATIVA 3: /rastreamento")
print("=" * 80)
response = requests.get(
    "https://api.bling.com.br/v3/rastreamento",
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(json.dumps(response.json(), indent=2, ensure_ascii=False)[:1500])
else:
    print(response.text[:500])

# Tentativa 4: Procurar em logisticas
print("\n" + "=" * 80)
print("TENTATIVA 4: /logisticas")
print("=" * 80)
response = requests.get(
    "https://api.bling.com.br/v3/logisticas",
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    dados = response.json()
    print(json.dumps(dados, indent=2, ensure_ascii=False)[:2000])
else:
    print(response.text[:500])

# Tentativa 5: Listar todos endpoints conhecidos
print("\n" + "=" * 80)
print("LISTANDO ENDPOINTS PRINCIPAIS DO BLING")
print("=" * 80)
endpoints = [
    "/contatos",
    "/pedidos/vendas", 
    "/notas-fiscais",
    "/produtos",
    "/clientes",
    "/fornecedores",
    "/contas",
    "/boletos",
    "/vendedores",
    "/depositos"
]

for ep in endpoints:
    r = requests.get(f"https://api.bling.com.br/v3{ep}?limite=1", headers=headers)
    status = "✅ OK" if r.status_code == 200 else f"❌ {r.status_code}"
    print(f"{status} {ep}")
