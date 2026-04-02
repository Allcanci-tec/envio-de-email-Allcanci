import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Carregar tokens
with open('tokens.json', 'r') as f:
    tokens = json.load(f)
    
ACCESS_TOKEN = tokens['access_token']

# Buscar pedidos vendas com logistica Correios
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
response = requests.get(
    "https://api.bling.com.br/v3/pedidos/vendas?logistica=151483&limite=5",
    headers=headers
)

if response.status_code == 200:
    dados = response.json()
    
    if 'data' in dados and len(dados['data']) > 0:
        pedido = dados['data'][0]  # Pega primeiro pedido
        
        # Salvar para análise
        with open('pedido_vendas_estrutura.json', 'w', encoding='utf-8') as f:
            json.dump(pedido, f, indent=2, ensure_ascii=False)
        
        print("✅ PRIMEIRO PEDIDO COM LOGÍSTICA CORREIOS:\n")
        print(json.dumps(pedido, indent=2, ensure_ascii=False))
        
        # Procurar por campos de rastreamento
        print("\n\n🔍 CHAVES DISPONÍVEIS NO PEDIDO:")
        print(list(pedido.keys()))
        
        if 'transporte' in pedido:
            print("\n📦 TRANSPORTE DISPONÍVEL:")
            print(json.dumps(pedido['transporte'], indent=2, ensure_ascii=False)[:2000])
            
        if 'objetos' in pedido:
            print("\n📭 OBJETOS:")
            print(json.dumps(pedido['objetos'], indent=2, ensure_ascii=False))
else:
    print(f"❌ Erro: {response.status_code}")
    print(response.text)
