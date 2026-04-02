#!/usr/bin/env python3
"""
Script para obter situacao completa da etiqueta (Bling + Correios)
"""

import json
from bling_auth import bling_get
from datetime import datetime
import requests

def obter_situacao_etiqueta(etiqueta):
    """Obtém situação completa da etiqueta combinando Bling + Correios"""
    
    print(f'\n📦 Obtendo situação da etiqueta: {etiqueta}\n')
    
    resultado = {
        "etiqueta": etiqueta,
        "data_consulta": datetime.now().isoformat(),
        "informacoes_bling": None,
        "rastreamento_correios": None
    }
    
    # 1. Tenta obter dados do Bling
    print('  1️⃣ Consultando Bling...')
    try:
        # Busca nos pedidos
        resp_pedidos = bling_get('/pedidos/vendas', params={'logistica': 151483, 'limit': 100})
        
        for pedido in resp_pedidos.get('data', []):
            volumes = pedido.get('transporte', {}).get('volumes', [])
            
            for volume in volumes:
                if volume.get('codigoRastreamento') == etiqueta:
                    resultado['informacoes_bling'] = {
                        "pedido_id": pedido.get('id'),
                        "numero_pedido": pedido.get('numero'),
                        "cliente": pedido.get('contato', {}).get('nome'),
                        "volume_id": volume.get('id'),
                        "servico": volume.get('servico'),
                        "codigo_rastreamento": volume.get('codigoRastreamento'),
                        "status_pedido": pedido.get('situacao', {}).get('valor')
                    }
                    print('     ✅ Encontrado no Bling')
                    break
        
        if not resultado['informacoes_bling']:
            print('     ⏭️ Não encontrado parametrizado')
            
    except Exception as e:
        print(f'     ❌ Erro: {str(e)[:50]}')
    
    # 2. Tenta rastreamento via Correios
    print('  2️⃣ Consultando Correios...')
    try:
        url = 'https://www.correios.com.br/rastreamento'
        response = requests.get(url, timeout=10, params={'numero': etiqueta})
        
        if response.status_code == 200:
            resultado['rastreamento_correios'] = {
                "url_rastreamento": f"https://www.correios.com.br/rastreamento?numero={etiqueta}",
                "status": "disponivel_para_consulta",
                "metodo": "web_url"
            }
            print('     ✅ Disponível na web dos Correios')
        else:
            resultado['rastreamento_correios'] = {
                "status": "indisponivel",
                "motivo": f"HTTP {response.status_code}"
            }
            print(f'     ⚠️ HTTP {response.status_code}')
    except Exception as e:
        resultado['rastreamento_correios'] = {
            "status": "erro",
            "erro": str(e)[:100]
        }
        print(f'     ❌ Erro: {str(e)[:50]}')
    
    return resultado


if __name__ == "__main__":
    etiqueta = "AD287897978BR"
    
    dados = obter_situacao_etiqueta(etiqueta)
    
    print("\n" + "="*70)
    print("📋 SITUAÇÃO DA ETIQUETA")
    print("="*70)
    print(json.dumps(dados, indent=2, ensure_ascii=False))
    
    # Exporta
    with open('situacao_etiqueta.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Salvo em: situacao_etiqueta.json")
