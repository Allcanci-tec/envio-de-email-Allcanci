import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Carregar tokens
with open('tokens.json', 'r') as f:
    tokens = json.load(f)
    
ACCESS_TOKEN = tokens['access_token']

# Buscar um pedido completo com TODAS as informações
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
response = requests.get(
    "https://api.bling.com.br/v3/pedidos/vendas/2363",
    headers=headers
)

if response.status_code == 200:
    pedido = response.json()
    # Salvar resposta completa para análise
    with open('pedido_completo_2363.json', 'w', encoding='utf-8') as f:
        json.dump(pedido, f, indent=2, ensure_ascii=False)
    
    # Exibir estrutura para encontrar dados de rastreamento
    print("✅ ESTRUTURA COMPLETA DO PEDIDO 2363:\n")
    print(json.dumps(pedido, indent=2, ensure_ascii=False)[:3000])
    print("\n... (arquivo salvo em pedido_completo_2363.json)")
    
    # Procurar por campos de rastreamento
    print("\n\n🔍 PROCURANDO DADOS DE RASTREAMENTO:\n")
    if 'transporte' in pedido:
        print("📦 TRANSPORTE:", json.dumps(pedido['transporte'], indent=2, ensure_ascii=False)[:1500])
    if 'objetos' in pedido:
        print("\n📭 OBJETOS:", json.dumps(pedido['objetos'], indent=2, ensure_ascii=False))
    if 'rastreamento' in pedido:
        print("\n🚚 RASTREAMENTO:", json.dumps(pedido['rastreamento'], indent=2, ensure_ascii=False))
else:
    print(f"❌ Erro: {response.status_code}")
    print(response.text)
