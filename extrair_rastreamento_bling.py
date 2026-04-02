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

print("🚀 BUSCANDO DADOS DE RASTREAMENTO DO BLING\n")

# Buscar pedido com parâmetro especial para retornar rastreamento
response = requests.get(
    "https://api.bling.com.br/v3/pedidos/vendas/25457174379",
    headers=headers
)

if response.status_code == 200:
    pedido = response.json()
    
    # Salvar estrutura completa
    with open('pedido_com_rastreamento.json', 'w', encoding='utf-8') as f:
        json.dump(pedido, f, indent=2, ensure_ascii=False)
    
    print("✅ ESTRUTURA COMPLETA:")
    todos_dados = pedido.get('data', pedido)
    print(json.dumps(todos_dados, indent=2, ensure_ascii=False))
    
    # Procurar pelo rastreamento
    if 'rastreamento' in todos_dados:
        print("\n\n✅ CAMPO RASTREAMENTO ENCONTRADO!")
        print(json.dumps(todos_dados['rastreamento'], indent=2, ensure_ascii=False))
    else:
        print("\n\n🔍 Campo 'rastreamento' não encontrado neste pedido")
        print("Chaves disponíveis:", list(todos_dados.keys()))
else:
    print(f"❌ Erro: {response.status_code}")
