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

print("🔍 PROCURANDO CAMPO RASTREAMENTO EM DIFERENTES ENDPOINTS\n")

volume_id = 16015289930
codigo_rastreamento = "AD292045598BR"
pedido_id = 25457174379

endpoints_teste = [
    ("Volumes direto", f"https://api.bling.com.br/v3/objetos/{volume_id}"),
    ("Rastreamento endpoint", "https://api.bling.com.br/v3/rastreamento"),
    ("Rastreamento por código", f"https://api.bling.com.br/v3/rastreamento?codigo={codigo_rastreamento}"),
    ("Pedido com rastreamento", f"https://api.bling.com.br/v3/pedidos/vendas/{pedido_id}/rastreamento"),
    ("Cotações", "https://api.bling.com.br/v3/cotacoes"),
]

for nome, endpoint in endpoints_teste:
    print(f"\n{'='*70}")
    print(f"🧪 {nome}")
    print(f"   URL: {endpoint}")
    print(f"{'='*70}")
    
    try:
        response = requests.get(endpoint, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            dados = response.json()
            print("✅ SUCESSO - Dados:")
            print(json.dumps(dados, indent=2, ensure_ascii=False)[:800])
            
            # Salvar resultado positivo
            nome_arquivo = nome.lower().replace(" ", "_") + ".json"
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Salvo em: {nome_arquivo}")
        else:
            print(f"❌ Erro: {response.status_code}")
            erro = response.json() if response.text else response.reason
            print(json.dumps(erro, indent=2, ensure_ascii=False) if isinstance(erro, dict) else str(erro)[:300])
            
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")

print("\n\n" + "="*70)
print("📚 PROCURANDO NA DOCUMENTAÇÃO DO BLING")
print("="*70)
print("Você pode ver na API do Bling qual endpoint retorna os dados de rastreamento.")
print("A estrutura que você mostrou tem os campos:")
print("  - codigo: etiqueta")
print("  - descricao: status (Criado, Saiu para entrega, etc)")
print("  - situacao: número do status")
print("  - ultimaAlteracao: timestamp da última sincronização")
print("\nEssa é exatamente a estrutura que precisamos usar! 🎯")
